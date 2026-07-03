import sqlite3
from pathlib import Path


def save_jobs_to_db(jobs: list[dict], db_path: str | Path) -> tuple[int, int]:
    path = Path(db_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with sqlite3.connect(path) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS jobs (
                title TEXT,
                company TEXT,
                location TEXT,
                UNIQUE(title, company, location)
            )
            """
        )

        inserted = 0
        skipped = 0
        for job in jobs:
            cursor = conn.execute(
                """
                INSERT OR IGNORE INTO jobs (title, company, location)
                VALUES (?, ?, ?)
                """,
                (job["title"], job["company"], job["location"]),
            )
            if cursor.rowcount == 1:
                inserted += 1
            else:
                skipped += 1

    return inserted, skipped
