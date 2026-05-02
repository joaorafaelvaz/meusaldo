from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from backend.database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    phone_number = Column(String, unique=True, index=True)
    name = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    workspaces = relationship("WorkspaceMember", back_populates="user")
    expenses = relationship("Expense", back_populates="user")

    def __str__(self):
        return f"{self.name} ({self.phone_number})"

class Workspace(Base):
    __tablename__ = "workspaces"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    personality = Column(String, default="Sarcástico e Engraçado")
    
    members = relationship("WorkspaceMember", back_populates="workspace")
    expenses = relationship("Expense", back_populates="workspace")
    credit_cards = relationship("CreditCard", back_populates="workspace")
    weekly_goals = relationship("WeeklyGoal", back_populates="workspace")

    def __str__(self):
        return self.name or f"Workspace #{self.id}"

class WorkspaceMember(Base):
    __tablename__ = "workspace_members"
    
    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    workspace_id = Column(Integer, ForeignKey("workspaces.id"), primary_key=True)
    role = Column(String, default="owner") # "owner" or "partner"
    
    user = relationship("User", back_populates="workspaces")
    workspace = relationship("Workspace", back_populates="members")

class WeeklyGoal(Base):
    __tablename__ = "weekly_goals"
    
    id = Column(Integer, primary_key=True, index=True)
    workspace_id = Column(Integer, ForeignKey("workspaces.id"))
    category = Column(String, index=True)
    amount = Column(Float, nullable=False)
    
    workspace = relationship("Workspace", back_populates="weekly_goals")

class CreditCard(Base):
    __tablename__ = "credit_cards"
    
    id = Column(Integer, primary_key=True, index=True)
    workspace_id = Column(Integer, ForeignKey("workspaces.id"))
    name = Column(String, index=True)
    closing_day = Column(Integer, nullable=False)
    due_day = Column(Integer, nullable=False)
    
    workspace = relationship("Workspace", back_populates="credit_cards")
    expenses = relationship("Expense", back_populates="credit_card")
    
    def __str__(self):
        return f"{self.name} (Fechamento: {self.closing_day})"

class Expense(Base):
    __tablename__ = "expenses"
    
    id = Column(Integer, primary_key=True, index=True)
    workspace_id = Column(Integer, ForeignKey("workspaces.id"))
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    amount = Column(Float, nullable=False)
    category = Column(String, index=True)
    description = Column(String, nullable=True)
    date = Column(DateTime(timezone=True), default=datetime.now)
    
    credit_card_id = Column(Integer, ForeignKey("credit_cards.id"), nullable=True)
    invoice_date = Column(DateTime(timezone=True), nullable=True)
    
    workspace = relationship("Workspace", back_populates="expenses")
    user = relationship("User", back_populates="expenses")
    credit_card = relationship("CreditCard", back_populates="expenses")
