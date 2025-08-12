from bson import ObjectId
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from app.config import logging
from app.models import TransactionDetails, User, InvestmentFund, InvestmentFundCreate, Transaction, NotificationChannels
from app.database import db
from app.auth import *
from typing import List

router = APIRouter(prefix="/funds")
logger = logging.getLogger(__name__)

@router.post('/subscribe/{fund_id}', status_code=status.HTTP_201_CREATED)
async def subscribe_fund(fund_id: str, user: User = Depends(get_current_user)):

    logger.info(f"User {user.email} is trying to subscribe to fund {fund_id}")
    fund = await db['InvestmentFund'].find_one({"_id": ObjectId(fund_id)})
    logger.info(f"Fund found: {fund}")

    if not fund:
        logger.warning(f"Fund {fund_id} not found")
        raise HTTPException(status_code=404, detail="Fund not found")
    
    if user.balance < fund['minimumFee']:
        logger.warning(f"User {user.email} has insufficient funds to subscribe to {fund['name']}")
        raise HTTPException(status_code=400, detail=f"Not enough money to subscribe to the investment fund {fund['name']}")

    await db['Transaction'].insert_one({
        "customer_id": user.id,
        "fund_id": fund_id,
        "type": "Open",
        "amount": fund['minimumFee'],
        "timestamp": datetime.datetime.now()
    })

    await db['User'].update_one({"_id": ObjectId(user.id)}, {"$inc": {"balance": -fund['minimumFee']}})

    updateduser = await db['User'].find_one({"_id": ObjectId(user.id)})
    logger.info(updateduser)
    
    # Notification logic placeholder

    return {"message": f"Subscribed to {fund['name']}"}

@router.post('/cancel/{fund_id}')
async def cancel_fund(fund_id: str, user: User = Depends(get_current_user)):

    fund = await db['InvestmentFund'].find_one({"_id": ObjectId(fund_id)})

    if not fund:
        raise HTTPException(status_code=404, detail="Fund not found")
    

    await db['Transaction'].insert_one({
        "customer_id": user.id,
        "fund_id": fund_id,
        "type": "Close",
        "amount": -fund['minimumFee'],
        "timestamp": datetime.datetime.now()
    })

    await db['User'].update_one({"_id": ObjectId(user.id)}, {"$inc": {"balance": fund['minimumFee']}})

    return {"message": f"Cancelled subscription to {fund['name']}"}

# Admin-only endpoints
def is_admin(user: User):
    return "Admin" in user.roles

@router.get('/transactions')
async def get_transactions(user: User = Depends(get_current_user)) -> List[TransactionDetails]:

    pipeline = [
        {
            "$match": {
                "customer_id": user.id
            }
        },
        {
            "$lookup": {
                "from": "User",
                "let": {
                    "customerIdString": "$customer_id"
                },
                "pipeline": [
                    {
                        "$match": {
                            "$expr": {
                                "$eq": ["$_id", {"$toObjectId": "$$customerIdString"}]
                            }
                        }
                    }
                ],
                "as": "userDetails"
            }
        },

        {
            "$lookup": {
                "from": "InvestmentFund",
                "let": {
                    "fundIdString": "$fund_id"
                },
                "pipeline": [
                    {
                        "$match": {
                            "$expr": {
                                "$eq": ["$_id", {"$toObjectId": "$$fundIdString"}]
                            }
                        }
                    }
                ],
                "as": "fundDetails"
            }
        },

        {
            "$unwind": "$userDetails"
        },
        {
            "$unwind": "$fundDetails"
        },
        {
            "$project": {
                "_id": 1,
                "customerId": { "$toString": "$userDetails._id" },
                "customerName": "$userDetails.name",
                "amount": 1,
                "type": 1,
                "fundName": "$fundDetails.name",
                "fundCategory": "$fundDetails.category",
                "timestamp": 1
            }
        }
    ]

    try:
        transactions = await db['Transaction'].aggregate(pipeline).to_list()
        return transactions
    except Exception as e:
        print(f"Error fetching transactions: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.post('/create', status_code=status.HTTP_201_CREATED)
async def create_fund(fund:InvestmentFundCreate, user: User = Depends(get_current_user)):
    
    if not is_admin(user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin privileges required")

    fund_dict = fund.model_dump()
    response = await db.InvestmentFund.insert_one(fund_dict)
    print(response.inserted_id)
    return {"message": "Fund created successfully", "id": str(response.inserted_id)}


@router.get('/list', response_model=List[InvestmentFund])
async def list_funds(user: User = Depends(get_current_user)):

    funds = await db.InvestmentFund.find().to_list()
    return funds