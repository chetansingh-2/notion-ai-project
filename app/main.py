from fastapi import FastAPI, HTTPException
from app.services.notion_service import NotionService
from app.services.task_processor import TaskProcessor
from app.services.scheduler_service import SchedulerService
from pydantic import BaseModel
from datetime import datetime

app = FastAPI()
notion_service = NotionService()
task_processor = TaskProcessor()
scheduler = SchedulerService()

class Task(BaseModel):
    title: str
    due_date: str = None
    priority: str = "Medium"

class TaskUpdate(BaseModel):
    status: str

class TextInput(BaseModel):
    text: str

@app.post("/process-text")
async def process_text_to_task(text_input: TextInput):
    try:
        result = await scheduler.create_task_from_text(text_input.text)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/process-deletion")
async def process_deletion(text_input: TextInput):
    try:
        result = await scheduler.task_deletion(text_input.text)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/reschedule-task")
async def rescheduler(text_input:TextInput):
    try:
        result = await scheduler.reschedule_task(text_input.text)
        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
