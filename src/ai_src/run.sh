# Create virtual environments
python3 -m venv server/venv
python3 -m venv client/venv

# Activate the server virtual environment and install dependencies
source server/venv/bin/activate
pip install -r server/requirements.txt
deactivate

# Activate the client virtual environment and install dependencies
source client/venv/bin/activate
pip install -r client/requirements.txt
deactivate

# Run the server and client in parallel
nohup server/venv/bin/python server/server.py &
nohup client/venv/bin/python client/client.py &
