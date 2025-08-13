from datetime import datetime
from pydantic import BaseModel, BeforeValidator, ConfigDict, EmailStr, Field
from typing import Annotated, Any, Optional, List
from pydantic_core import core_schema

PyObjectId = Annotated[str, BeforeValidator(str)]

class Role(BaseModel):
    id: PyObjectId = Field(alias="_id", default=None)
    name: str

class NotificationChannels(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    name: str

class UserCreate(BaseModel):
    name: str
    password: str
    email: EmailStr
    username: Optional[str] = None
    balance: float = 500.0
    notification_channel: str = "Email"
    roles: List[str] = ["Customer"]

class User(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    name: str
    username: Optional[str] = None
    hashed_password: str
    email: EmailStr
    balance: float = 500.0
    notification_channel: str = "Email"
    roles: List[str] = ["Customer"]
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True
    )

class InvestmentFund(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    name: str
    minimumFee: float
    category: str
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_schema_extra={
            "examples": [
                {
                    "name": "Sample Fund",
                    "minimumFee": 1000,
                    "category": "FIC"
                }
            ]
        }
    )

class UserInvestmentFund(BaseModel):
    user_id: str
    fund_id: str
    subscription_date: datetime

class InvestmentFundCreate(BaseModel):
    name: str
    minimumFee: float
    category: str
    

class Transaction(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    customer_id: str
    fund_id: str
    type: str  # Open for Subscription/Close for Cancellation
    amount: float
    timestamp: datetime

class TransactionDetails(BaseModel):

    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    customerId: str
    customerName: str
    amount: float
    type: str
    fundName: str
    fundCategory: str
    timestamp: datetime

class FundResponse(BaseModel):
    
    message: str
    fund_id: str
    current_balance: float