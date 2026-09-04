"""
reset_database.py
------------------
Cleans the SQLite database and deletes uploaded files so you can test
GeMGuard AI completely from scratch (from basic).

Run: python reset_database.py
"""
import os
import shutil
import sqlite3

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.join(BASE_DIR, "Backend")
DB_PATH = os.path.join(BACKEND_DIR, "gem_compliance.db")
UPLOADS_DIR = os.path.join(BACKEND_DIR, "uploads")


def clean_project():
    print("[CLEAN] Cleaning GeMGuard AI database and uploads for clean testing...\n")

    # 1. Reset SQLite Database
    if os.path.exists(DB_PATH):
        try:
            # Connect and delete all table rows
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()

            # Get table names
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = [row[0] for row in cursor.fetchall() if not row[0].startswith("sqlite_")]

            for table in tables:
                cursor.execute(f"DELETE FROM {table};")
                print(f"  OK: Cleared table {table}")

            conn.commit()
            conn.close()
            print(f"  OK: Database {DB_PATH} reset successfully.")
        except Exception as e:
            print(f"  WARNING: Could not clear DB rows directly ({e}), deleting DB file...")
            try:
                os.remove(DB_PATH)
                print(f"  OK: Deleted database file {DB_PATH}")
            except Exception as del_err:
                print(f"  ERROR: Could not delete DB file: {del_err}")

    # 2. Clear uploads folder
    if os.path.exists(UPLOADS_DIR):
        for item in os.listdir(UPLOADS_DIR):
            item_path = os.path.join(UPLOADS_DIR, item)
            try:
                if os.path.isfile(item_path):
                    os.remove(item_path)
                elif os.path.isdir(item_path):
                    shutil.rmtree(item_path)
            except Exception as e:
                print(f"  WARNING: Could not remove upload item {item}: {e}")
        print(f"  OK: Cleared all files from {UPLOADS_DIR}")
    else:
        os.makedirs(UPLOADS_DIR, exist_ok=True)
        print(f"  OK: Created fresh uploads directory.")

    print("\nSUCCESS: Clean-up complete! You now have a 100% fresh database to test from basic.")


if __name__ == "__main__":
    clean_project()
