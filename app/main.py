from fastapi import FastAPI, Request
from app.config import logging
from app.routers.routers import router
from app.routers.auth_router import router as auth_router
import logging

logger = logging.getLogger(__name__)

app = FastAPI()
app.include_router(auth_router)
app.include_router(router)

@app.get('/')
def root(request: Request = None):
    return {"message": "Welcome to the Investment Fund Management API"}


