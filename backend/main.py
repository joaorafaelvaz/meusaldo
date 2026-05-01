from anyio import to_thread
from fastapi import FastAPI, Depends, Request, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import json
import os
import requests
import litellm
from pydantic import BaseModel, Field
from sqladmin import Admin, ModelView
from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request

from typing import Optional
from datetime import datetime, timedelta
import calendar

from backend.database import engine, Base, get_db

def add_months(d: datetime, months: int) -> datetime:
    month = d.month - 1 + months
    year = d.year + month // 12
    month = month % 12 + 1
    return d.replace(year=year, month=month, day=1)

def calculate_invoice_date(purchase_date: datetime, closing_day: int, due_day: int) -> datetime:
    cycle_date = purchase_date
    if purchase_date.day >= closing_day:
        cycle_date = add_months(cycle_date, 1)
        
    if due_day < closing_day:
        due_date_base = add_months(cycle_date, 1)
    else:
        due_date_base = cycle_date
        
    max_day = calendar.monthrange(due_date_base.year, due_date_base.month)[1]
    actual_due_day = min(due_day, max_day)
    
    return datetime(due_date_base.year, due_date_base.month, actual_due_day, tzinfo=purchase_date.tzinfo)

from backend import models

# Create tables for MVP (in production use Alembic)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Meusaldo API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Admin Authentication
class AdminAuth(AuthenticationBackend):
    async def login(self, request: Request) -> bool:
        form = await request.form()
        username, password = form["username"], form["password"]
        
        admin_user = os.getenv("ADMIN_USERNAME", "admin")
        admin_pass = os.getenv("ADMIN_PASSWORD", "senha123")
        
        if username == admin_user and password == admin_pass:
            request.session.update({"token": "admin_session"})
            return True
        return False

    async def logout(self, request: Request) -> bool:
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        token = request.session.get("token")
        return token == "admin_session"

authentication_backend = AdminAuth(secret_key=os.getenv("SECRET_KEY", "meusaldo-super-secret-key-123"))

# Admin Panel Setup
class UserAdmin(ModelView, model=models.User):
    name = "Usuário"
    name_plural = "Usuários"
    icon = "fa-solid fa-user"
    column_list = [models.User.id, models.User.name, models.User.phone_number]
    column_searchable_list = [models.User.name, models.User.phone_number]

class WorkspaceAdmin(ModelView, model=models.Workspace):
    name = "Workspace"
    name_plural = "Workspaces"
    icon = "fa-solid fa-building"
    column_list = [models.Workspace.id, models.Workspace.name]
    column_searchable_list = [models.Workspace.name]

class CreditCardAdmin(ModelView, model=models.CreditCard):
    name = "Cartão de Crédito"
    name_plural = "Cartões de Crédito"
    icon = "fa-solid fa-credit-card"
    column_list = [models.CreditCard.id, models.CreditCard.name, models.CreditCard.closing_day, models.CreditCard.due_day]
    form_columns = [models.CreditCard.workspace, models.CreditCard.name, models.CreditCard.closing_day, models.CreditCard.due_day]

class ExpenseAdmin(ModelView, model=models.Expense):
    name = "Despesa"
    name_plural = "Despesas"
    icon = "fa-solid fa-money-bill-wave"
    column_list = [models.Expense.id, models.Expense.amount, models.Expense.category, models.Expense.date, models.Expense.invoice_date]
    column_searchable_list = [models.Expense.category, models.Expense.description]
    column_sortable_list = [models.Expense.date, models.Expense.amount, models.Expense.invoice_date]
    form_columns = [models.Expense.workspace, models.Expense.credit_card, models.Expense.amount, models.Expense.category, models.Expense.description, models.Expense.date, models.Expense.invoice_date]

admin = Admin(app, engine, base_url="/api/admin", authentication_backend=authentication_backend)
admin.add_view(UserAdmin)
admin.add_view(WorkspaceAdmin)
admin.add_view(CreditCardAdmin)
admin.add_view(ExpenseAdmin)

@app.get("/")
def read_root():
    return {"message": "Meusaldo API is running"}

