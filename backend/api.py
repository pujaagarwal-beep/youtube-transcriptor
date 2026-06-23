from fastapi import FastAPI, BackgroundTasks
import threading

from sheets_sync import main as run_sync  # reuse your existing logic

app = FastAPI()

# simple lock to avoid multiple runs at once
lock = threading.Lock()


@app.get("/")
def home():
    return {"status": "ok", "message": "Sheets Sync API is running"}


@app.post("/run-sync")
def run_sync_route(background_tasks: BackgroundTasks):
    """
    Trigger sheet sync manually.
    Runs in background so API doesn't hang.
    """

    if lock.locked():
        return {"status": "busy", "message": "Sync already running"}

    def task():
        with lock:
            run_sync()

    background_tasks.add_task(task)

    return {"status": "started", "message": "Sheet sync started"}