from flask import Flask, jsonify
import subprocess
import sys

app = Flask(__name__)

@app.route('/launch', methods=['POST'])
def launch_emotion():
    try:
        # Use the current Python interpreter (virtualenv)
        subprocess.Popen([sys.executable, 'emotion/live_emotion.py'])
        return jsonify({'status': 'launched'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(port=5000)
