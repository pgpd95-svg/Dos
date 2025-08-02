from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, date, timedelta
from enum import Enum

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Enums
class TransactionType(str, Enum):
    income = "income"
    expense = "expense"

class BudgetPeriod(str, Enum):
    weekly = "weekly"
    monthly = "monthly"
    yearly = "yearly"

# Models
class Category(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    color: str = "#3B82F6"
    type: TransactionType
    created_at: datetime = Field(default_factory=datetime.utcnow)

class CategoryCreate(BaseModel):
    name: str
    color: str = "#3B82F6"
    type: TransactionType

class Transaction(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    type: TransactionType
    amount: float
    category_id: str
    category_name: str
    description: Optional[str] = ""
    date: date
    currency: str = "USD"
    created_at: datetime = Field(default_factory=datetime.utcnow)

class TransactionCreate(BaseModel):
    type: TransactionType
    amount: float
    category_id: str
    description: Optional[str] = ""
    date: date
    currency: str = "USD"

class Budget(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    category_id: str
    category_name: str
    amount: float
    period: BudgetPeriod
    currency: str = "USD"
    created_at: datetime = Field(default_factory=datetime.utcnow)

class BudgetCreate(BaseModel):
    category_id: str
    amount: float
    period: BudgetPeriod
    currency: str = "USD"

class Settings(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    default_currency: str = "USD"
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class SettingsUpdate(BaseModel):
    default_currency: str

class BudgetOverview(BaseModel):
    category_id: str
    category_name: str
    category_color: str
    period: BudgetPeriod
    budget_amount: float
    spent_amount: float
    remaining_amount: float
    percentage_used: float
    is_over_budget: bool
    currency: str

# Routes
@api_router.get("/")
async def root():
    return {"message": "Budget Tracker API"}

# Categories
@api_router.post("/categories", response_model=Category)
async def create_category(category: CategoryCreate):
    category_dict = category.dict()
    category_obj = Category(**category_dict)
    await db.categories.insert_one(category_obj.dict())
    return category_obj

@api_router.get("/categories", response_model=List[Category])
async def get_categories():
    categories = await db.categories.find().to_list(1000)
    return [Category(**cat) for cat in categories]

@api_router.get("/categories/{category_type}", response_model=List[Category])
async def get_categories_by_type(category_type: TransactionType):
    categories = await db.categories.find({"type": category_type}).to_list(1000)
    return [Category(**cat) for cat in categories]

@api_router.delete("/categories/{category_id}")
async def delete_category(category_id: str):
    result = await db.categories.delete_one({"id": category_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Category not found")
    return {"message": "Category deleted"}

# Transactions
@api_router.post("/transactions", response_model=Transaction)
async def create_transaction(transaction: TransactionCreate):
    # Get category name
    category = await db.categories.find_one({"id": transaction.category_id})
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    transaction_dict = transaction.dict()
    transaction_dict["category_name"] = category["name"]
    transaction_obj = Transaction(**transaction_dict)
    await db.transactions.insert_one(transaction_obj.dict())
    return transaction_obj

@api_router.get("/transactions", response_model=List[Transaction])
async def get_transactions(limit: Optional[int] = 100):
    transactions = await db.transactions.find().sort("created_at", -1).limit(limit).to_list(limit)
    return [Transaction(**tx) for tx in transactions]

@api_router.get("/transactions/{transaction_type}", response_model=List[Transaction])
async def get_transactions_by_type(transaction_type: TransactionType, limit: Optional[int] = 100):
    transactions = await db.transactions.find({"type": transaction_type}).sort("created_at", -1).limit(limit).to_list(limit)
    return [Transaction(**tx) for tx in transactions]

@api_router.delete("/transactions/{transaction_id}")
async def delete_transaction(transaction_id: str):
    result = await db.transactions.delete_one({"id": transaction_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return {"message": "Transaction deleted"}

# Budgets
@api_router.post("/budgets", response_model=Budget)
async def create_budget(budget: BudgetCreate):
    # Check if budget already exists for this category and period
    existing_budget = await db.budgets.find_one({
        "category_id": budget.category_id,
        "period": budget.period
    })
    if existing_budget:
        # Update existing budget
        await db.budgets.update_one(
            {"id": existing_budget["id"]},
            {"$set": {"amount": budget.amount, "currency": budget.currency}}
        )
        updated_budget = await db.budgets.find_one({"id": existing_budget["id"]})
        return Budget(**updated_budget)
    
    # Get category name
    category = await db.categories.find_one({"id": budget.category_id})
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    budget_dict = budget.dict()
    budget_dict["category_name"] = category["name"]
    budget_obj = Budget(**budget_dict)
    await db.budgets.insert_one(budget_obj.dict())
    return budget_obj

@api_router.get("/budgets", response_model=List[Budget])
async def get_budgets():
    budgets = await db.budgets.find().to_list(1000)
    return [Budget(**budget) for budget in budgets]

@api_router.get("/budgets/{period}", response_model=List[Budget])
async def get_budgets_by_period(period: BudgetPeriod):
    budgets = await db.budgets.find({"period": period}).to_list(1000)
    return [Budget(**budget) for budget in budgets]

@api_router.delete("/budgets/{budget_id}")
async def delete_budget(budget_id: str):
    result = await db.budgets.delete_one({"id": budget_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Budget not found")
    return {"message": "Budget deleted"}

# Budget Overview
@api_router.get("/budget-overview/{period}", response_model=List[BudgetOverview])
async def get_budget_overview(period: BudgetPeriod):
    budgets = await db.budgets.find({"period": period}).to_list(1000)
    overview = []
    
    for budget in budgets:
        # Calculate date range based on period
        today = date.today()
        if period == BudgetPeriod.weekly:
            start_date = today - datetime.timedelta(days=today.weekday())
            end_date = start_date + datetime.timedelta(days=6)
        elif period == BudgetPeriod.monthly:
            start_date = today.replace(day=1)
            if today.month == 12:
                end_date = today.replace(year=today.year + 1, month=1, day=1) - datetime.timedelta(days=1)
            else:
                end_date = today.replace(month=today.month + 1, day=1) - datetime.timedelta(days=1)
        else:  # yearly
            start_date = today.replace(month=1, day=1)
            end_date = today.replace(month=12, day=31)
        
        # Calculate spent amount for this category in the period
        spent_transactions = await db.transactions.find({
            "category_id": budget["category_id"],
            "type": "expense",
            "date": {"$gte": start_date.isoformat(), "$lte": end_date.isoformat()}
        }).to_list(1000)
        
        spent_amount = sum(tx["amount"] for tx in spent_transactions)
        remaining_amount = budget["amount"] - spent_amount
        percentage_used = (spent_amount / budget["amount"] * 100) if budget["amount"] > 0 else 0
        is_over_budget = spent_amount > budget["amount"]
        
        # Get category details
        category = await db.categories.find_one({"id": budget["category_id"]})
        
        overview_item = BudgetOverview(
            category_id=budget["category_id"],
            category_name=budget["category_name"],
            category_color=category["color"] if category else "#3B82F6",
            period=budget["period"],
            budget_amount=budget["amount"],
            spent_amount=spent_amount,
            remaining_amount=remaining_amount,
            percentage_used=percentage_used,
            is_over_budget=is_over_budget,
            currency=budget["currency"]
        )
        overview.append(overview_item)
    
    return overview

# Settings
@api_router.get("/settings", response_model=Settings)
async def get_settings():
    settings = await db.settings.find_one()
    if not settings:
        # Create default settings
        default_settings = Settings()
        await db.settings.insert_one(default_settings.dict())
        return default_settings
    return Settings(**settings)

@api_router.put("/settings", response_model=Settings)
async def update_settings(settings_update: SettingsUpdate):
    settings = await db.settings.find_one()
    if not settings:
        # Create new settings
        new_settings = Settings(default_currency=settings_update.default_currency)
        await db.settings.insert_one(new_settings.dict())
        return new_settings
    
    # Update existing settings
    await db.settings.update_one(
        {"id": settings["id"]},
        {"$set": {"default_currency": settings_update.default_currency, "updated_at": datetime.utcnow()}}
    )
    updated_settings = await db.settings.find_one({"id": settings["id"]})
    return Settings(**updated_settings)

# Analytics
@api_router.get("/analytics/spending-by-category")
async def get_spending_by_category(period: Optional[str] = "monthly"):
    # Calculate date range based on period
    today = date.today()
    if period == "weekly":
        start_date = today - datetime.timedelta(days=today.weekday())
    elif period == "monthly":
        start_date = today.replace(day=1)
    else:  # yearly
        start_date = today.replace(month=1, day=1)
    
    # Aggregate spending by category
    pipeline = [
        {
            "$match": {
                "type": "expense",
                "date": {"$gte": start_date.isoformat()}
            }
        },
        {
            "$group": {
                "_id": {"category_id": "$category_id", "category_name": "$category_name"},
                "total_spent": {"$sum": "$amount"},
                "transaction_count": {"$sum": 1}
            }
        },
        {
            "$sort": {"total_spent": -1}
        }
    ]
    
    result = await db.transactions.aggregate(pipeline).to_list(1000)
    
    # Add category colors
    for item in result:
        category = await db.categories.find_one({"id": item["_id"]["category_id"]})
        item["color"] = category["color"] if category else "#3B82F6"
        item["category_name"] = item["_id"]["category_name"]
        item["category_id"] = item["_id"]["category_id"]
        del item["_id"]
    
    return result

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()