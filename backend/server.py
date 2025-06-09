from fastapi import FastAPI, APIRouter, HTTPException
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

class UserCreate(BaseModel):
    name: str
    email: str
    role: str = "team_member"

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
async def create_user(user_data: UserCreate):
    user = User(**user_data.dict())
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
