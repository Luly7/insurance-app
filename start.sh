#!/bin/bash
cd ~/insurance_app
source ~/venv/bin/activate
kill $(lsof -ti :8000) 2>/dev/null
sleep 1
nohup uvicorn main:app --host 0.0.0.0 --port 8000 > app.log 2>&1 &
echo "✅ Insurance app started!"
echo "📱 Open: http://100.66.232.87:8000"
