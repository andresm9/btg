from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from app.config import logging
from app.models import User, UserCreate, InvestmentFund, Transaction, NotificationChannels
from app.database import db
from app.auth import *
from typing import List

router = APIRouter()

logger = logging.getLogger(__name__)

@router.post('/funds/subscribe')
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

@router.post('/funds/cancel')
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

@router.post('/funds/create')
async def create_fund(name: str, minimumFee: float, category: str, user: User = Depends(get_current_user)):
    if not is_admin(user):
        raise HTTPException(status_code=403, detail="Admin privileges required")
    fund = {
        "name": name,
        "minimumFee": minimumFee,
        "category": category
    }
    await db.investment_funds.insert_one(fund)
    return {"message": "Fund created successfully"}

@router.delete('/funds/delete')
async def delete_fund(fund_id: str, user: User = Depends(get_current_user)):
    if not is_admin(user):
        raise HTTPException(status_code=403, detail="Admin privileges required")
    await db.investment_funds.delete_one({"id": fund_id})
    return {"message": "Fund deleted successfully"}
