sudo apt install mysql-server

sudo systemctl start mysql

sudo systemctl enable mysql

sudo mysql

pip install mysql-connector-python

pydantic_settings

pip3 install sqlalchemy

sudo apt update

sudo apt install redis-server

sudo systemctl start redis

sudo systemctl enable redis

sudo systemctl status redis

redis-cli ping

sudo systemctl restart redis

pip install pytest sqlalchemy-utils




# اجرای تست‌ها
pytest tests/test_database.py -v




mysql -u chainstore_user -p chainstore_db -e "DROP DATABASE chainstore_db;"
mysql -u chainstore_user -p -e "CREATE DATABASE chainstore_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
alembic upgrade head


