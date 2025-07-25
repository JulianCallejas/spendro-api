from fastapi import APIRouter

from app.api.v1.endpoints import auth, users, budgets, transactions, sync, transcription

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(budgets.router, prefix="/budgets", tags=["budgets"])
api_router.include_router(transactions.router, prefix="/transactions", tags=["transactions"])
api_router.include_router(sync.router, prefix="/sync", tags=["synchronization"])
api_router.include_router(transcription.router, prefix="/transcription", tags=["transcription"])