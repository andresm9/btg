from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from app.config import logging
from app.models import User, UserCreate, InvestmentFund, InvestmentFundCreate, Transaction, NotificationChannels
from app.database import db
from app.auth import *
from typing import List

router = APIRouter(prefix="/funds")
logger = logging.getLogger(__name__)

@router.post('/subscribe')
async def subscribe_fund(fund_id: str, user: User = Depends(get_current_user)):

    fund = await db.investment_funds.find_one({"id": fund_id})

    if not fund:
        raise HTTPException(status_code=404, detail="Fund not found")
    
    if user.balance < fund['minimumFee']:
        raise HTTPException(status_code=400, detail=f"Not enough money to subscribe to the investment fund {fund['name']}")
    
    await db.transactions.insert_one({
        "customer_id": user.id,
        "fund_id": fund_id,
        "type": "Open",
        "amount": fund['minimumFee'],
        "timestamp": "now" # Replace with actual timestamp
    })
    await db.users.update_one({"id": user.id}, {"$inc": {"balance": -fund['minimumFee']}})
    # Notification logic placeholder
    return {"message": f"Subscribed to {fund['name']}"}

@router.post('/cancel')
async def cancel_fund(fund_id: str, user: User = Depends(get_current_user)):
    fund = await db.investment_funds.find_one({"id": fund_id})
    if not fund:
        raise HTTPException(status_code=404, detail="Fund not found")
    await db.transactions.insert_one({
        "customer_id": user.id,
        "fund_id": fund_id,
        "type": "Close",
        "amount": fund['minimumFee'],
        "timestamp": "now" # Replace with actual timestamp
    })
    await db.users.update_one({"id": user.id}, {"$inc": {"balance": fund['minimumFee']}})
    # Notification logic placeholder
    return {"message": f"Cancelled subscription to {fund['name']}"}

@router.get('/transactions')
async def get_transactions(user: User = Depends(get_current_user)) -> List[Transaction]:
    txs = []
    async for tx in db.transactions.find({"customer_id": user.id}):
        txs.append(tx)
    return txs

# Admin-only endpoints
def is_admin(user: User):
    return "Admin" in user.roles


@router.post('/create', status_code=status.HTTP_201_CREATED)
async def create_fund(fund:InvestmentFundCreate, user: User = Depends(get_current_user)):
    
    if not is_admin(user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin privileges required")

    fund_dict = fund.model_dump()
    response = await db.InvestmentFund.insert_one(fund_dict)
    print(response.inserted_id)
    return {"message": "Fund created successfully"}


@router.get('/list', response_model=List[InvestmentFund])
async def list_funds(user: User = Depends(get_current_user)):

    if not is_admin(user):
        raise HTTPException(status_code=403, detail="Admin privileges required")

    funds = await db.InvestmentFund.find().to_list()
    return funds