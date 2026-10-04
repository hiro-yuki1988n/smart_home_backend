# test_db.py
from app.db.postgres import init_db
from app.db.base import Base

def test():
    init_db()
    print("Tables found:", Base.metadata.tables.keys())

if __name__ == "__main__":
    test()
