#!/bin/bash
./0.kill.sh
python3 app.py &
gunicorn -w 4 -b 127.0.0.1:5000 app:app &
