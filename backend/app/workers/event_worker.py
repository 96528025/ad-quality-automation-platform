import time

from app.database import SessionLocal
from app.services.event_pipeline import process_pending_events


def run_worker(poll_interval_seconds: float = 1.0, batch_size: int = 100) -> None:
    while True:
        db = SessionLocal()
        try:
            process_pending_events(db, limit=batch_size)
        finally:
            db.close()
        time.sleep(poll_interval_seconds)


if __name__ == "__main__":
    run_worker()
