# Argus: Plateforme de Sécurité Personnalisée


## Project Overview
Argus is an intelligent surveillance platform that integrates facial recognition, object/person detection, movement detection, and voice command detection for security actions.

## Voice Command Detection
You can control security actions (e.g., lock doors, trigger alarm, open garage, turn on lights) using natural voice commands.

### Demo
- Go to `/voicecontrol/demo/` in your browser.
- Click "Start Recording" and speak a command (e.g., "Can you please lock the doors?").
- Click "Stop & Send" to process your command and see the result.

Supported actions include:
- Lock/unlock doors
- Trigger/disarm alarm
- Open garage
- Turn on lights

Flexible command detection supports synonyms and natural phrases.

## Quick Setup Guide

### 1. Clone the Repository
```sh
git clone https://github.com/Hibaxbelghith/argus.git
cd argus
```

### 2. Create and Activate a Virtual Environment (Python 3.11)
```sh
# Windows (PowerShell)
python -m venv venv
.\venv\Scripts\Activate
```

### 3. Install Dependencies
```sh
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Run Database Migrations
```sh
python manage.py migrate
```

### 5. Start the Development Server
```sh
python manage.py runserver
```

Visit [http://127.0.0.1:8000/](http://127.0.0.1:8000/) to access the app.

## Notes
- Use the provided `venv` or `.venv` for your virtual environment. Only one is needed.
- For speech-to-text, install Vosk or Google Speech dependencies as needed.
- This server is for development only. For production, use a WSGI/ASGI server.

## Troubleshooting
- If you see errors about missing packages, re-run `pip install -r requirements.txt`.
- Ensure your Python version is 3.11.
- For environment issues, delete and recreate your virtual environment.

---

For more details, see the code comments or contact the project maintainers.
