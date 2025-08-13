# Investment Fund Management Application

A FastAPI-based REST API for managing investment funds, customer subscriptions, notifications, and reporting. Uses MongoDB for data storage and JWT for authentication.

## Features
- Customer management with balance and notification preferences
- Investment fund subscription/cancellation
- Transaction reporting
- JWT authentication and role management
- Exception handling and clean code practices
- Unit testing
- AWS deployment via Serverless Framework and CloudFormation

## Setup
1. Install dependencies: `pip install -r requirements.txt`
2. Configure MongoDB connection in `.env`
3. Run the app: `fastapi run app/main.py`

## Testing
Run unit tests with:
```
pytest tests/
```

## Deployment
See `terraform` for AWS deployment instructions.
