#!/bin/bash
export MONGO_URI=mongodb://${mongo_uri}:27017/
export MONGO_DB_NAME=${mongo_db_name}
sudo yum update -y
sudo yum install -y python3 git
git clone https://github.com/andresm9/btg.git /home/ec2-user/app
cd /home/ec2-user/app
pip3 install "fastapi[standard]"
pip3 install --no-cache-dir --upgrade -r requirements.txt
fastapi run app/main.py --proxy-headers --port 80