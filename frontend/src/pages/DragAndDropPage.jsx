import { useUser } from "@clerk/clerk-react";
import Header from "../components/Header";
import { useState, useRef } from "react";
import axios from "axios";
import "../styles/DragAndDropPage.css";
import MicIcon from "@mui/icons-material/Mic";
import MicOffIcon from "@mui/icons-material/MicOff";
import IconButton from "@mui/material/IconButton";

function DragAndDropPage() {
  const { isSignedIn } = useUser();
  const [pdfFile, setPdfFile] = useState(null); // Selected PDF file
  const [pdfText, setPdfText] = useState(""); // Extracted text from PDF
  const [aiSuggestions, setAiSuggestions] = useState(""); // AI Suggestions
  const [instructions, setInstructions] = useState(""); // User instructions
  const [errorMessage, setErrorMessage] = useState("");
  const [isRecording, setIsRecording] = useState(false); // Voice recording state
  const fileInputRef = useRef(null);
  const recognitionRef = useRef(null);

  const handleFileSelect = (event) => {
    const file = event.target.files[0];
    if (!file) {
      setErrorMessage("No file selected.");
      return;
    }
    setPdfFile(file);
    setErrorMessage("");
    setPdfText(""); // Reset PDF text when a new file is selected
    setAiSuggestions(""); // Reset AI suggestions
  };

  const handleCancelUpload = () => {
    setPdfFile(null);
    setPdfText("");
    setAiSuggestions("");
    fileInputRef.current.value = null; // Reset file input
  };

  const handleSubmit = async () => {
    if (!pdfFile) {
      setErrorMessage("Please upload a file before submitting.");
      return;
    }

    const formData = new FormData();
    formData.append("file", pdfFile);

    try {
      // Step 1: Convert PDF to text via /upload endpoint
      const uploadResponse = await axios.post("http://127.0.0.1:5000/upload", formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      });

      const { results } = uploadResponse.data;
      const extractedText = results.text || "No text extracted.";
      setPdfText(extractedText);

      // Step 2: Send the extracted text and instructions to /process_prompt endpoint
      if (instructions.trim() && extractedText.trim()) {
        const promptResponse = await axios.post("http://127.0.0.1:5000/process_prompt", {
          instructions,
          document_text: extractedText,
        });

        const { analysis } = promptResponse.data;
        setAiSuggestions(analysis || "No suggestions provided.");
      } else {
        setErrorMessage("Please provide instructions and ensure the text is extracted successfully.");
      }
    } catch (error) {
      setErrorMessage("Error processing the file or instructions. Please try again.");
      console.error(error);
    }
  };

  const toggleVoiceInput = () => {
    if (!("webkitSpeechRecognition" in window)) {
      alert("Your browser does not support voice recognition.");
      return;
    }

    if (!isRecording) {
      const recognition = new window.webkitSpeechRecognition();
      recognition.lang = "en-US";
      recognition.continuous = true;
      recognition.interimResults = false;

      recognition.onstart = () => {
        setIsRecording(true);
        recognitionRef.current = recognition;
      };

      recognition.onerror = (event) => {
        console.error("Speech recognition error: ", event.error);
        setIsRecording(false);
      };

      recognition.onend = () => {
        setIsRecording(false);
        recognitionRef.current = null;
      };

      recognition.onresult = (event) => {
        const transcript = Array.from(event.results)
          .map((result) => result[0].transcript)
          .join(" ");
        setInstructions((prev) => `${prev} ${transcript}`.trim());
      };

      recognition.start();
    } else {
      if (recognitionRef.current) {
        recognitionRef.current.stop();
        recognitionRef.current = null;
      }
      setIsRecording(false);
    }
  };

  const triggerFileInput = () => {
    fileInputRef.current.click();
  };

  return (
    <div className="drag-and-drop-container">
      {isSignedIn ? (
        <>
          <Header />
          <div className="drag-and-drop-header">
            <h1 className="drag-and-drop-title">Document Processing</h1>
            <p className="drag-and-drop-subtitle">
              Provide instructions and upload a PDF document for analysis and suggestions.
            </p>

            <div className="instructions-input-container">
              <div className="instructions-header">
                <IconButton
                  className="voice-record-btn"
                  color={isRecording ? "error" : "primary"}
                  onClick={toggleVoiceInput}
                  aria-label="toggle voice input"
                >
                  {isRecording ? <MicOffIcon /> : <MicIcon />}
                </IconButton>
              </div>
              <textarea
                className="instructions-input"
                placeholder="Enter your instructions for processing the document..."
                value={instructions}
                onChange={(e) => setInstructions(e.target.value)}
              />
            </div>

            <div
              className={`drag-and-drop-upload-box ${pdfFile ? "success-upload" : ""}`}
              onClick={!pdfFile ? triggerFileInput : undefined}
            >
              <input
                type="file"
                accept="application/pdf"
                onChange={handleFileSelect}
                ref={fileInputRef}
                className="drag-and-drop-input"
              />
              {pdfFile ? (
                <p className="upload-success-text">✔ Uploaded Successfully: {pdfFile.name}</p>
              ) : (
                <p className="drag-and-drop-upload-text">
                  Drag and drop your file here or click to select.
                </p>
              )}
            </div>

            {pdfFile && (
              <div className="submit-cancel-buttons">
                <button className="drag-and-drop-submit-btn" onClick={handleSubmit}>
                  Submit
                </button>
                <button className="cancel-upload-btn" onClick={handleCancelUpload}>
                  Cancel
                </button>
              </div>
            )}

            {errorMessage && <p className="drag-and-drop-error">{errorMessage}</p>}
          </div>

          <div className="drag-and-drop-content">
            <div className="drag-and-drop-column">
              <h3 className="drag-and-drop-section-title">Original Text</h3>
              <div className="drag-and-drop-text-box">
              {pdfText || (
                <p className="drag-and-drop-placeholder">
                  No document uploaded yet. The text will appear here.
                </p>
              )}
            </div>
            </div>

            <div className="drag-and-drop-column">
              <h3 className="drag-and-drop-section-title">AI Suggestions</h3>
              <div className="drag-and-drop-text-box ai-suggestions">
                {aiSuggestions || (
                  <p className="drag-and-drop-placeholder">
                    AI suggestions and enhancements will appear here after analysis.
                  </p>
                )}
              </div>
            </div>
          </div>
        </>
      ) : (
        <h1 className="drag-and-drop-unauthorized">You are not authorized to access this page</h1>
      )}
    </div>
  );
}

export default DragAndDropPage;