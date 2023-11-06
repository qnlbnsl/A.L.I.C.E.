Let's start by creating the necessary files and directories for our project. We will have two main directories: `server` and `client`. Each of these directories will have its own virtual environment and requirements file. 

The `server` directory will contain the following files:
- `server.py`: This is the main server script that will handle incoming connections and manage the audio streams.
- `transcriber.py`: This script will handle the transcription of the audio streams using the Whisper API.
- `requirements.txt`: This file will list all the Python packages that need to be installed in the server's virtual environment.

The `client` directory will contain the following files:
- `client.py`: This is the main client script that will capture audio from the microphone and send it to the server.
- `requirements.txt`: This file will list all the Python packages that need to be installed in the client's virtual environment.

Let's start with the `server` directory:

server/requirements.txt