@app.get("/api/expenses")
def get_expenses(db: Session = Depends(get_db)):
    # Fetch latest expenses for the MVP dashboard
    expenses = db.query(models.Expense).order_by(models.Expense.date.desc()).limit(20).all()
    result = []
    for exp in expenses:
        user_name = "Você"
        if exp.user_id:
            member = db.query(models.WorkspaceMember).filter_by(user_id=exp.user_id, workspace_id=exp.workspace_id).first()
            if member and member.role == "partner":
                user_name = "Parceiro"
            elif member and member.role == "owner":
                user_name = "Você"
            else:
                user_name = exp.user.name if exp.user else "Você"
        
        result.append({
            "id": exp.id,
            "desc": exp.description or "Sem descrição",
            "category": exp.category,
            "amount": exp.amount,
            "date": exp.date.strftime("%d/%m/%Y") if exp.date else "",
            "user": user_name
        })
    return result

@app.get("/api/dashboard")
def get_dashboard_data(db: Session = Depends(get_db)):
    now = datetime.now()
    expenses = db.query(models.Expense).all()
    
    category_totals = {}
    future_totals = {}
    
    for exp in expenses:
        eff_date = exp.invoice_date if exp.invoice_date else exp.date
        if not eff_date:
            continue
            
        if eff_date.year == now.year and eff_date.month == now.month:
            cat = exp.category or "Outros"
            category_totals[cat] = category_totals.get(cat, 0) + exp.amount
            
        if eff_date.year > now.year or (eff_date.year == now.year and eff_date.month > now.month):
            month_str = eff_date.strftime("%m/%Y")
            future_totals[month_str] = future_totals.get(month_str, 0) + exp.amount

    category_data = [{"name": k, "value": v} for k, v in category_totals.items()]
    category_data.sort(key=lambda x: x["value"], reverse=True)
    
    future_data = [{"month": k, "amount": v} for k, v in future_totals.items()]
    future_data.sort(key=lambda x: datetime.strptime(x["month"], "%m/%Y"))
    
    return {
        "categories": category_data,
        "future": future_data
    }

class ExpenseData(BaseModel):
    amount: Optional[float] = None
    category: Optional[str] = None
    description: Optional[str] = None
    card_name: Optional[str] = None
    cardholder: Optional[str] = None
    installments: int = Field(default=1)

class BillData(BaseModel):
    due_date: Optional[str] = None
    payee: Optional[str] = None
    amount: Optional[float] = None

class ExpenseExtraction(BaseModel):
    intent: str = Field(default="chat")
    reply: str = Field(default="")
    expense_data: Optional[ExpenseData] = None
    bill_data: Optional[BillData] = None

