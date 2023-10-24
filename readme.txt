INITIAL:
sudo apt-get update
sudo apt-get install libpython3-dev
sudo apt-get install python-pip
sudo apt install python3-pip
sudo pip install virtualenv
sudo apt-get install python3-venv

VENV:
CREATE - virtualenv -p python3 venv
ACTIVATE - source venv/bin/activate

PACKAGES:
pip install openai
pip install streamlit-authenticator

STREAMLIT:
streamlit run streamlit_test.py

