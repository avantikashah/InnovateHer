from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from groq import Groq

app = Flask(__name__)
CORS(app)

# Initialize the Groq client
groq_api_key = os.getenv("GROQ_API_KEY")
client = Groq(api_key=groq_api_key)

# Create an uploads folder
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Global variable to store the transcription text
transcription_text = ""

@app.route("/generate-notes", methods=["POST"])
def generate_notes():
    global transcription_text
    if "audio" not in request.files:
        return jsonify({"error": "No audio file found in the request"}), 400

    audio_file = request.files["audio"]
    audio_path = os.path.join(app.config["UPLOAD_FOLDER"], audio_file.filename)

    # Save the audio file to the server
    audio_file.save(audio_path)
    print(f"Audio file saved at: {audio_path}")
    
    # Transcribe the audio and store the transcription text
    transcription_text = transcribe_audio(filename=audio_path)
    
    # Generate the question and answer based on the transcription text
    notes = give_notes()
    return jsonify({"notes": notes})

def give_notes():
    global transcription_text
    notes = client.chat.completions.create(
        messages=[{"role":"user", "content":f"Generate notes for:{transcription_text}"}],
        model="llama-3.3-70b-versatile",  # Use appropriate model
        temperature=0.7,
        max_tokens=150
    )
    notes = notes.choices[0].message.content.strip()
    return notes



@app.route("/generate-quizzes", methods=["POST"])
def generate_quizzes():
    global transcription_text
    if "audio" not in request.files:
        return jsonify({"error": "No audio file found in the request"}), 400

    audio_file = request.files["audio"]
    audio_path = os.path.join(app.config["UPLOAD_FOLDER"], audio_file.filename)

    # Save the audio file to the server
    audio_file.save(audio_path)
    print(f"Audio file saved at: {audio_path}")
    
    # Transcribe the audio and store the transcription text
    transcription_text = transcribe_audio(filename=audio_path)
    
    # Generate the question and answer based on the transcription text
    question, answer = generate_mcq_one_by_one()

    # Respond back with question and answer
    return jsonify({
        "message": "Quiz generation is successful",
        "path": audio_path,
        "question": question,
        "answer": answer
    })

def transcribe_audio(filename):
    global transcription_text  # Use global to store the transcription text
    with open(filename, "rb") as file:
        # Create a transcription of the audio file
        transcription = client.audio.transcriptions.create(
            file=(filename, file.read()), # Required audio file
            model="whisper-large-v3-turbo", # Required model to use for transcription
            prompt="Specify context or spelling",  # Optional
            response_format="json",  # Optional
            language="en",  # Optional
            temperature=0.0  # Optional
        )
        transcription_text = transcription.text
        print(f"Transcription: {transcription_text}")

@app.route("/next-question", methods=["GET"])
def get_next_question():
    # This just recalls the generate_mcq_one_by_one without returning anything to frontend
    generate_mcq_one_by_one()
    return jsonify({"message": "Next question generated successfully"})

def generate_mcq_one_by_one():
    global transcription_text
    
    # Step 1: Ask Groq for one MCQ based on the transcription
    question_response = client.chat.completions.create(
        messages=[{"role":"user", "content":f"Generate a single multiple-choice question based on the following text:{transcription_text}"}],
        model="llama-3.3-70b-versatile",  # Use appropriate model
        temperature=0.7,
        max_tokens=150
    )
    question = question_response.choices[0].message.content.strip()
    print(question)
    
    # Step 2: Ask Groq to generate the answer for that question
    answer_response = client.chat.completions.create(
        messages=[{"role":"user", "content":f"Give the answer for {question}"}],
        model="llama-3.3-70b-versatile",  # Use appropriate model
        temperature=0.7,
        max_tokens=150
    )
    answer = answer_response.choices[0].message.content.strip()
    print(answer)
    return question, answer

@app.route("/end-quiz", methods=["POST"])
def end_quiz():
    global transcription_text
    transcription_text = ""  # Clear the transcription when the user ends the quiz
    return jsonify({"message": "Quiz ended successfully"})

if __name__ == "__main__":
    app.run(debug=True)


