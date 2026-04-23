from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    phone_number = Column(String, unique=True, index=True)
    name = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    workspaces = relationship("WorkspaceMember", back_populates="user")

    def __str__(self):
        return f"{self.name} ({self.phone_number})"

class Workspace(Base):
    __tablename__ = "workspaces"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    members = relationship("WorkspaceMember", back_populates="workspace")
    expenses = relationship("Expense", back_populates="workspace")

    def __str__(self):
        return self.name or f"Workspace #{self.id}"

class WorkspaceMember(Base):
    __tablename__ = "workspace_members"
    
    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    workspace_id = Column(Integer, ForeignKey("workspaces.id"), primary_key=True)
    role = Column(String, default="owner") # "owner" or "partner"
    
    user = relationship("User", back_populates="workspaces")
    workspace = relationship("Workspace", back_populates="members")

class Expense(Base):
    __tablename__ = "expenses"
    
    id = Column(Integer, primary_key=True, index=True)
    workspace_id = Column(Integer, ForeignKey("workspaces.id"))
    amount = Column(Float, nullable=False)
    category = Column(String, index=True)
    description = Column(String, nullable=True)
    date = Column(DateTime(timezone=True), default=func.now())
    
    workspace = relationship("Workspace", back_populates="expenses")
