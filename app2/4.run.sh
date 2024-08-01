#!/bin/bash
./0.kill.sh
source myenv/bin/activate
python3 app.py &
#gunicorn -w 4 -b 127.0.0.1:5000 app:app &
