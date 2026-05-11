import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
os.environ.setdefault("DATABASE_URL", f"sqlite:///{PROJECT_ROOT / 'backend' / 'ad_quality.db'}")
sys.path.insert(0, str(PROJECT_ROOT / "backend"))

from app.database import Base, engine
from app import models  # noqa: F401


def main() -> None:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    print("Database reset complete.")


if __name__ == "__main__":
    main()
