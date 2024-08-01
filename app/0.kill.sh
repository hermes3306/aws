pids=$(sudo ps aux | grep python |  awk '{print $2}')
if [ -n "$pids" ]; then
    echo "Killing processes: $pids"
    sudo kill $pids
else
    echo "No Python processes running found."
fi

pids=$(sudo ps aux | grep gunicorn |  awk '{print $2}')
if [ -n "$pids" ]; then
    echo "Killing processes: $pids"
    sudo kill $pids
else
    echo "No guincorn running found."
fi
