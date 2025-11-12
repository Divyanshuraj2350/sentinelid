
import sys
sys.path.insert(0, '/Users/divyanshu23/Desktop/SentinelID/backend')

from app import app, db

print("🔄 Initializing database...")

with app.app_context():
    db.create_all()
    print("✅ Database created successfully!")
    print("📁 Location: instance/sentinelid.db")

