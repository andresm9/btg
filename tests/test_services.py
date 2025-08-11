import pytest
from app.services import FundService
from app.models import User, InvestmentFund
from unittest.mock import patch

@pytest.fixture
def mock_db():
    class MockDB:
        users = {}
        investment_funds = {}
        transactions = []
        def find_one(self, query):
            if 'users' in query:
                return self.users.get(query['id'])
            if 'investment_funds' in query:
                return self.investment_funds.get(query['id'])
        def update_one(self, query, update):
            if 'users' in query:
                self.users[query['id']]['balance'] += update['$inc']['balance']
        def insert_one(self, doc):
            self.transactions.append(doc)
        def find(self, query):
            return [tx for tx in self.transactions if tx['customer_id'] == query['customer_id']]
    return MockDB()

@patch('app.services.db', new_callable=lambda: mock_db())
def test_subscribe_success(mock_db):
    mock_db.users = {'u1': {'id': 'u1', 'balance': 600}}
    mock_db.investment_funds = {'f1': {'id': 'f1', 'minimumFee': 100, 'name': 'TestFund'}}
    assert FundService.subscribe('u1', 'f1') is True
    assert mock_db.users['u1']['balance'] == 500

@patch('app.services.db', new_callable=lambda: mock_db())
def test_subscribe_insufficient_funds(mock_db):
    mock_db.users = {'u1': {'id': 'u1', 'balance': 50}}
    mock_db.investment_funds = {'f1': {'id': 'f1', 'minimumFee': 100, 'name': 'TestFund'}}
    with pytest.raises(Exception):
        FundService.subscribe('u1', 'f1')

@patch('app.services.db', new_callable=lambda: mock_db())
def test_cancel_success(mock_db):
    mock_db.users = {'u1': {'id': 'u1', 'balance': 500}}
    mock_db.investment_funds = {'f1': {'id': 'f1', 'minimumFee': 100, 'name': 'TestFund'}}
    assert FundService.cancel('u1', 'f1') is True
    assert mock_db.users['u1']['balance'] == 600
