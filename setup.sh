
#!/bin/bash

echo "🛡️ SentinelID Setup Script"

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

cd backend
python3 << 'PYEOF'
from database import db, app
with app.app_context():
    db.create_all()
print("✅ Database initialized!")
PYEOF

cd ..

echo "✅ Setup complete!"
echo ""
echo "Terminal 1: cd backend && python app.py"
echo "Terminal 2: cd frontend && python -m http.server 8000"
