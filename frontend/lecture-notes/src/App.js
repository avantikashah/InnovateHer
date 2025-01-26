import React, { useState } from "react";

export default function AudioRecorder() {
  const [mediaRecorder, setMediaRecorder] = useState(null);
  const [audioURL, setAudioURL] = useState(null);
  const [audioBlob, setAudioBlob] = useState(null); // Store audio blob
  const [isRecording, setIsRecording] = useState(false);
  const [showOptions, setShowOptions] = useState(false);
	const [notes, setNotes] = useState(""); 

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const recorder = new MediaRecorder(stream);
      const audioChunks = [];

      recorder.ondataavailable = (event) => {
        audioChunks.push(event.data);
      };

      recorder.onstop = () => {
        const blob = new Blob(audioChunks, { type: "audio/wav" });
        setAudioBlob(blob); // Store the blob
        const url = URL.createObjectURL(blob);
        setAudioURL(url);
        setShowOptions(true);
      };

      recorder.start();
      setMediaRecorder(recorder);
      setIsRecording(true);
    } catch (error) {
      console.error("Error accessing microphone:", error);
    }
  };

  const stopRecording = () => {
    if (mediaRecorder) {
      mediaRecorder.stop();
      setIsRecording(false);
      setMediaRecorder(null);
    }
  };

	const generateNotes = async () => {
		if (!audioBlob) {
			alert("No audio file to upload!");
			return;
		}
	
		const formData = new FormData();
		formData.append("audio", audioBlob, "recording.wav");
	
		try {
			const response = await fetch("http://127.0.0.1:5000/generate-notes", {
				method: "POST",
				body: formData,
			});
	
			if (response.ok) {
				const result = await response.json();
				alert("Notes generated successfully: " + result.notes);
				console.log("Generated Notes:", result.notes); // Print notes to the console
				setNotes(result.notes); 
			} else {
				alert("Failed to generate notes. Please try again.");
			}
		} catch (error) {
			console.error("Error sending audio file:", error);
			alert("Error connecting to the server.");
		}
	};
	

  const generateQuizzes = async () => {
    if (!audioBlob) {
      alert("No audio file to upload!");
      return;
    }

    const formData = new FormData();
    formData.append("audio", audioBlob, "recording.wav");

    try {
      const response = await fetch("http://127.0.0.1:5000/generate-quizzes", {
        method: "POST",
        body: formData,
      });

      if (response.ok) {
        const result = await response.json();
        alert("Quiz generated successfully: " + JSON.stringify(result));
      } else {
        alert("Failed to generate quizzes. Please try again.");
      }
    } catch (error) {
      console.error("Error sending audio file:", error);
      alert("Error connecting to the server.");
    }
  };

	return (
		<div style={styles.container}>
			{!isRecording && !showOptions && (
				<button onClick={startRecording} style={styles.button}>
					Start Recording
				</button>
			)}
			{isRecording && (
				<button onClick={stopRecording} style={styles.button}>
					Stop Recording
				</button>
			)}
			{showOptions && audioURL && (
				<div style={styles.optionsContainer}>
					<audio controls src={audioURL} style={styles.audioPlayer}></audio>
					<button onClick={generateQuizzes} style={styles.button}>
						Generate Quizzes
					</button>
					<button onClick={generateNotes} style={styles.button}>
						Generate Notes
					</button>
					
					{/* Display the generated notes */}
					{notes && (
						<div style={styles.notesContainer}>
							<h3>Generated Notes:</h3>
							<p>{notes}</p>
						</div>
					)}
				</div>
			)}
		</div>
	);
}

const styles = {
  container: {
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    justifyContent: "center",
    height: "100vh",
    backgroundColor: "#f5f5f5",
  },
  button: {
    padding: "10px 20px",
    margin: "10px",
    fontSize: "16px",
    borderRadius: "5px",
    border: "none",
    backgroundColor: "#4CAF50",
    color: "white",
    cursor: "pointer",
  },
  optionsContainer: {
    marginTop: "20px",
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    gap: "10px",
  },
  audioPlayer: {
    margin: "10px",
  },
};


