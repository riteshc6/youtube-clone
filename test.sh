#! /bin/bash
sudo apt update
sudo apt install python3-pip
sudo apt install postgresql
sudo apt install nano
sudo apt-get install python3-venv
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt
sudo apt install redis
sudo apt install nginx
sudo apt install gunicorn
flask db migrate
flask db init
flask db migrate
sudo apt-get install python-psycopg2
flask db upgrade
sudo bash -c 'cat > \.env <<EOF
DATABASE_URL='postgresql://ritesh:ritesh@127.0.0.1:5432/youtube'
ELASTICSEARCH_URL='https://f069c30c3cb14cdea0d99bff5edb320f.us-west1.gcp.cloud.es.io:9243/'
ELASTIC_USER = 'elastic'
ELASTIC_PASSWORD = 'jxhGL9smUvkxFLEWr4ErzjaR'
EOF
'
gunicorn youtube:app -b localhost:8000 &
sudo bash -c 'cat >  /etc/nginx/conf.d/virtual.conf << EOF
server {
    listen       80;
    server_name  13.233.31.67;

    location / {
        proxy_pass http://127.0.0.1:8000;
    }
}
client_max_body_size 20M;
EOF
'
sudo bash -c 'cat > /etc/systemd/system/testing.service
[Unit]
Description=Youtube web application
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/youtube
ExecStart=/home/ubuntu/youtube/venv/bin/gunicorn -b localhost:8000 -w 4 youtube:app
Environment=FLASK_CONFIG=production
Environment=DATABASE_URL=postgresql://postgres:postgres@youtube.clejaeyrxoaa.ap-south-1.rds.amazonaws.com
Restart=always

[Install]
WantedBy=multi-user.target
EOF
'
sudo nginx -t
sudo service nginx restart
sudo systemctl daemon-reload
sudo systemctl start youtube
sudo bash -c 'cat > /etc/systemd/system/worker.service << EOF
[Unit]
Description=Youtube task worker
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/youtube
ExecStart=/home/ubuntu/youtube/venv/bin/celery -A app.celery worker
Environment=FLASK_CONFIG=production
Environment=DATABASE_URL=postgresql://postgres:postgres@youtube.clejaeyrxoaa.ap-south-1.rds.amazonaws.com
Restart=always

[Install]
WantedBy=multi-user.target
EOF
'
sudo systemctl daemon-reload
sudo systemctl status celery