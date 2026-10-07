# Taskroom: Learn FastAPI

FastAPI is a Python tool that lets a web page talk to a Python program. In this little task list, the page sends a message and the program sends an answer back.

## Run it

```bash
python -m pip install -r requirements.txt
python -m uvicorn app:app --reload
```

Open `http://127.0.0.1:8000` for the task list. Add a task or tick its box, then look at the right-hand panel to see the message and answer. FastAPI's API guide is at `http://127.0.0.1:8000/docs`.

## Publish the Docker image

When you push a commit to GitHub, the workflow builds the Docker image and pushes it to Docker Hub as `moksha087/taskroom:latest` and with a tag for that commit. It runs for pushes to any branch.

Before the first push, add these repository secrets under **Settings > Secrets and variables > Actions**:

- `DOCKERHUB_USERNAME`: your Docker Hub username.
- `DOCKERHUB_TOKEN`: a Docker Hub access token.

Find the build result in the repository's **Actions** tab. Saving changes locally does not start a build; commit and push them to GitHub.

To run the published image locally:

```bash
docker pull moksha087/taskroom:latest
docker run --rm -p 8000:8000 moksha087/taskroom:latest
```

Then open `http://127.0.0.1:8000`.

## Two messages

- `GET /api/tasks` asks, "What tasks do I have?"
- `PUT /api/tasks/{task_id}` tells the app to save a task. Its message looks like `{"title":"Read a book","completed":false}`.

Tasks are practice data. They go away when the app stops.