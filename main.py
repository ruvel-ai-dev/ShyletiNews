from app import app
from scheduler import start_background_scheduler

if __name__ == "__main__":
    start_background_scheduler()
    app.run(host="0.0.0.0", port=5000, debug=True)
