from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"

app = FastAPI(
    title="Taskroom API",
    description="A tiny task app for learning how a web page talks to a Python program.",
    version="1.0.2",
)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/health", tags=["Health"], summary="Check whether the API is running")
def health():
    return {"status": "ok"}


@app.get("/api/version", tags=["Health"], summary="Get the app version")
def get_version():
    return {"name": app.title, "version": app.version}


class TaskInput(BaseModel):
    title: str = Field(min_length=1, max_length=80, strip_whitespace=True, description="The task to save.")
    completed: bool = Field(default=False, description="True when the task is finished.")


class Task(TaskInput):
    id: int = Field(description="The task's number.")


tasks: dict[int, Task] = {
    1: Task(id=1, title="Pack my school bag", completed=True),
    2: Task(id=2, title="Read a funny book"),
    3: Task(id=3, title="Draw a picture"),
}


@app.get("/", include_in_schema=False)
def home():
    return FileResponse(STATIC_DIR / "index.html")


@app.get(
    "/api/tasks",
    response_model=list[Task],
    tags=["Tasks"],
    summary="Ask to see all tasks",
    description="GET asks the app to send back the whole task list.",
)
def list_tasks():
    return sorted(tasks.values(), key=lambda task: task.id)


@app.put(
    "/api/tasks/{task_id}",
    response_model=Task,
    tags=["Tasks"],
    summary="Tell the app to save a task",
    description="PUT sends a task to save. It can add a new task or replace one with the same number.",
)
def save_task(task_id: int, task_input: TaskInput):
    task = Task(id=task_id, **task_input.model_dump())
    tasks[task_id] = task
    return task