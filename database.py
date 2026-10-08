import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "garbage360.db"


def get_connection():
    conn = sqlite3.connect(DB_PATH, timeout=10.0)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    try:
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT NOT NULL,
                description TEXT NOT NULL,
                location TEXT NOT NULL,
                latitude REAL,
                longitude REAL,
                image_hash TEXT,
                image_name TEXT,
                category TEXT NOT NULL,
                severity TEXT NOT NULL,
                priority TEXT NOT NULL,
                drain_risk TEXT NOT NULL,
                confidence REAL NOT NULL,
                recommended_action TEXT NOT NULL,
                analysis_mode TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'Reported'
            )
            """
        )
        conn.commit()
    finally:
        conn.close()


def insert_report(data: dict) -> int:
    from datetime import datetime, timezone

    conn = get_connection()
    try:
        cur = conn.execute(
            """
            INSERT INTO reports (
                created_at, description, location, latitude, longitude,
                image_hash, image_name, category, severity, priority,
                drain_risk, confidence, recommended_action, analysis_mode, status
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                datetime.now(timezone.utc).isoformat(),
                data["description"],
                data["location"],
                data.get("latitude"),
                data.get("longitude"),
                data.get("image_hash"),
                data.get("image_name"),
                data["category"],
                data["severity"],
                data["priority"],
                data["drain_risk"],
                data["confidence"],
                data["recommended_action"],
                data["analysis_mode"],
                "Reported",
            ),
        )
        conn.commit()
        report_id = cur.lastrowid
        return report_id
    finally:
        conn.close()


def fetch_reports():
    conn = get_connection()
    try:
        rows = conn.execute(
            "SELECT * FROM reports ORDER BY id DESC"
        ).fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()


def update_report_status(report_id: int, status: str):
    conn = get_connection()
    try:
        conn.execute(
            "UPDATE reports SET status = ? WHERE id = ?",
            (status, report_id),
        )
        conn.commit()
    finally:
        conn.close()


def report_stats(reports):
    reports = reports or []
    return {
        "total": len(reports),
        "open": sum(r.get("status") != "Resolved" for r in reports),
        "critical": sum(r.get("priority") == "P1" for r in reports),
        "resolved": sum(r.get("status") == "Resolved" for r in reports),
    }

