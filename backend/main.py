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

from backend.database import engine, Base, get_db
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

class ExpenseAdmin(ModelView, model=models.Expense):
    name = "Despesa"
    name_plural = "Despesas"
    icon = "fa-solid fa-money-bill-wave"
    column_list = [models.Expense.id, models.Expense.amount, models.Expense.category, models.Expense.date]
    column_searchable_list = [models.Expense.category, models.Expense.description]
    column_sortable_list = [models.Expense.date, models.Expense.amount]
    form_columns = [models.Expense.workspace, models.Expense.amount, models.Expense.category, models.Expense.description]

admin = Admin(app, engine, base_url="/api/admin", authentication_backend=authentication_backend)
admin.add_view(UserAdmin)
admin.add_view(WorkspaceAdmin)
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
        result.append({
            "id": exp.id,
            "desc": exp.description or "Sem descrição",
            "category": exp.category,
            "amount": exp.amount,
            "date": exp.date.strftime("%d/%m/%Y") if exp.date else "",
            "user": "Você" # Placeholder for MVP since auth is skipped
        })
    return result

class ExpenseExtraction(BaseModel):
    is_expense: bool = Field(description="True if the message is reporting an expense")
    amount: float = Field(default=0.0, description="The extracted monetary amount")
    category: str = Field(default="", description="The category of the expense")
    description: str = Field(default="", description="A short description of the expense")
    is_question: bool = Field(default=False, description="True if asking a question")
    answer: str = Field(default="", description="The answer to the user's question")

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
        
        system_prompt = (
            "You are a financial assistant for a Brazilian user. "
            "Extract the expense amount, category, and description from the user's message. "
            "If they are asking a question, answer it friendly in Portuguese. "
            "Always return a strict JSON matching the schema."
        )

        response = litellm.completion(
            model=model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": text}
            ],
            response_format={"type": "json_object"} # Instruct to return JSON
        )
        
        content = response.choices[0].message.content
        parsed = json.loads(content)
        
        ext = ExpenseExtraction(**parsed)

        reply_text = ""
        if ext.is_expense and ext.amount > 0:
            ws_member = db.query(models.WorkspaceMember).filter(models.WorkspaceMember.user_id == user.id).first()
            if ws_member:
                expense = models.Expense(
                    workspace_id=ws_member.workspace_id,
                    amount=ext.amount,
                    category=ext.category,
                    description=ext.description
                )
                db.add(expense)
                db.commit()
                reply_text = f"✅ Gasto de R$ {ext.amount:.2f} em {ext.category} registrado com sucesso!"
        elif ext.is_question and ext.answer:
            reply_text = ext.answer
        else:
            reply_text = "Desculpe, não entendi. Você pode informar um gasto (ex: 'gastei 50 no ifood')?"

        # Send reply back via Waha
        waha_url = os.getenv("WAHA_API_URL", "http://localhost:3000")
        waha_session = os.getenv("WAHA_SESSION", "default")
        
        requests.post(f"{waha_url}/api/sendText", json={
            "session": waha_session,
            "chatId": message_data.get("from"),
            "text": reply_text
        })
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
    background_tasks.add_task(process_waha_message, payload, db)
    return {"status": "ok"}