def process_waha_message(payload: dict, db: Session):
    """
    Background task to process the Waha message using LiteLLM.
    Extracts expense data and writes to DB, then sends confirmation via Waha API.
    """
    try:
        # Extract text and phone from Waha webhook payload
        # Waha payload structure varies slightly, assuming typical structure:
        message_data = payload.get("payload", {})
        text = message_data.get("body", "")
        phone = message_data.get("from", "").split("@")[0]

        if not text or message_data.get("fromMe"):
            return

        print(f"Processing message from {phone}: {text}")

        # Ensure user exists (simplified for MVP)
        user = db.query(models.User).filter(models.User.phone_number == phone).first()
        if not user:
            user = models.User(phone_number=phone, name="User")
            db.add(user)
            db.commit()
            db.refresh(user)
            # Create a default workspace
            ws = models.Workspace(name="My Workspace")
            db.add(ws)
            db.commit()
            db.refresh(ws)
            db.add(models.WorkspaceMember(user_id=user.id, workspace_id=ws.id, role="owner"))
            db.commit()

        # Parse with LiteLLM
        model_name = os.getenv("LLM_MODEL", "gpt-3.5-turbo") # Default to OpenAI for better JSON parsing out of the box
        api_base = os.getenv("LLM_API_BASE") # Useful for Ollama or local models
        
 #       system_prompt = (
 #           "You are a financial assistant for a Brazilian user. "
 #           "Extract the expense amount, category, and description from the user's message. "
 #           "If they are asking a question, answer it friendly, funny and sarcastic in Brazilian Portuguese. "
 #           "IMPORTANT: Always return a strict JSON matching this exact schema: "
 #           "{\"is_expense\": true, \"amount\": 50.0, \"category\": \"Food\", \"description\": \"Lunch\"}. "
 #           "Do NOT invent new keys like 'expense_amount', strictly use 'amount'."
 #       )

        system_prompt = """
        You are a highly efficient personal financial assistant. You have a sarcastic, humorous, and friendly personality. While your instructions are in English, you MUST ALWAYS generate the spoken response for the user in Brazilian Portuguese (PT-BR).

            YOUR MISSIONS:
            1. Record Expenses: Extract the amount, category, and description.
            2. Set Reminders: Identify bills to pay, payees, and due dates.
            3. Answer Queries: Understand when the user is asking about their financial history or spending habits.
            4. Clarify: If the user logs an expense or bill but forgets crucial data (like the amount or the description), you MUST ask them for the missing information before confirming.

            OUTPUT GUIDELINES:
            You do not have direct access to a database. Your job is to parse the user's input and structure their intent.
            You MUST ALWAYS and EXCLUSIVELY return a valid JSON object matching this exact schema. Do not output any markdown formatting, conversational text, or explanations outside the JSON block.

            {
            "intent": "expense | query | reminder | clarification | chat",
            "reply": "Your spoken response in PT-BR with your sarcastic and friendly tone. Use this field to interact, confirm actions, or ask for missing information.",
            "expense_data": {
                "amount": 0.0,
                "category": "String in Portuguese (e.g., Alimentação, Transporte, Lazer) or null",
                "description": "String or null",
                "card_name": "String or null",
                "cardholder": "String or null",
                "installments": "Integer (default 1, e.g., 4 if 'em 4x')"
            },
            "bill_data": {
                "due_date": "DD/MM/YYYY or null",
                "payee": "String (name of the bill/recipient) or null",
                "amount": 0.0
            }
            }

            DATA POPULATION RULES:
            - "intent":
            - Use "expense" ONLY if the user provides a complete expense record (amount + description).
            - Use "reminder" if the user mentions a bill with a future due date.
            - Use "query" if the user is asking a question about their spending (e.g., "How much did I spend this week?").
            - Use "clarification" if the user attempts to log an expense or bill but misses the amount or description.
            - Use "chat" for general conversation unrelated to specific financial actions.
            - The "amount" fields must be strictly numeric (float). NEVER invent new keys like 'expense_amount', strictly use 'amount'. If no amount is given, use null.
            - Time reference: Today is {CURRENT_DATE}. Translate relative terms like "tomorrow" or "next Friday" into the explicit DD/MM/YYYY format for "due_date".
            
            - BANK NOTIFICATIONS (PUSH/SMS): 
              If the user pastes a bank notification like "Compra aprovada no LATAM PASS...":
              - "intent": MUST be "expense".
              - "amount": Extract numeric value (e.g., "RS 369,00" -> 369.0).
              - "description": The establishment name (e.g., "CONTABILIZEI TECNOLOGIA L" or "MERCADOLIVRE*MERCADOLIVRE").
              - "card_name": Extract card name and final digits (e.g., "LATAM PASS VS INFINI" or "LATAM PASS VS INFINI final 6631").
              - "cardholder": If names like "GIORGIA", "LUCIA", or "RENATO" appear, use them. Otherwise, default to "João".
              - "installments": Extract integer if the purchase was split (e.g., "em 4x", "parcelado em 3"). Default to 1.
              - "reply": Create a sarcastic and funny confirmation including the cardholder name, available limit, and number of installments.
        """

        prompt_with_date = system_prompt.replace("{CURRENT_DATE}", datetime.now().strftime("%d/%m/%Y"))

        response = litellm.completion(
            model=model_name,
            api_base=api_base,
            messages=[
                {"role": "system", "content": prompt_with_date},
                {"role": "user", "content": text}
            ],
            response_format={"type": "json_object"} # Instruct to return JSON
        )
        
        content = response.choices[0].message.content
        print(f"Raw LLM response: {content}") # Debugging line
        
        try:
            parsed = json.loads(content)
        except json.JSONDecodeError:
            # Sometimes models return markdown blocks like ```json ... ```
            clean_content = content.replace("```json", "").replace("```", "").strip()
            parsed = json.loads(clean_content)
        
        ext = ExpenseExtraction(**parsed)

        reply_text = ext.reply or "Desculpe, ocorreu um erro interno e não consegui processar."
        ws_member = db.query(models.WorkspaceMember).filter(models.WorkspaceMember.user_id == user.id).first()
        
        if ext.intent == "expense" and ext.expense_data and ext.expense_data.amount is not None:
            if ws_member:
                desc = ext.expense_data.description or "Sem descrição"
                if ext.expense_data.cardholder:
                    desc += f" (Cartão de: {ext.expense_data.cardholder})"

                base_card_id = None
                base_invoice_date = None
                purchase_date = datetime.now()
                
                if ext.expense_data.card_name:
                    card_token = ext.expense_data.card_name.split()[0].lower()
                    cards = db.query(models.CreditCard).filter(models.CreditCard.workspace_id == ws_member.workspace_id).all()
                    for c in cards:
                        if c.name.lower() in ext.expense_data.card_name.lower() or card_token in c.name.lower():
                            base_card_id = c.id
                            base_invoice_date = calculate_invoice_date(purchase_date, c.closing_day, c.due_day)
                            break

                installments = ext.expense_data.installments
                if installments < 1:
                    installments = 1

                total_amount = ext.expense_data.amount
                base_installment_amount = round(total_amount / installments, 2)
                remainder = round(total_amount - (base_installment_amount * installments), 2)

                for i in range(1, installments + 1):
                    current_desc = desc
                    if installments > 1:
                        current_desc += f" (Parcela {i}/{installments})"
                    
                    current_amount = base_installment_amount
                    if i == installments:
                        current_amount = round(current_amount + remainder, 2)

                    current_invoice_date = None
                    if base_invoice_date:
                        current_invoice_date = add_months(base_invoice_date, i - 1)
                    
                    current_date = purchase_date
                    if not base_card_id and i > 1:
                        current_date = add_months(purchase_date, i - 1)

                    expense = models.Expense(
                        workspace_id=ws_member.workspace_id,
                        user_id=user.id,
                        amount=current_amount,
                        category=ext.expense_data.category or "Geral",
                        description=current_desc,
                        credit_card_id=base_card_id,
                        invoice_date=current_invoice_date,
                        date=current_date
                    )
                    db.add(expense)
                
                db.commit()

        elif ext.intent == "query":
            if ws_member:
                thirty_days_ago = datetime.now() - timedelta(days=30)
                recent_expenses = db.query(models.Expense).filter(
                    models.Expense.workspace_id == ws_member.workspace_id,
                    models.Expense.date >= thirty_days_ago
                ).all()
                
                context_str = "Despesas recentes (últimos 30 dias):\n"
                if not recent_expenses:
                    context_str += "Nenhuma despesa registrada nos últimos 30 dias.\n"
                else:
                    for exp in recent_expenses:
                        cat = exp.category or "Geral"
                        desc = exp.description or "Sem descrição"
                        date_str = exp.date.strftime("%d/%m/%Y") if exp.date else "Desconhecido"
                        context_str += f"- {date_str} | {cat} | R$ {exp.amount:.2f} | {desc}\n"
                
                query_prompt = f"""
                You are a highly efficient personal financial assistant with a sarcastic, humorous, and friendly personality.
                The user asked a question about their finances: "{text}"
                
                Here is their actual spending data for the last 30 days:
                {context_str}
                
                Answer the user's question accurately based ONLY on the data above. Do not invent expenses.
                If they ask about "this week", calculate it based on the dates provided (today is {datetime.now().strftime("%d/%m/%Y")}).
                Reply in Brazilian Portuguese (PT-BR). Do NOT output JSON. Output ONLY the plain text response to send via WhatsApp.
                """
                
                query_response = litellm.completion(
                    model=model_name,
                    api_base=api_base,
                    messages=[
                        {"role": "system", "content": query_prompt}
                    ]
                )
                
                reply_text = query_response.choices[0].message.content.strip()

        waha_url = os.getenv("WAHA_API_URL", "http://localhost:3000")
        waha_session = os.getenv("WAHA_SESSION", "default")
        waha_api_key = os.getenv("WAHA_API_KEY")
        
        headers = {
            "Content-Type": "application/json"
        }
        if waha_api_key:
            # Most Waha setups use X-Api-Key or Authorization header for security
            headers["X-Api-Key"] = waha_api_key
            headers["Authorization"] = f"Bearer {waha_api_key}" # Adding both just in case it depends on the proxy

        requests.post(
            f"{waha_url}/api/sendText", 
            json={
                "session": waha_session,
                "chatId": message_data.get("from"),
                "text": reply_text
            },
            headers=headers
        )
        print(f"Reply to {phone}: {reply_text}")

    except Exception as e:
        print(f"Error processing message: {e}")


@app.post("/api/webhooks/waha")
async def waha_webhook(request: Request, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """
    Endpoint to receive Waha WhatsApp webhooks.
    Must return 200 OK immediately to acknowledge receipt.
    """
    payload = await request.json()
    print("--- INCOMING WEBHOOK RECEIVED ---")
    print(json.dumps(payload, indent=2))
    background_tasks.add_task(process_waha_message, payload, db)
    return {"status": "ok"}
