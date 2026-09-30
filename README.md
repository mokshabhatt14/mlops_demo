# Taskroom: Learn FastAPI

FastAPI is a Python tool that lets a web page talk to a Python program. In this little task list, the page sends a message and the program sends an answer back.

## Run it

```bash
python -m pip install -r requirements.txt
python -m uvicorn app:app --reload
```

Open `http://127.0.0.1:8000` for the task list. Add a task or tick its box, then look at the right-hand panel to see the message and answer. FastAPI's API guide is at `http://127.0.0.1:8000/docs`.

## Two messages

- `GET /api/tasks` asks, "What tasks do I have?"
- `PUT /api/tasks/{task_id}` tells the app to save a task. Its message looks like `{"title":"Read a book","completed":false}`.

Tasks are practice data. They go away when the app stops.