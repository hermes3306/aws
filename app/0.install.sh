sudo apt update -y
sudo apt install nginx 
sudo systemctl start nginx 
sudo systemctl enable nginx
sudo systemctl status nginx

sudo apt install python3-pip
sudo apt install python3-venv

python3 -m venv myenv
source myenv/bin/activate
pip install flask, psycopg2
pip install psycopg2-binary
pip install flask_cors

sudo apt install postgresql-client  -y
sudo apt install libpq-dev python3-dev -y
