import logging
from pydantic import BaseModel, EmailStr
from typing import Optional, List

class Role(BaseModel):
    id: str
    name: str

class NotificationChannels(BaseModel):
    id: str
    name: str

class UserCreate(BaseModel):
    name: str
    password: str
    email: EmailStr
    username: Optional[str] = None
    notification_channel: str = "Email"
    roles: List[str] = ["Customer"]

class User(BaseModel):
    id: Optional[str] = None
    name: str
    username: Optional[str] = None
    hashed_password: str
    email: EmailStr
    balance: float = 500.0
    notification_channel: str = "Email"
    roles: List[str] = ["Customer"]

class InvestmentFund(BaseModel):
    id: str
    name: str
    minimumFee: float
    category: str

class Transaction(BaseModel):
    id: str
    customer_id: str
    fund_id: str
    type: str  # Open for Subscription/Close for Cancellation
    amount: float
    timestamp: str