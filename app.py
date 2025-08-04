from flask import Flask, render_template, request, jsonify
import speech_recognition as sr
import os
from werkzeug.utils import secure_filename
from flask_cors import CORS  # Enable cross-origin support

# ✅ Initialize Flask App
app = Flask(__name__)
CORS(app)  # Allow frontend requests

# ✅ Set up the Uploads Folder
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

recognizer = sr.Recognizer()

# ✅ Serve index.html from "templates" folder
@app.route("/")
def home():
    return render_template("index.html")  # Uses templates/index.html

# ✅ API to handle real-time speech recognition from the microphone
@app.route("/record", methods=["POST"])
def record_speech():
    try:
        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source, duration=1)
            print("Listening...")
            audio = recognizer.listen(source, timeout=60)
            text = recognizer.recognize_google(audio)
            return jsonify({"text": text})
    except sr.UnknownValueError:
        return jsonify({"error": "Could not understand the audio"}), 400
    except sr.RequestError:
        return jsonify({"error": "Error connecting to Google API"}), 500

# ✅ API to handle uploaded audio files
@app.route("/upload", methods=["POST"])
def upload_audio():
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400
    
    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400
    
    filename = secure_filename(file.filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(file_path)
    
    with sr.AudioFile(file_path) as source:
        recognizer.adjust_for_ambient_noise(source, duration=1)
        audio = recognizer.record(source)
        
        try:
            text = recognizer.recognize_google(audio)
            return jsonify({"text": text})
        except sr.UnknownValueError:
            return jsonify({"error": "Could not understand the audio"}), 400
        except sr.RequestError:
            return jsonify({"error": "Error connecting to Google API"}), 500

# ✅ Run Flask App
if __name__ == "__main__":
    app.run(debug=True)
