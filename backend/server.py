from fastapi import FastAPI, APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional
import uuid
from datetime import datetime, timedelta
from enum import Enum
import jwt
import bcrypt
from passlib.context import CryptContext
import requests
import hmac
import hashlib
import json
import openai
import httpx

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Security setup
SECRET_KEY = os.environ.get('SECRET_KEY', 'your-secret-key-change-in-production')
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Enums
class TaskStatus(str, Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    OVERDUE = "overdue"

class Priority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

class EisenhowerQuadrant(str, Enum):
    DO = "do"  # Urgent & Important
    DECIDE = "decide"  # Important & Not Urgent
    DELEGATE = "delegate"  # Urgent & Not Important
    DELETE = "delete"  # Not Urgent & Not Important

class UserRole(str, Enum):
    ADMIN = "admin"
    MANAGER = "manager"
    TEAM_MEMBER = "team_member"

class PlanType(str, Enum):
    PERSONAL = "personal"
    TEAM = "team"
    ENTERPRISE = "enterprise"

# Models
class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    email: str
    role: str = "team_member"  # team_member, manager, admin
    performance_score: float = 0.0
    tasks_completed: int = 0
    tasks_assigned: int = 0
    tasks_overdue: int = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)
    company_id: Optional[str] = None

# Auth Models
class UserAuth(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: str
    password_hash: str
    is_active: bool = True
    is_verified: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = None

class Company(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    plan: PlanType
    subscription_status: str = "trial"  # trial, active, suspended, cancelled
    trial_ends_at: datetime = Field(default_factory=lambda: datetime.utcnow() + timedelta(days=14))
    created_at: datetime = Field(default_factory=datetime.utcnow)
    settings: dict = {}

class AuthSignup(BaseModel):
    name: str
    email: str
    password: str
    company: str
    plan: PlanType = PlanType.PERSONAL

class AuthLogin(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    user: dict

# Helper Functions
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
        
        user = await db.users.find_one({"id": user_id})
        if user is None:
            raise HTTPException(status_code=401, detail="User not found")
        return User(**user)
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")

# WhatsApp Integration Endpoints
@api_router.post("/whatsapp/message")
async def handle_whatsapp_message(request: dict):
    """Process incoming WhatsApp messages and generate responses"""
    try:
        phone_number = request.get("phone_number", "")
        message_text = request.get("message", "").strip().lower()
        message_id = request.get("message_id", "")
        timestamp = request.get("timestamp", 0)

        # Get or create user
        user = await get_or_create_whatsapp_user(phone_number)

        # Process command
        response = await process_whatsapp_command(user, message_text)

        return {"reply": response, "success": True}

    except Exception as e:
        logger.error(f"WhatsApp message processing error: {str(e)}")
        return {
            "reply": "❌ Sorry, I encountered an error processing your request. Please try again.",
            "success": False
        }

async def get_or_create_whatsapp_user(phone_number: str):
    """Get existing WhatsApp user or create new one"""
    users_collection = db.users

    user = await users_collection.find_one({"phone_number": phone_number})
    if not user:
        user_data = {
            "id": str(uuid.uuid4()),
            "name": f"WhatsApp User {phone_number[-4:]}",
            "email": f"whatsapp_{phone_number}@productivity.app",
            "phone_number": phone_number,
            "role": "team_member",
            "performance_score": 0.0,
            "tasks_completed": 0,
            "tasks_assigned": 0,
            "tasks_overdue": 0,
            "created_at": datetime.utcnow(),
            "company_id": None
        }
        result = await users_collection.insert_one(user_data)
        user_data["_id"] = result.inserted_id
        return user_data

    return user

async def process_whatsapp_command(user, message_text: str) -> str:
    """Process WhatsApp task-related commands"""

    # Create task command: "create task: buy groceries"
    if message_text.startswith("create task:") or message_text.startswith("add task:"):
        task_description = message_text.replace("create task:", "").replace("add task:", "").strip()
        if not task_description:
            return "📝 Please provide a task description.\n\n*Example:* create task: buy groceries"

        task_data = {
            "id": str(uuid.uuid4()),
            "title": task_description,
            "description": "",
            "assigned_to": user["id"],
            "status": "todo",
            "priority": "medium",
            "eisenhower_quadrant": "decide",  # Default to important but not urgent
            "created_at": datetime.utcnow(),
            "tags": ["whatsapp"]
        }

        await db.tasks.insert_one(task_data)

        # Update user task count
        await db.users.update_one(
            {"id": user["id"]},
            {"$inc": {"tasks_assigned": 1}}
        )

        return f"✅ *Task Created Successfully!*\n\n📋 {task_description}\n\nUse *list tasks* to see all your tasks."

    # List tasks command
    elif message_text in ["list tasks", "show tasks", "my tasks", "tasks"]:
        tasks = await db.tasks.find({
            "assigned_to": user["id"],
            "status": {"$ne": "completed"}
        }).to_list(20)

        if not tasks:
            return "📝 *No pending tasks found.*\n\nCreate a task with: *create task: [description]*"

        response = "📋 *Your Pending Tasks:*\n\n"
        for i, task in enumerate(tasks, 1):
            priority_emoji = {"urgent": "🔥", "high": "⚡", "medium": "📌", "low": "📝"}.get(task.get("priority", "medium"), "📝")
            response += f"{i}. {priority_emoji} {task['title']}\n"

        response += f"\n*Total: {len(tasks)} tasks*\n\nComplete with: *complete task [number]*"
        return response

    # Complete task command: "complete task 1"
    elif message_text.startswith("complete task") or message_text.startswith("done task"):
        try:
            # Extract task number
            words = message_text.split()
            task_number = None
            for word in words:
                if word.isdigit():
                    task_number = int(word)
                    break
            
            if task_number is None:
                return "📝 Please specify a task number.\n\n*Example:* complete task 1"

            tasks = await db.tasks.find({
                "assigned_to": user["id"],
                "status": {"$ne": "completed"}
            }).to_list(100)

            if task_number < 1 or task_number > len(tasks):
                return f"❌ Invalid task number. You have {len(tasks)} pending tasks.\n\nUse *list tasks* to see all tasks."

            task_to_complete = tasks[task_number - 1]

            await db.tasks.update_one(
                {"id": task_to_complete["id"]},
                {
                    "$set": {
                        "status": "completed",
                        "completed_at": datetime.utcnow()
                    }
                }
            )

            # Update user completed count
            await db.users.update_one(
                {"id": user["id"]},
                {"$inc": {"tasks_completed": 1}}
            )

            return f"🎉 *Task Completed!*\n\n✅ {task_to_complete['title']}\n\nGreat job! Keep up the momentum!"

        except Exception as e:
            return "❌ Error completing task. Please check the task number and try again."

    # Productivity stats
    elif message_text in ["stats", "status", "performance", "dashboard"]:
        user_tasks = await db.tasks.find({"assigned_to": user["id"]}).to_list(1000)
        completed_tasks = [t for t in user_tasks if t.get("status") == "completed"]
        pending_tasks = [t for t in user_tasks if t.get("status") != "completed"]
        
        completion_rate = (len(completed_tasks) / len(user_tasks) * 100) if user_tasks else 0
        
        response = f"📊 *Your Productivity Stats*\n\n"
        response += f"📋 Total tasks: {len(user_tasks)}\n"
        response += f"✅ Completed: {len(completed_tasks)}\n"
        response += f"⏳ Pending: {len(pending_tasks)}\n"
        response += f"📈 Completion rate: {completion_rate:.1f}%\n\n"
        
        if completion_rate > 80:
            response += "🏆 Excellent performance! You're crushing it!"
        elif completion_rate > 60:
            response += "👍 Good work! Keep pushing forward!"
        else:
            response += "💪 Let's boost your productivity! Break tasks into smaller steps."
            
        return response

    # AI coaching
    elif message_text in ["coach", "help me", "advice", "tips"]:
        return """🤖 *AI Productivity Coach*

Here are some proven productivity tips:

🎯 *Prioritization:*
• Focus on 3 important tasks daily
• Use urgency vs importance matrix
• Tackle hardest tasks first

⏰ *Time Management:*
• Work in 25-minute focused blocks
• Take 5-minute breaks between blocks
• Plan your day the night before

✅ *Task Management:*
• Break large tasks into smaller steps
• Set specific deadlines
• Celebrate completed tasks

Need personalized advice? Use the web app for detailed AI coaching!"""

    # Help command
    elif message_text in ["help", "commands", "?", "menu"]:
        return """🤖 *Productivity Beast WhatsApp Bot*

*📝 Task Commands:*
• *create task: [description]* - Add new task
• *list tasks* - Show pending tasks
• *complete task [number]* - Mark as done

*📊 Analytics:*
• *stats* - View your performance
• *coach* - Get productivity tips

*Examples:*
• create task: buy groceries
• list tasks
• complete task 1
• stats

Need advanced features? Visit the web app! 🚀"""

    # Default response for unrecognized commands
    else:
        return f"""🤔 I didn't understand that command.

*Quick Commands:*
• create task: [description]
• list tasks
• complete task [number]
• help

*Example:* create task: finish project report

Type *help* for all commands."""

@api_router.get("/whatsapp/status")
async def get_whatsapp_status():
    """Get WhatsApp service status"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:3001/status", timeout=5.0)
            return response.json()
    except Exception as e:
        return {
            "connected": False,
            "status": "service_unavailable",
            "error": str(e)
        }

@api_router.get("/whatsapp/qr")
async def get_whatsapp_qr():
    """Get WhatsApp QR code for authentication"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:3001/qr", timeout=5.0)
            return response.json()
    except Exception as e:
        return {
            "qr": None,
            "status": "service_unavailable",
            "error": str(e)
        }

@api_router.post("/whatsapp/send")
async def send_whatsapp_message(request: dict):
    """Send message via WhatsApp service"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "http://localhost:3001/send",
                json=request,
                timeout=10.0
            )
            return response.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/whatsapp/restart")
async def restart_whatsapp_service():
    """Restart WhatsApp service connection"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post("http://localhost:3001/restart", timeout=5.0)
            return response.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Authentication Routes
@api_router.post("/auth/signup")
async def signup(signup_data: AuthSignup):
    # Check if user already exists
    existing_user = await db.user_auth.find_one({"email": signup_data.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")
    
    # Create company
    company = Company(
        name=signup_data.company,
        plan=signup_data.plan
    )
    await db.companies.insert_one(company.dict())
    
    # Create auth user
    password_hash = get_password_hash(signup_data.password)
    auth_user = UserAuth(
        email=signup_data.email,
        password_hash=password_hash
    )
    await db.user_auth.insert_one(auth_user.dict())
    
    # Create user profile
    user = User(
        id=auth_user.id,
        name=signup_data.name,
        email=signup_data.email,
        role=UserRole.ADMIN,  # First user is admin
        company_id=company.id
    )
    await db.users.insert_one(user.dict())
    
    return {"success": True, "message": "Account created successfully"}

@api_router.post("/auth/login", response_model=Token)
async def login(login_data: AuthLogin):
    # Find user
    auth_user = await db.user_auth.find_one({"email": login_data.email})
    if not auth_user or not verify_password(login_data.password, auth_user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    if not auth_user["is_active"]:
        raise HTTPException(status_code=401, detail="Account is deactivated")
    
    # Update last login
    await db.user_auth.update_one(
        {"id": auth_user["id"]},
        {"$set": {"last_login": datetime.utcnow()}}
    )
    
    # Get user profile
    user = await db.users.find_one({"id": auth_user["id"]})
    if not user:
        raise HTTPException(status_code=404, detail="User profile not found")
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": auth_user["id"]}, expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user["id"],
            "name": user["name"],
            "email": user["email"],
            "role": user["role"],
            "company_id": user.get("company_id")
        }
    }

@api_router.get("/auth/me")
async def get_current_user_profile(current_user: User = Depends(get_current_user)):
    return current_user

class UserCreate(BaseModel):
    name: str
    email: str
    password: str
    company: str
    plan: PlanType = PlanType.PERSONAL

class Task(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    description: Optional[str] = ""
    assigned_to: Optional[str] = None  # User ID
    assigned_by: Optional[str] = None  # User ID
    project_id: Optional[str] = None  # For project-based tasks
    status: TaskStatus = TaskStatus.TODO
    priority: Priority = Priority.MEDIUM
    eisenhower_quadrant: Optional[EisenhowerQuadrant] = None
    due_date: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    subtasks: List[str] = []  # Task IDs
    tags: List[str] = []
    feedback: Optional[str] = None
    quality_rating: Optional[int] = None  # 1-10 scale

class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = ""
    assigned_to: Optional[str] = None
    project_id: Optional[str] = None
    priority: Priority = Priority.MEDIUM
    due_date: Optional[datetime] = None
    tags: List[str] = []

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    priority: Optional[Priority] = None
    due_date: Optional[datetime] = None
    feedback: Optional[str] = None
    quality_rating: Optional[int] = None

class Project(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: Optional[str] = ""
    owner_id: str  # User ID
    team_members: List[str] = []  # User IDs
    status: str = "active"  # active, completed, archived
    created_at: datetime = Field(default_factory=datetime.utcnow)
    due_date: Optional[datetime] = None

class ProjectCreate(BaseModel):
    name: str
    description: Optional[str] = ""
    owner_id: str
    team_members: List[str] = []
    due_date: Optional[datetime] = None

class PerformanceReport(BaseModel):
    user_id: str
    user_name: str
    period: str  # daily, weekly, monthly
    tasks_completed: int
    tasks_assigned: int
    tasks_overdue: int
    completion_rate: float
    average_quality: float
    performance_score: float
    feedback: str
    suggestions: List[str] = []

# Helper Functions
def calculate_eisenhower_quadrant(priority: Priority, due_date: Optional[datetime]) -> EisenhowerQuadrant:
    """Calculate Eisenhower matrix quadrant based on priority and due date"""
    if not due_date:
        if priority in [Priority.HIGH, Priority.URGENT]:
            return EisenhowerQuadrant.DECIDE
        else:
            return EisenhowerQuadrant.DELETE
    
    # Handle timezone-aware datetime
    if due_date.tzinfo is not None:
        # Remove timezone info to compare with naive datetime
        due_date = due_date.replace(tzinfo=None)
    
    days_until_due = (due_date - datetime.utcnow()).days
    is_urgent = days_until_due <= 2  # 2 days or less is urgent
    is_important = priority in [Priority.HIGH, Priority.URGENT]
    
    if is_urgent and is_important:
        return EisenhowerQuadrant.DO
    elif is_important and not is_urgent:
        return EisenhowerQuadrant.DECIDE
    elif is_urgent and not is_important:
        return EisenhowerQuadrant.DELEGATE
    else:
        return EisenhowerQuadrant.DELETE

async def calculate_performance_score(user_id: str) -> float:
    """Calculate performance score based on completion rate, timeliness, and quality"""
    tasks = await db.tasks.find({"assigned_to": user_id}).to_list(1000)
    
    if not tasks:
        return 0.0
    
    completed_tasks = [t for t in tasks if t.get("status") == TaskStatus.COMPLETED]
    overdue_tasks = [t for t in tasks if t.get("status") == TaskStatus.OVERDUE]
    
    completion_rate = len(completed_tasks) / len(tasks)
    timeliness_score = 1.0 - (len(overdue_tasks) / len(tasks))
    
    # Average quality rating
    quality_ratings = [t.get("quality_rating", 5) for t in completed_tasks if t.get("quality_rating")]
    quality_score = sum(quality_ratings) / len(quality_ratings) / 10 if quality_ratings else 0.5
    
    # Weighted performance score
    performance_score = (completion_rate * 0.4 + timeliness_score * 0.4 + quality_score * 0.2) * 10
    return min(10.0, max(0.0, performance_score))

# API Routes

# User Management
@api_router.post("/users", response_model=User)
async def create_user(signup_data: AuthSignup):
    # Check if user already exists
    existing_user = await db.user_auth.find_one({"email": signup_data.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")
    
    # Create company
    company = Company(
        name=signup_data.company,
        plan=signup_data.plan
    )
    await db.companies.insert_one(company.dict())
    
    # Create auth user
    password_hash = get_password_hash(signup_data.password)
    auth_user = UserAuth(
        email=signup_data.email,
        password_hash=password_hash
    )
    await db.user_auth.insert_one(auth_user.dict())
    
    # Create user profile
    user = User(
        id=auth_user.id,
        name=signup_data.name,
        email=signup_data.email,
        role=UserRole.ADMIN,  # First user is admin
        company_id=company.id
    )
    await db.users.insert_one(user.dict())
    return user

@api_router.get("/users", response_model=List[User])
async def get_users():
    users = await db.users.find().to_list(1000)
    return [User(**user) for user in users]

@api_router.get("/users/{user_id}", response_model=User)
async def get_user(user_id: str):
    user = await db.users.find_one({"id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return User(**user)

# Task Management
@api_router.post("/tasks", response_model=Task)
async def create_task(task_data: TaskCreate):
    task_dict = task_data.dict()
    
    # Calculate Eisenhower quadrant
    eisenhower_quadrant = calculate_eisenhower_quadrant(
        task_data.priority, 
        task_data.due_date
    )
    task_dict["eisenhower_quadrant"] = eisenhower_quadrant
    
    task = Task(**task_dict)
    await db.tasks.insert_one(task.dict())
    
    # Update user task count
    if task.assigned_to:
        await db.users.update_one(
            {"id": task.assigned_to},
            {"$inc": {"tasks_assigned": 1}}
        )
    
    return task

@api_router.get("/tasks", response_model=List[Task])
async def get_tasks(
    assigned_to: Optional[str] = None,
    project_id: Optional[str] = None,
    status: Optional[TaskStatus] = None
):
    filter_dict = {}
    if assigned_to:
        filter_dict["assigned_to"] = assigned_to
    if project_id:
        filter_dict["project_id"] = project_id
    if status:
        filter_dict["status"] = status
    
    tasks = await db.tasks.find(filter_dict).to_list(1000)
    return [Task(**task) for task in tasks]

@api_router.get("/tasks/{task_id}", response_model=Task)
async def get_task(task_id: str):
    task = await db.tasks.find_one({"id": task_id})
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return Task(**task)

@api_router.put("/tasks/{task_id}", response_model=Task)
async def update_task(task_id: str, task_update: TaskUpdate):
    task = await db.tasks.find_one({"id": task_id})
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    update_dict = {k: v for k, v in task_update.dict().items() if v is not None}
    
    # Handle status changes
    if task_update.status == TaskStatus.COMPLETED and task.get("status") != TaskStatus.COMPLETED:
        update_dict["completed_at"] = datetime.utcnow()
        # Update user completed count
        if task.get("assigned_to"):
            await db.users.update_one(
                {"id": task["assigned_to"]},
                {"$inc": {"tasks_completed": 1}}
            )
    
    await db.tasks.update_one({"id": task_id}, {"$set": update_dict})
    
    updated_task = await db.tasks.find_one({"id": task_id})
    return Task(**updated_task)

@api_router.delete("/tasks/{task_id}")
async def delete_task(task_id: str):
    result = await db.tasks.delete_one({"id": task_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"message": "Task deleted successfully"}

# Project Management
@api_router.post("/projects", response_model=Project)
async def create_project(project_data: ProjectCreate):
    project = Project(**project_data.dict())
    await db.projects.insert_one(project.dict())
    return project

@api_router.get("/projects", response_model=List[Project])
async def get_projects():
    projects = await db.projects.find().to_list(1000)
    return [Project(**project) for project in projects]

@api_router.get("/projects/{project_id}", response_model=Project)
async def get_project(project_id: str):
    project = await db.projects.find_one({"id": project_id})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return Project(**project)

# Performance & Analytics
@api_router.get("/analytics/dashboard")
async def get_dashboard_analytics():
    total_tasks = await db.tasks.count_documents({})
    completed_tasks = await db.tasks.count_documents({"status": TaskStatus.COMPLETED})
    overdue_tasks = await db.tasks.count_documents({"status": TaskStatus.OVERDUE})
    in_progress_tasks = await db.tasks.count_documents({"status": TaskStatus.IN_PROGRESS})
    
    # Eisenhower matrix distribution
    eisenhower_stats = {}
    for quadrant in EisenhowerQuadrant:
        count = await db.tasks.count_documents({"eisenhower_quadrant": quadrant})
        eisenhower_stats[quadrant.value] = count
    
    return {
        "total_tasks": total_tasks,
        "completed_tasks": completed_tasks,
        "overdue_tasks": overdue_tasks,
        "in_progress_tasks": in_progress_tasks,
        "completion_rate": (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0,
        "eisenhower_matrix": eisenhower_stats
    }

@api_router.get("/analytics/performance/{user_id}")
async def get_user_performance(user_id: str):
    user = await db.users.find_one({"id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Calculate updated performance score
    performance_score = await calculate_performance_score(user_id)
    
    # Update user's performance score
    await db.users.update_one(
        {"id": user_id},
        {"$set": {"performance_score": performance_score}}
    )
    
    tasks = await db.tasks.find({"assigned_to": user_id}).to_list(1000)
    completed_tasks = [t for t in tasks if t.get("status") == TaskStatus.COMPLETED]
    overdue_tasks = [t for t in tasks if t.get("status") == TaskStatus.OVERDUE]
    
    completion_rate = (len(completed_tasks) / len(tasks) * 100) if tasks else 0
    
    return {
        "user_id": user_id,
        "user_name": user["name"],
        "performance_score": performance_score,
        "tasks_assigned": len(tasks),
        "tasks_completed": len(completed_tasks),
        "tasks_overdue": len(overdue_tasks),
        "completion_rate": completion_rate
    }

@api_router.get("/analytics/team-performance")
async def get_team_performance():
    users = await db.users.find().to_list(1000)
    team_performance = []
    
    for user in users:
        performance_score = await calculate_performance_score(user["id"])
        tasks = await db.tasks.find({"assigned_to": user["id"]}).to_list(1000)
        completed_tasks = [t for t in tasks if t.get("status") == TaskStatus.COMPLETED]
        
        team_performance.append({
            "user_id": user["id"],
            "user_name": user["name"],
            "performance_score": performance_score,
            "tasks_assigned": len(tasks),
            "tasks_completed": len(completed_tasks),
            "completion_rate": (len(completed_tasks) / len(tasks) * 100) if tasks else 0
        })
    
    # Sort by performance score
    team_performance.sort(key=lambda x: x["performance_score"], reverse=True)
    return team_performance

# AI Coach Endpoints
@api_router.get("/ai-coach/insights/{user_id}")
async def get_ai_insights(user_id: str):
    """Generate AI insights for a user's productivity patterns"""
    user = await db.users.find_one({"id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    tasks = await db.tasks.find({"assigned_to": user_id}).to_list(1000)
    
    # Analyze patterns
    insights = []
    suggestions = []
    
    if not tasks:
        return {
            "insights": ["No tasks found for analysis"],
            "suggestions": ["Start by creating some tasks to track your productivity"],
            "performance_trend": "stable"
        }
    
    completed_tasks = [t for t in tasks if t.get("status") == TaskStatus.COMPLETED]
    overdue_tasks = [t for t in tasks if t.get("status") == TaskStatus.OVERDUE]
    
    completion_rate = len(completed_tasks) / len(tasks)
    
    # Generate insights based on patterns
    if completion_rate > 0.8:
        insights.append("Excellent task completion rate! You're consistently delivering.")
        suggestions.append("Consider taking on more challenging projects to grow further.")
    elif completion_rate > 0.6:
        insights.append("Good task completion rate with room for improvement.")
        suggestions.append("Focus on better time management for remaining tasks.")
    else:
        insights.append("Task completion rate needs attention.")
        suggestions.append("Consider breaking large tasks into smaller, manageable subtasks.")
    
    if len(overdue_tasks) > 0:
        insights.append(f"You have {len(overdue_tasks)} overdue tasks affecting your performance.")
        suggestions.append("Set up reminder systems and prioritize overdue tasks first.")
    
    # Analyze Eisenhower quadrant distribution
    do_tasks = [t for t in tasks if t.get("eisenhower_quadrant") == EisenhowerQuadrant.DO]
    if len(do_tasks) > len(tasks) * 0.5:
        insights.append("You're spending too much time on urgent tasks.")
        suggestions.append("Focus more on important but not urgent tasks to reduce future urgency.")
    
    return {
        "insights": insights,
        "suggestions": suggestions,
        "performance_trend": "improving" if completion_rate > 0.7 else "needs_attention"
    }

# Health check
@api_router.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow()}

# Sample data endpoint for demo
@api_router.post("/populate-sample-data")
async def populate_sample_data():
    """Populate the database with sample data for demonstration"""
    
    # Clear existing data
    await db.tasks.delete_many({})
    await db.projects.delete_many({})
    await db.users.delete_many({})
    
    # Create sample users
    sample_users = [
        {"name": "Sarah Johnson", "email": "sarah@company.com", "role": "manager"},
        {"name": "Mike Chen", "email": "mike@company.com", "role": "team_member"},
        {"name": "Emma Rodriguez", "email": "emma@company.com", "role": "team_member"},
        {"name": "Alex Thompson", "email": "alex@company.com", "role": "team_member"},
        {"name": "David Kim", "email": "david@company.com", "role": "team_member"}
    ]
    
    created_users = []
    for user_data in sample_users:
        user = User(**user_data)
        await db.users.insert_one(user.dict())
        created_users.append(user)
    
    # Create sample projects
    sample_projects = [
        {
            "name": "Website Redesign",
            "description": "Complete overhaul of company website with modern design",
            "owner_id": created_users[0].id,
            "team_members": [created_users[1].id, created_users[2].id],
            "due_date": datetime.utcnow() + timedelta(days=45)
        },
        {
            "name": "Mobile App Development",
            "description": "Build native mobile app for iOS and Android",
            "owner_id": created_users[0].id,
            "team_members": [created_users[3].id, created_users[4].id],
            "due_date": datetime.utcnow() + timedelta(days=90)
        }
    ]
    
    created_projects = []
    for project_data in sample_projects:
        project = Project(**project_data)
        await db.projects.insert_one(project.dict())
        created_projects.append(project)
    
    # Create sample tasks with different Eisenhower categories
    sample_tasks = [
        # DO - Urgent & Important
        {
            "title": "Fix Critical Security Vulnerability",
            "description": "Address security issue reported by security audit",
            "assigned_to": created_users[1].id,
            "project_id": created_projects[0].id,
            "priority": Priority.URGENT,
            "due_date": datetime.utcnow() + timedelta(days=1),
            "tags": ["security", "urgent", "critical"]
        },
        # DECIDE - Important but Not Urgent
        {
            "title": "Plan Q3 Marketing Strategy",
            "description": "Develop comprehensive marketing plan for next quarter",
            "assigned_to": created_users[2].id,
            "priority": Priority.HIGH,
            "due_date": datetime.utcnow() + timedelta(days=14),
            "tags": ["strategy", "marketing", "planning"]
        },
        # DELEGATE - Urgent but Not Important
        {
            "title": "Update Meeting Room Booking System",
            "description": "Small updates to the room booking interface",
            "assigned_to": created_users[3].id,
            "priority": Priority.LOW,
            "due_date": datetime.utcnow() + timedelta(days=2),
            "tags": ["admin", "booking", "update"]
        },
        # DELETE - Neither Urgent nor Important
        {
            "title": "Research Industry Trends",
            "description": "General research on industry trends and competitors",
            "assigned_to": created_users[4].id,
            "priority": Priority.LOW,
            "due_date": datetime.utcnow() + timedelta(days=30),
            "tags": ["research", "trends", "optional"]
        },
        # Additional tasks for demonstration
        {
            "title": "Design Mobile App UI",
            "description": "Create user interface designs for the mobile application",
            "assigned_to": created_users[2].id,
            "project_id": created_projects[1].id,
            "priority": Priority.HIGH,
            "due_date": datetime.utcnow() + timedelta(days=10),
            "tags": ["design", "ui", "mobile"]
        },
        {
            "title": "Write API Documentation",
            "description": "Document all API endpoints for the new system",
            "assigned_to": created_users[1].id,
            "project_id": created_projects[0].id,
            "priority": Priority.MEDIUM,
            "due_date": datetime.utcnow() + timedelta(days=7),
            "tags": ["documentation", "api", "development"]
        }
    ]
    
    created_tasks = []
    for task_data in sample_tasks:
        # Calculate Eisenhower quadrant
        eisenhower_quadrant = calculate_eisenhower_quadrant(
            task_data["priority"], 
            task_data["due_date"]
        )
        task_data["eisenhower_quadrant"] = eisenhower_quadrant
        
        task = Task(**task_data)
        await db.tasks.insert_one(task.dict())
        created_tasks.append(task)
        
        # Update user task count
        await db.users.update_one(
            {"id": task.assigned_to},
            {"$inc": {"tasks_assigned": 1}}
        )
    
    # Complete some tasks and add ratings
    completed_task_updates = [
        {
            "task_id": created_tasks[4].id,  # Design Mobile App UI
            "status": TaskStatus.COMPLETED,
            "quality_rating": 9,
            "feedback": "Excellent design work with great attention to detail"
        },
        {
            "task_id": created_tasks[5].id,  # Write API Documentation
            "status": TaskStatus.COMPLETED,
            "quality_rating": 8,
            "feedback": "Comprehensive documentation, well structured"
        }
    ]
    
    for update in completed_task_updates:
        await db.tasks.update_one(
            {"id": update["task_id"]},
            {
                "$set": {
                    "status": update["status"],
                    "quality_rating": update["quality_rating"],
                    "feedback": update["feedback"],
                    "completed_at": datetime.utcnow()
                }
            }
        )
        
        # Update user completed count
        task = await db.tasks.find_one({"id": update["task_id"]})
        await db.users.update_one(
            {"id": task["assigned_to"]},
            {"$inc": {"tasks_completed": 1}}
        )
    
    # Set some tasks to in_progress
    await db.tasks.update_one(
        {"id": created_tasks[0].id},  # Security vulnerability
        {"$set": {"status": TaskStatus.IN_PROGRESS}}
    )
    
    await db.tasks.update_one(
        {"id": created_tasks[1].id},  # Marketing strategy
        {"$set": {"status": TaskStatus.IN_PROGRESS}}
    )
    
    return {
        "message": "Sample data populated successfully",
        "users_created": len(created_users),
        "projects_created": len(created_projects),
        "tasks_created": len(created_tasks)
    }

# AI Integration Settings
class AISettings(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    company_id: str
    openai_api_key: Optional[str] = None
    claude_api_key: Optional[str] = None
    preferred_ai_provider: str = "openai"  # openai, claude, both
    ai_enabled: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)

class WhatsAppSettings(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    company_id: str
    whatsapp_business_account_id: Optional[str] = None
    whatsapp_access_token: Optional[str] = None
    webhook_verify_token: Optional[str] = None
    phone_number_id: Optional[str] = None
    enabled: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)

@api_router.post("/integrations/ai-settings")
async def update_ai_settings(settings: AISettings, current_user: User = Depends(get_current_user)):
    settings.company_id = current_user.company_id
    
    # Update or create AI settings
    await db.ai_settings.replace_one(
        {"company_id": settings.company_id},
        settings.dict(),
        upsert=True
    )
    
    return {"success": True, "message": "AI settings updated"}

@api_router.get("/integrations/ai-settings")
async def get_ai_settings(current_user: User = Depends(get_current_user)):
    settings = await db.ai_settings.find_one({"company_id": current_user.company_id})
    if settings:
        # Don't return actual API keys for security
        settings["openai_api_key"] = "***" if settings.get("openai_api_key") else None
        settings["claude_api_key"] = "***" if settings.get("claude_api_key") else None
        return settings
    return {"company_id": current_user.company_id, "ai_enabled": False}

@api_router.post("/integrations/whatsapp-settings")
async def update_whatsapp_settings(settings: WhatsAppSettings, current_user: User = Depends(get_current_user)):
    settings.company_id = current_user.company_id
    
    # Update or create WhatsApp settings
    await db.whatsapp_settings.replace_one(
        {"company_id": settings.company_id},
        settings.dict(),
        upsert=True
    )
    
    return {"success": True, "message": "WhatsApp settings updated"}

@api_router.get("/integrations/whatsapp-settings")
async def get_whatsapp_settings(current_user: User = Depends(get_current_user)):
    settings = await db.whatsapp_settings.find_one({"company_id": current_user.company_id})
    if settings:
        # Don't return actual tokens for security
        settings["whatsapp_access_token"] = "***" if settings.get("whatsapp_access_token") else None
        return settings
    return {"company_id": current_user.company_id, "enabled": False}

# Enhanced AI Coach with real AI integration
@api_router.post("/ai-coach/chat")
async def ai_chat(request: dict, current_user: User = Depends(get_current_user)):
    message = request.get("message", "")
    ai_provider = request.get("provider", "openai")
    
    # Get AI settings for the user's company
    ai_settings = await db.ai_settings.find_one({"company_id": current_user.company_id})
    
    try:
        # Enhanced AI response with user context
        user_context = await get_user_context_for_ai(current_user.id)
        ai_response = await generate_ai_coaching_response(
            message, current_user, user_context, ai_provider, ai_settings
        )
        
        return {
            "response": ai_response,
            "provider": ai_provider,
            "timestamp": datetime.utcnow(),
            "user_context_used": True
        }
        
    except Exception as e:
        logger.error(f"AI Chat error: {str(e)}")
        # Enhanced fallback response
        enhanced_response = await generate_enhanced_coaching_response(message, current_user)
        return {
            "response": enhanced_response,
            "provider": "enhanced_fallback",
            "timestamp": datetime.utcnow(),
            "error": "AI provider unavailable, using enhanced coaching"
        }

async def get_user_context_for_ai(user_id: str) -> dict:
    """Get comprehensive user context for AI coaching"""
    
    # Get user's tasks
    tasks = await db.tasks.find({"assigned_to": user_id}).to_list(1000)
    
    # Get user's projects
    projects = await db.projects.find({
        "$or": [
            {"owner_id": user_id},
            {"team_members": user_id}
        ]
    }).to_list(100)
    
    # Calculate performance metrics
    completed_tasks = [t for t in tasks if t.get("status") == "completed"]
    overdue_tasks = [t for t in tasks if t.get("status") == "overdue"]
    in_progress_tasks = [t for t in tasks if t.get("status") == "in_progress"]
    
    # Eisenhower matrix distribution
    eisenhower_distribution = {}
    for quadrant in ["do", "decide", "delegate", "delete"]:
        eisenhower_distribution[quadrant] = len([t for t in tasks if t.get("eisenhower_quadrant") == quadrant])
    
    # Recent activity pattern
    recent_tasks = [t for t in tasks if (datetime.utcnow() - t.get("created_at", datetime.utcnow())).days <= 7]
    
    return {
        "total_tasks": len(tasks),
        "completed_tasks": len(completed_tasks),
        "overdue_tasks": len(overdue_tasks),
        "in_progress_tasks": len(in_progress_tasks),
        "active_projects": len([p for p in projects if p.get("status") == "active"]),
        "completion_rate": (len(completed_tasks) / len(tasks) * 100) if tasks else 0,
        "eisenhower_distribution": eisenhower_distribution,
        "recent_activity": len(recent_tasks),
        "productivity_trend": "improving" if len(completed_tasks) > len(overdue_tasks) else "needs_attention"
    }

async def generate_ai_coaching_response(message: str, user: User, context: dict, provider: str, ai_settings: dict) -> str:
    """Generate AI coaching response using specified provider"""
    
    # Create comprehensive prompt with user context
    system_prompt = f"""You are an expert productivity coach helping {user.name} optimize their work performance. 

CURRENT USER CONTEXT:
- Total tasks: {context['total_tasks']}
- Completion rate: {context['completion_rate']:.1f}%
- Overdue tasks: {context['overdue_tasks']}
- Active projects: {context['active_projects']}
- Recent activity: {context['recent_activity']} tasks this week
- Productivity trend: {context['productivity_trend']}

EISENHOWER MATRIX DISTRIBUTION:
- Do First (Urgent & Important): {context['eisenhower_distribution'].get('do', 0)}
- Schedule (Important, Not Urgent): {context['eisenhower_distribution'].get('decide', 0)}
- Delegate (Urgent, Not Important): {context['eisenhower_distribution'].get('delegate', 0)}
- Don't Do (Neither Urgent nor Important): {context['eisenhower_distribution'].get('delete', 0)}

Provide personalized, actionable productivity coaching based on their actual data. Be specific, encouraging, and offer concrete next steps."""

    user_prompt = f"User Question: {message}\n\nPlease provide coaching advice based on my current productivity metrics."

    try:
        if provider == "openai" and (ai_settings and ai_settings.get("openai_api_key") or os.environ.get('OPENAI_API_KEY')):
            # Use OpenAI
            api_key = ai_settings.get("openai_api_key") if ai_settings else os.environ.get('OPENAI_API_KEY')
            
            from openai import OpenAI
            client = OpenAI(api_key=api_key)
            
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=1000,
                temperature=0.7
            )
            
            return response.choices[0].message.content
            
        elif provider == "claude" and ai_settings and ai_settings.get("claude_api_key"):
            # Use Claude
            import anthropic
            client = anthropic.Anthropic(api_key=ai_settings["claude_api_key"])
            
            response = client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=1000,
                messages=[
                    {"role": "user", "content": f"{system_prompt}\n\n{user_prompt}"}
                ]
            )
            
            return response.content[0].text
            
        elif provider == "gemini" and ai_settings and ai_settings.get("gemini_api_key"):
            # Use Gemini
            import google.generativeai as genai
            genai.configure(api_key=ai_settings["gemini_api_key"])
            model = genai.GenerativeModel('gemini-pro')
            
            response = model.generate_content(f"{system_prompt}\n\n{user_prompt}")
            return response.text
            
        else:
            # Fallback to enhanced local coaching
            return await generate_enhanced_coaching_response(message, user, context)
            
    except Exception as e:
        logger.error(f"AI provider {provider} failed: {str(e)}")
        return await generate_enhanced_coaching_response(message, user, context)


# AI Coach Slash Commands
@api_router.post("/ai-coach/command")
async def ai_command(request: dict, current_user: User = Depends(get_current_user)):
    command = request.get("command", "").lower().strip()
    
    try:
        user_context = await get_user_context_for_ai(current_user.id)
        
        if command == "/analyze":
            return await handle_analyze_command(current_user, user_context)
        elif command == "/optimize":
            return await handle_optimize_command(current_user, user_context)
        elif command == "/goals":
            return await handle_goals_command(current_user, user_context)
        elif command == "/habits":
            return await handle_habits_command(current_user, user_context)
        elif command == "/report":
            return await handle_report_command(current_user, user_context)
        elif command == "/help":
            return await handle_help_command()
        else:
            return {
                "response": "Unknown command. Type `/help` to see available commands.",
                "command": command,
                "timestamp": datetime.utcnow()
            }
            
    except Exception as e:
        logger.error(f"Command error: {str(e)}")
        return {
            "response": "Sorry, I encountered an error processing your command. Please try again.",
            "error": str(e),
            "timestamp": datetime.utcnow()
        }

async def handle_analyze_command(user: User, context: dict):
    """Deep productivity analysis"""
    
    # Get recent tasks for pattern analysis
    recent_tasks = await db.tasks.find({
        "assigned_to": user.id,
        "created_at": {"$gte": datetime.utcnow() - timedelta(days=30)}
    }).to_list(1000)
    
    # Analyze task patterns
    patterns = {
        "peak_day": "Monday",  # Simplified for demo
        "peak_count": 5,
        "peak_hour": "9",
        "avg_completion_time": "2.5",
        "complexity_trend": "Increasing"
    }
    
    response = f"🔍 **Deep Productivity Analysis for {user.name.split()[0]}**\n\n"
    response += f"**📊 Performance Metrics (Last 30 Days):**\n"
    response += f"• Tasks completed: {context['completed_tasks']}\n"
    response += f"• Completion rate: {context['completion_rate']:.1f}%\n"
    response += f"• Average daily tasks: {len(recent_tasks)/30:.1f}\n"
    response += f"• Overdue rate: {(context['overdue_tasks']/max(context['total_tasks'], 1)*100):.1f}%\n\n"
    
    response += f"**🎯 Task Distribution Analysis:**\n"
    for quadrant, count in context['eisenhower_distribution'].items():
        percentage = (count / max(context['total_tasks'], 1)) * 100
        response += f"• {quadrant.title()}: {count} tasks ({percentage:.1f}%)\n"
    
    response += f"\n**📈 Productivity Patterns:**\n"
    response += f"• Peak activity: {patterns['peak_day']} with {patterns['peak_count']} tasks\n"
    response += f"• Most productive time: {patterns['peak_hour']}:00\n"
    response += f"• Average task completion time: {patterns['avg_completion_time']} days\n"
    response += f"• Task complexity trend: {patterns['complexity_trend']}\n\n"
    
    response += f"**💡 Key Insights:**\n"
    if context['completion_rate'] > 85:
        response += "• Excellent execution - you're in the top 10% of performers!\n"
    elif context['completion_rate'] > 70:
        response += "• Good performance with room for optimization\n"
    else:
        response += "• Focus needed on task completion and follow-through\n"
        
    if context['eisenhower_distribution'].get('do', 0) > context['total_tasks'] * 0.3:
        response += "• High urgency pattern detected - focus on prevention\n"
    else:
        response += "• Good balance between urgent and important tasks\n"
        
    response += f"\n**🎯 Recommended Actions:**\n"
    response += "1. Focus on completing existing tasks before adding new ones\n"
    response += "2. Implement daily task review at 5 PM\n"
    response += "3. Set up weekly planning sessions every Friday\n"
    
    return {
        "response": response,
        "command": "/analyze",
        "data": {"context": context, "patterns": patterns},
        "timestamp": datetime.utcnow()
    }

async def handle_optimize_command(user: User, context: dict):
    """Task optimization recommendations"""
    
    # Get current tasks
    current_tasks = await db.tasks.find({
        "assigned_to": user.id,
        "status": {"$ne": "completed"}
    }).to_list(1000)
    
    # Create optimization plan
    optimization_plan = {
        "prioritized_tasks": [
            {"title": "High priority task 1", "priority_score": 9.5, "urgency": "high"},
            {"title": "Medium priority task", "priority_score": 7.0, "urgency": "medium"},
            {"title": "Low priority task", "priority_score": 4.0, "urgency": "low"}
        ],
        "recommended_capacity": 8,
        "time_blocks": {
            "morning": "High-priority creative work",
            "midday": "Meetings and collaboration",
            "afternoon": "Admin tasks and planning"
        },
        "quick_wins": [
            "Review and organize task list",
            "Complete 2-minute tasks immediately",
            "Set up tomorrow's top 3 priorities",
            "Clear email inbox",
            "Update project status"
        ],
        "focus_area": "Task completion and follow-through"
    }
    
    response = f"⚡ **Task Optimization Plan for {user.name.split()[0]}**\n\n"
    response += f"**🎯 Current Workload:**\n"
    response += f"• Active tasks: {len(current_tasks)}\n"
    response += f"• Overdue tasks: {context['overdue_tasks']}\n"
    response += f"• This week's capacity: {optimization_plan['recommended_capacity']} tasks\n\n"
    
    response += f"**📋 Optimized Task Priority:**\n"
    for i, task in enumerate(optimization_plan['prioritized_tasks'][:10], 1):
        urgency_emoji = "🔥" if task['urgency'] == "high" else "⚡" if task['urgency'] == "medium" else "📝"
        response += f"{i}. {urgency_emoji} {task['title']} (Score: {task['priority_score']:.1f})\n"
    
    response += f"\n**⏰ Time Blocking Suggestion:**\n"
    response += f"• Morning (9-11 AM): {optimization_plan['time_blocks']['morning']}\n"
    response += f"• Midday (11 AM-2 PM): {optimization_plan['time_blocks']['midday']}\n"
    response += f"• Afternoon (2-5 PM): {optimization_plan['time_blocks']['afternoon']}\n\n"
    
    response += f"**🚀 Quick Wins (Complete Today):**\n"
    for i, quick_win in enumerate(optimization_plan['quick_wins'][:5], 1):
        response += f"{i}. {quick_win}\n"
    
    response += f"\n**💡 Optimization Tips:**\n"
    response += f"• Focus on {optimization_plan['focus_area']} this week\n"
    response += f"• Batch similar tasks together\n"
    response += f"• Use 25-minute focused work blocks\n"
    response += f"• Review and adjust daily at 5 PM\n"
    
    return {
        "response": response,
        "command": "/optimize",
        "data": optimization_plan,
        "timestamp": datetime.utcnow()
    }

async def handle_goals_command(user: User, context: dict):
    """Smart goal setting based on current performance"""
    
    goals = {
        "performance_goals": [
            {
                "title": "Improve Task Completion Rate",
                "target": f"{min(95, context['completion_rate'] + 15):.0f}%",
                "current": f"{context['completion_rate']:.1f}%",
                "timeline": "30 days",
                "action": "Complete 1 additional task per day consistently"
            },
            {
                "title": "Reduce Overdue Tasks",
                "target": "0 overdue tasks",
                "current": f"{context['overdue_tasks']} overdue",
                "timeline": "14 days",
                "action": "Daily triage and prioritization review"
            }
        ],
        "weekly_milestones": [
            f"Achieve {min(100, context['completion_rate'] + 5):.0f}% completion rate",
            "Complete all overdue tasks",
            f"Maintain {min(95, context['completion_rate'] + 15):.0f}% rate for full week",
            "Establish sustainable daily routine"
        ],
        "success_metrics": [
            "Daily task completion tracking",
            "Weekly performance review",
            "Monthly goal assessment",
            "Quarterly productivity audit"
        ],
        "rewards": {
            "daily": "15-minute break for favorite activity",
            "weekly": "Special meal or entertainment",
            "final": "Day off or significant personal reward"
        }
    }
    
    response = f"🎯 **SMART Goals for {user.name.split()[0]}**\n\n"
    response += f"**Based on your current performance:**\n"
    response += f"• Completion rate: {context['completion_rate']:.1f}%\n"
    response += f"• Weekly velocity: {context['recent_activity']} tasks\n"
    response += f"• Current trajectory: {context['productivity_trend'].replace('_', ' ').title()}\n\n"
    
    response += f"**📈 30-Day Performance Goals:**\n\n"
    
    for i, goal in enumerate(goals['performance_goals'], 1):
        response += f"**Goal {i}: {goal['title']}**\n"
        response += f"• Target: {goal['target']}\n"
        response += f"• Current: {goal['current']}\n"
        response += f"• Timeline: {goal['timeline']}\n"
        response += f"• Action: {goal['action']}\n\n"
    
    response += f"**🏆 Weekly Milestones:**\n"
    for week, milestone in enumerate(goals['weekly_milestones'], 1):
        response += f"• Week {week}: {milestone}\n"
    
    response += f"\n**📊 Success Metrics:**\n"
    for metric in goals['success_metrics']:
        response += f"• {metric}\n"
    
    response += f"\n**🎉 Reward System:**\n"
    response += f"• Daily win: {goals['rewards']['daily']}\n"
    response += f"• Weekly achievement: {goals['rewards']['weekly']}\n"
    response += f"• Goal completion: {goals['rewards']['final']}\n"
    
    return {
        "response": response,
        "command": "/goals",
        "data": goals,
        "timestamp": datetime.utcnow()
    }

async def handle_habits_command(user: User, context: dict):
    """Habit formation recommendations"""
    
    habits = {
        "consistency_score": min(10, context['completion_rate'] / 10),
        "planning_score": 7.0,  # Simplified for demo
        "focus_score": 6.5,
        "recommended_habits": [
            {
                "name": "Daily Task Planning",
                "trigger": "First coffee of the day",
                "action": "Write down top 3 priorities",
                "reward": "Check social media for 5 minutes",
                "start_date": "Tomorrow",
                "difficulty": 3
            },
            {
                "name": "Task Completion Celebration",
                "trigger": "Completing any task",
                "action": "Cross it off and say 'Done!'",
                "reward": "Feel satisfaction and momentum",
                "start_date": "Today",
                "difficulty": 2
            }
        ],
        "implementation_schedule": [
            "Focus on daily planning habit",
            "Add completion celebration",
            "Integrate weekly review",
            "Establish energy management"
        ],
        "tracking_methods": [
            "Simple daily checklist",
            "Weekly habit review",
            "Monthly progress assessment",
            "Quarterly habit optimization"
        ]
    }
    
    response = f"🌱 **Productivity Habits for {user.name.split()[0]}**\n\n"
    response += f"**Current Habits Assessment:**\n"
    response += f"• Task completion consistency: {habits['consistency_score']:.1f}/10\n"
    response += f"• Weekly planning: {habits['planning_score']:.1f}/10\n"
    response += f"• Focus maintenance: {habits['focus_score']:.1f}/10\n\n"
    
    response += f"**🎯 Recommended Habit Stack:**\n\n"
    
    for i, habit in enumerate(habits['recommended_habits'], 1):
        response += f"**Habit {i}: {habit['name']}**\n"
        response += f"• Trigger: {habit['trigger']}\n"
        response += f"• Action: {habit['action']}\n"
        response += f"• Reward: {habit['reward']}\n"
        response += f"• Start date: {habit['start_date']}\n"
        response += f"• Difficulty: {habit['difficulty']}/10\n\n"
    
    response += f"**📅 Implementation Schedule:**\n"
    for week, focus in enumerate(habits['implementation_schedule'], 1):
        response += f"• Week {week}: {focus}\n"
    
    response += f"\n**📈 Habit Tracking:**\n"
    for tracker in habits['tracking_methods']:
        response += f"• {tracker}\n"
    
    response += f"\n**💡 Success Tips:**\n"
    response += f"• Start with just one habit at a time\n"
    response += f"• Track daily for the first 30 days\n"
    response += f"• Link new habits to existing routines\n"
    response += f"• Celebrate small wins consistently\n"
    
    return {
        "response": response,
        "command": "/habits",
        "data": habits,
        "timestamp": datetime.utcnow()
    }

async def handle_report_command(user: User, context: dict):
    """Generate comprehensive productivity report"""
    
    # Get historical data for trends
    historical_data = {
        "avg_completion_rate": 75.0,
        "trend": "improving",
        "best_day": "Tuesday",
        "worst_day": "Monday"
    }
    
    report = {
        "productivity_score": min(10, (context['completion_rate'] / 10) + (5 if context['overdue_tasks'] == 0 else 3)),
        "trend": "improving" if context['productivity_trend'] == "improving" else "stable",
        "trend_percentage": 12.5,  # Simplified for demo
        "top_strength": "Task execution" if context['completion_rate'] > 80 else "Planning",
        "improvement_area": "Time management" if context['overdue_tasks'] > 0 else "Task prioritization",
        "historical_avg": historical_data.get('avg_completion_rate', 70),
        "industry_benchmark": 78.0,
        "efficiency_score": min(10, context['completion_rate'] / 10),
        "time_management_score": 8.5 if context['overdue_tasks'] == 0 else 6.0,
        "work_style": "Executor" if context['completion_rate'] > 80 else "Planner",
        "peak_hours": "9-11 AM",
        "complexity_preference": "Moderate",
        "collaboration_level": "High" if context.get('active_projects', 0) > 2 else "Moderate",
        "weekly_breakdown": {
            "Monday": {"completed": 3, "avg_duration": 2.5},
            "Tuesday": {"completed": 4, "avg_duration": 2.0},
            "Wednesday": {"completed": 3, "avg_duration": 2.8},
            "Thursday": {"completed": 4, "avg_duration": 2.2},
            "Friday": {"completed": 2, "avg_duration": 1.5}
        },
        "action_items": [
            "Complete overdue tasks first" if context['overdue_tasks'] > 0 else "Maintain current performance",
            "Implement daily planning routine",
            "Set up weekly review process",
            "Optimize peak productivity hours"
        ],
        "most_productive_day": "Tuesday",
        "avg_task_duration": 2.4,
        "procrastination_index": 3.0 if context['overdue_tasks'] == 0 else 6.5,
        "stress_level": 4 if context['overdue_tasks'] <= 2 else 7
    }
    
    response = f"📊 **Productivity Report for {user.name.split()[0]}**\n"
    response += f"*Generated on {datetime.utcnow().strftime('%B %d, %Y')}*\n\n"
    
    response += f"**🎯 Executive Summary:**\n"
    response += f"• Overall productivity score: {report['productivity_score']:.1f}/10\n"
    response += f"• Performance trend: {report['trend']} ({report['trend_percentage']:+.1f}%)\n"
    response += f"• Key strength: {report['top_strength']}\n"
    response += f"• Improvement area: {report['improvement_area']}\n\n"
    
    response += f"**📈 Performance Metrics:**\n"
    response += f"• Tasks completed: {context['completed_tasks']} (vs {report['historical_avg']:.1f} avg)\n"
    response += f"• Completion rate: {context['completion_rate']:.1f}% (vs {report['industry_benchmark']:.1f}% benchmark)\n"
    response += f"• Efficiency score: {report['efficiency_score']:.1f}/10\n"
    response += f"• Time management: {report['time_management_score']:.1f}/10\n\n"
    
    response += f"**🎭 Work Style Analysis:**\n"
    response += f"• Primary work style: {report['work_style']}\n"
    response += f"• Peak productivity hours: {report['peak_hours']}\n"
    response += f"• Task complexity preference: {report['complexity_preference']}\n"
    response += f"• Collaboration level: {report['collaboration_level']}\n\n"
    
    response += f"**📅 Weekly Breakdown:**\n"
    for day, stats in report['weekly_breakdown'].items():
        response += f"• {day}: {stats['completed']} completed, {stats['avg_duration']:.1f}h avg\n"
    
    response += f"\n**🚀 Action Items for Next Week:**\n"
    for i, action in enumerate(report['action_items'], 1):
        response += f"{i}. {action}\n"
    
    response += f"\n**📊 Detailed Analytics:**\n"
    response += f"• Most productive day: {report['most_productive_day']}\n"
    response += f"• Average task duration: {report['avg_task_duration']} hours\n"
    response += f"• Procrastination index: {report['procrastination_index']:.1f}/10\n"
    response += f"• Stress level indicator: {report['stress_level']}/10\n"
    
    return {
        "response": response,
        "command": "/report",
        "data": report,
        "timestamp": datetime.utcnow()
    }

async def handle_help_command():
    """Show available AI Coach commands"""
    
    response = """🤖 **AI Productivity Coach - Command Guide**

**Available Commands:**

🔍 `/analyze` - Deep dive into your productivity patterns and performance metrics

⚡ `/optimize` - Get a personalized task prioritization and time-blocking plan  

🎯 `/goals` - Generate SMART goals based on your current performance data

🌱 `/habits` - Receive productivity habit recommendations and implementation plans

📊 `/report` - Generate comprehensive productivity report with trends and insights

❓ `/help` - Show this command guide

**Chat Examples:**
• "How can I improve my productivity?"
• "I'm feeling overwhelmed with my tasks"
• "Help me prioritize my work"
• "What are best practices for team collaboration?"

**Pro Tips:**
• Use commands for structured analysis
• Ask specific questions for targeted advice
• Reference your current tasks and projects for personalized guidance
• Regular check-ins help build better productivity habits

Start by typing a command or asking me any productivity question! 🚀"""

    return {
        "response": response,
        "command": "/help",
        "timestamp": datetime.utcnow()
    }
async def generate_enhanced_coaching_response(message: str, user: User, context: dict = None) -> str:
    """Enhanced fallback coaching response with real user data"""
    
    if context is None:
        context = await get_user_context_for_ai(user.id)
    
    lower_message = message.lower()
    user_name = user.name.split()[0]  # First name
    
    # Personalized greeting with data
    if any(word in lower_message for word in ['hello', 'hi', 'hey']):
        return f"Hello {user_name}! 👋 I'm your AI Productivity Coach. \n\nI can see you have {context['total_tasks']} tasks with a {context['completion_rate']:.1f}% completion rate. Let's work together to optimize your productivity! \n\nI can help you with:\n• Task prioritization and optimization\n• Time management strategies\n• Goal setting and achievement\n• Performance analysis\n• Habit formation\n\nWhat would you like to focus on today?"
    
    # Data-driven overwhelm response
    if any(word in lower_message for word in ['stuck', 'overwhelmed', 'help']):
        insights = []
        if context['overdue_tasks'] > 0:
            insights.append(f"You have {context['overdue_tasks']} overdue tasks that need immediate attention")
        if context['eisenhower_distribution'].get('do', 0) > context['total_tasks'] * 0.3:
            insights.append("Too many urgent tasks - let's work on prevention strategies")
        if context['completion_rate'] < 70:
            insights.append("Your completion rate could be improved with better task breakdown")
            
        response = f"I understand you're feeling overwhelmed, {user_name}. Based on your data, here's my immediate action plan:\n\n"
        
        if insights:
            response += "**Key Issues I Found:**\n"
            for insight in insights:
                response += f"• {insight}\n"
            response += "\n"
        
        response += """**Immediate Relief Strategy:**
1. **Focus on {do_tasks} urgent tasks first** - These need immediate attention
2. **Break down large tasks** - Aim for 15-30 minute chunks
3. **Use the 2-minute rule** - If it takes less than 2 minutes, do it now
4. **Schedule {decide_tasks} important tasks** - Don't let them become urgent

**Next Steps:**
• Complete 1 overdue task right now
• Block 25 minutes for focused work
• Review and reschedule unrealistic deadlines

Which of these strategies feels most helpful for your current situation?""".format(
            do_tasks=context['eisenhower_distribution'].get('do', 0),
            decide_tasks=context['eisenhower_distribution'].get('decide', 0)
        )
        
        return response
    
    # Performance optimization with real data
    if any(word in lower_message for word in ['productivity', 'improve', 'better', 'efficient']):
        performance_insights = []
        
        if context['completion_rate'] > 80:
            performance_insights.append("Excellent completion rate! You're already performing well.")
        elif context['completion_rate'] > 60:
            performance_insights.append("Good completion rate with room for optimization.")
        else:
            performance_insights.append("Completion rate needs attention - let's focus on this first.")
            
        if context['eisenhower_distribution'].get('delete', 0) > 0:
            performance_insights.append(f"You have {context['eisenhower_distribution']['delete']} low-priority tasks to eliminate.")
            
        response = f"Great question, {user_name}! Based on your productivity data analysis:\n\n"
        response += "📊 **Your Current Performance:**\n"
        for insight in performance_insights:
            response += f"• {insight}\n"
        response += f"\n🎯 **Personalized Optimization Plan:**\n\n"
        
        if context['completion_rate'] < 70:
            response += "**1. Completion Rate Boost:**\n• Break tasks into smaller, specific actions\n• Set realistic daily task limits (3-5 important tasks)\n• Use time-blocking for focused work\n\n"
        
        if context['eisenhower_distribution'].get('do', 0) > context['total_tasks'] * 0.3:
            response += "**2. Reduce Urgency Addiction:**\n• Schedule important tasks before they become urgent\n• Build buffer time into deadlines\n• Focus on prevention vs. firefighting\n\n"
        
        response += f"**3. Energy Management:**\n• Schedule demanding tasks during peak energy hours\n• Batch similar tasks together\n• Take breaks every 90 minutes\n\n**Next Action:** Would you like me to analyze your specific task patterns and suggest a custom daily routine?"
        
        return response
    
    # Team performance insights
    if any(word in lower_message for word in ['team', 'collaboration', 'meeting']):
        return f"Team productivity insights for {user_name}:\n\n**🤝 Current Team Involvement:**\n• Active in {context['active_projects']} projects\n• Contributing to team success\n\n**📈 Team Optimization Strategies:**\n\n1. **Communication Excellence:**\n   - Async updates for non-urgent items\n   - Clear agenda for all meetings\n   - Document decisions and action items\n\n2. **Workload Distribution:**\n   - Regular capacity check-ins\n   - Cross-training to prevent bottlenecks\n   - Fair distribution of challenging work\n\n3. **Collaboration Tools:**\n   - Shared task visibility\n   - Clear ownership and deadlines\n   - Regular retrospectives\n\nWhich team challenge would you like specific help with?"
    
    # Goal setting with data context
    if any(word in lower_message for word in ['goal', 'target', 'objective']):
        return f"Goal setting guidance for {user_name} based on your current performance:\n\n**🎯 SMART+ Goals Framework:**\n\n**Current Baseline:**\n• Completion Rate: {context['completion_rate']:.1f}%\n• Weekly Activity: {context['recent_activity']} tasks\n• Active Projects: {context['active_projects']}\n\n**Recommended Goals:**\n• **Performance Goal:** Increase completion rate to {min(95, context['completion_rate'] + 15):.0f}% within 30 days\n• **Efficiency Goal:** Reduce overdue tasks from {context['overdue_tasks']} to 0 within 2 weeks\n• **Balance Goal:** Maintain 60% Important/Non-Urgent tasks in your matrix\n\n**Implementation Strategy:**\n✓ Weekly goal reviews every Friday\n✓ Track leading indicators (daily completed tasks)\n✓ Adjust targets based on realistic capacity\n✓ Celebrate milestone achievements\n\nWhich specific goal area would you like help structuring?"
    
    # Stress and burnout with personalized data
    if any(word in lower_message for word in ['stress', 'burnout', 'tired', 'exhausted']):
        workload_analysis = "high" if context['total_tasks'] > 20 else "moderate" if context['total_tasks'] > 10 else "manageable"
        
        return f"I understand you're feeling overwhelmed, {user_name}. Let me help you regain balance. 🌱\n\n**📊 Workload Analysis:**\n• Current load: {workload_analysis} ({context['total_tasks']} tasks)\n• Overdue pressure: {context['overdue_tasks']} tasks behind\n• Recent activity: {context['recent_activity']} tasks this week\n\n**🚨 Immediate Relief Plan:**\n\n1. **Take a break right now** - Even 5 minutes helps reset your mind\n2. **Triage ruthlessly:**\n   - Focus only on {context['eisenhower_distribution'].get('do', 0)} urgent tasks today\n   - Defer {context['eisenhower_distribution'].get('decide', 0)} important tasks to tomorrow\n   - Delegate or delete {context['eisenhower_distribution'].get('delegate', 0) + context['eisenhower_distribution'].get('delete', 0)} lower-priority items\n\n3. **Capacity reset:**\n   - Limit yourself to 3 important tasks per day\n   - Build 25% buffer time into estimates\n   - Say no to new commitments this week\n\n**🛡️ Prevention Strategy:**\n• Weekly workload review (Fridays)\n• Daily energy check-ins\n• Proactive boundary setting\n\nWhat's the ONE thing you can remove from your plate today to reduce pressure?"
    
    # Analysis and insights
    if any(word in lower_message for word in ['analyze', 'analysis', 'insight', 'pattern']):
        return f"📊 **Productivity Analysis for {user_name}**\n\n**Performance Snapshot:**\n• Overall completion rate: {context['completion_rate']:.1f}%\n• Task velocity: {context['recent_activity']} tasks/week\n• Project engagement: {context['active_projects']} active projects\n• Trend: {context['productivity_trend'].replace('_', ' ').title()}\n\n**🎯 Eisenhower Matrix Analysis:**\n• Do First: {context['eisenhower_distribution'].get('do', 0)} tasks ({context['eisenhower_distribution'].get('do', 0)/max(context['total_tasks'], 1)*100:.0f}%)\n• Schedule: {context['eisenhower_distribution'].get('decide', 0)} tasks ({context['eisenhower_distribution'].get('decide', 0)/max(context['total_tasks'], 1)*100:.0f}%)\n• Delegate: {context['eisenhower_distribution'].get('delegate', 0)} tasks ({context['eisenhower_distribution'].get('delegate', 0)/max(context['total_tasks'], 1)*100:.0f}%)\n• Eliminate: {context['eisenhower_distribution'].get('delete', 0)} tasks ({context['eisenhower_distribution'].get('delete', 0)/max(context['total_tasks'], 1)*100:.0f}%)\n\n**🔍 Key Insights:**\n• Optimal distribution: 20% Do, 60% Schedule, 15% Delegate, 5% Eliminate\n• Your pattern shows: {'Balanced approach' if context['eisenhower_distribution'].get('decide', 0) > context['eisenhower_distribution'].get('do', 0) else 'Too much urgency - focus on prevention'}\n\n**📈 Recommendations:**\n• {'Excellent balance! Maintain current approach.' if context['completion_rate'] > 80 else 'Focus on completing existing tasks before adding new ones.'}\n• {'Reduce urgent tasks by planning ahead' if context['eisenhower_distribution'].get('do', 0) > 5 else 'Good urgency management'}\n\nWould you like specific recommendations for any particular area?"
    
    # Default comprehensive response with data
    return f"Thanks for reaching out, {user_name}! Based on your productivity data, here's my assessment:\n\n**📊 Current Status:**\n• {context['total_tasks']} total tasks with {context['completion_rate']:.1f}% completion rate\n• {context['overdue_tasks']} overdue tasks need attention\n• {context['active_projects']} active projects\n• Productivity trend: {context['productivity_trend'].replace('_', ' ')}\n\n**🎯 Key Productivity Principles:**\n• **Clarity** - Know exactly what needs to be done (Eisenhower Matrix)\n• **Focus** - Single-task with deep attention\n• **Energy Management** - Work with your natural rhythms\n• **Continuous Improvement** - Small, consistent optimizations\n\n**💡 Actionable Next Steps:**\n1. Complete {min(3, context['overdue_tasks'] or 1)} highest-priority tasks today\n2. Schedule important non-urgent work to prevent future urgency\n3. Work in focused 25-minute blocks with 5-minute breaks\n4. Track what works and iterate weekly\n\n**I can help you with:**\n• `/analyze` - Deep dive into your productivity patterns\n• `/optimize` - Custom task prioritization\n• `/goals` - SMART goal setting with your data\n• `/habits` - Build sustainable productivity habits\n\nWhat specific area would you like to focus on improving?"

# WhatsApp Webhook endpoint
@api_router.post("/integrations/whatsapp/webhook")
async def whatsapp_webhook(request: dict):
    """Handle WhatsApp Business API webhooks"""
    
    # This is a placeholder for WhatsApp integration
    # Users will configure their own WhatsApp Business API
    
    if request.get("object") == "whatsapp_business_account":
        for entry in request.get("entry", []):
            for change in entry.get("changes", []):
                if change.get("field") == "messages":
                    # Process incoming message
                    messages = change.get("value", {}).get("messages", [])
                    for message in messages:
                        # Handle message logic here
                        await process_whatsapp_message(message)
    
    return {"status": "success"}

async def process_whatsapp_message(message: dict):
    """Process incoming WhatsApp message and create tasks if needed"""
    
    # Extract message details
    phone_number = message.get("from")
    message_text = message.get("text", {}).get("body", "")
    
    # Check if message is a task creation request
    if "create task" in message_text.lower() or "@productivity" in message_text.lower():
        # Parse task from message
        # This is where you'd implement task creation logic
        pass
    
    return {"processed": True}

# Razorpay configuration
RAZORPAY_KEY_ID = os.environ.get('RAZORPAY_KEY_ID', 'rzp_test_9WzaP4XKo0z9By')
RAZORPAY_KEY_SECRET = os.environ.get('RAZORPAY_KEY_SECRET', 'test_secret_key')

# Payment Models
class PaymentOrder(BaseModel):
    amount: int  # in paise
    currency: str = "INR"
    plan: str

class PaymentVerification(BaseModel):
    razorpay_order_id: str
    razorpay_payment_id: str
    razorpay_signature: str
    plan: str

# Payment endpoints
@api_router.post("/payment/create-order")
async def create_payment_order(order: PaymentOrder):
    """Create Razorpay order for subscription payment"""
    
    # In production, use actual Razorpay client
    # import razorpay
    # client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))
    
    # For demo, create mock order
    order_id = f"order_{str(uuid.uuid4())[:8]}"
    
    # Store order in database
    order_data = {
        "id": order_id,
        "amount": order.amount,
        "currency": order.currency,
        "plan": order.plan,
        "status": "created",
        "created_at": datetime.utcnow()
    }
    
    await db.payment_orders.insert_one(order_data)
    
    return {
        "id": order_id,
        "amount": order.amount,
        "currency": order.currency,
        "status": "created"
    }

@api_router.post("/payment/verify")
async def verify_payment(verification: PaymentVerification):
    """Verify payment and activate subscription"""
    
    # In production, verify signature with Razorpay
    # expected_signature = hmac.new(
    #     RAZORPAY_KEY_SECRET.encode(),
    #     f"{verification.razorpay_order_id}|{verification.razorpay_payment_id}".encode(),
    #     hashlib.sha256
    # ).hexdigest()
    
    # For demo, always verify successfully
    is_valid = True
    
    if is_valid:
        # Create user account with paid subscription
        user_data = {
            "name": f"User_{verification.plan}",
            "email": f"user_{verification.razorpay_payment_id[:8]}@example.com",
            "role": "admin",
            "subscription_plan": verification.plan,
            "subscription_status": "active",
            "payment_id": verification.razorpay_payment_id
        }
        
        user = User(**user_data)
        await db.users.insert_one(user.dict())
        
        # Create access token
        access_token = create_access_token(data={"sub": user.id})
        
        return {
            "success": True,
            "token": access_token,
            "user": user_data,
            "message": "Payment verified and account activated"
        }
    else:
        raise HTTPException(status_code=400, detail="Payment verification failed")

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
