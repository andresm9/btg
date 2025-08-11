from app.database import db
from app.config import logging
from app.models import User, InvestmentFund, Transaction
from fastapi import HTTPException
from typing import Optional

logger = logging.getLogger(__name__)

class FundService:
    @staticmethod
    def subscribe(user_id: str, fund_id: str):
        
        logger.info(f"Service: subscribe called for user {user_id} to fund {fund_id}")
        
        user = db.users.find_one({"id": user_id})
        fund = db.investment_funds.find_one({"id": fund_id})

        if not fund:
            logger.warning(f"Service: Investment Fund not found {fund_id}")
            raise HTTPException(status_code=404, detail="Investment Fund not found")

        # Validate if user has sufficient balance
        if user['balance'] < fund['minimumFee']:

            logger.warning(f"FundService: Insufficient balance for user {user_id} to subscribe to Investment Fund {fund['name']}")
            raise HTTPException(status_code=400, detail=f"Not enough money to subscribe to the investment fund {fund['name']}")
        
        #Execute operation in the database as a transaction
        db.transactions.insert_one({
            "customer_id": user_id,
            "fund_id": fund_id,
            "type": "Open",
            "amount": fund['minimumFee'],
            "timestamp": "now"
        })

        
        db.users.update_one({"id": user_id}, {"$inc": {"balance": -fund['minimumFee']}})
        logger.info(f"Service: User {user_id} subscribed to fund {fund['name']}")
        return True

    @staticmethod
    def cancel(user_id: str, fund_id: str):
        logger.info(f"Service: cancel called for user {user_id} to fund {fund_id}")
        fund = db.investment_funds.find_one({"id": fund_id})
        if not fund:
            logger.warning(f"Service: Fund not found {fund_id}")
            raise HTTPException(status_code=404, detail="Fund not found")
        db.transactions.insert_one({
            "customer_id": user_id,
            "fund_id": fund_id,
            "type": "Close",
            "amount": fund['minimumFee'],
            "timestamp": "now"
        })
        db.users.update_one({"id": user_id}, {"$inc": {"balance": fund['minimumFee']}})
        logger.info(f"Service: User {user_id} cancelled subscription to fund {fund['name']}")
        return True

    @staticmethod
    def get_transactions(user_id: str):
        logger.info(f"Service: get_transactions called for user {user_id}")
        txs = list(db.transactions.find({"customer_id": user_id}))
        logger.info(f"Service: Returned {len(txs)} transactions for user {user_id}")
        return txs
