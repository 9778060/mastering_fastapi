INITIAL:
sudo apt update && sudo apt upgrade -y
sudo apt install software-properties-common -y
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update
sudo apt install python3.12
python3.12 --version
curl -sS https://bootstrap.pypa.io/get-pip.py | python3.12
pip3.12 -V
pip3.12 install virtualenv

VENV:
CREATE - virtualenv -p python3.12 venv
ACTIVATE - source venv/bin/activate

PACKAGES:
pip3.12 install -r requirements.txt

UVICORN:
uvicorn socialapi:main.app --reload

ALEMBIC:
init -> alembic init migrations
current -> alembic current
generate revision -> alembic revision --autogenerate
upgrade -> alembic upgrade <revision | head>
downgrade -> alembic downgrade <revision | base>
history -> alembic history <--verbose>

POSTGRESQL:
sudo service postgresql start
sudo service postgresql stop
sudo service postgresql status
sudo -u postgres psql
hostname -I
