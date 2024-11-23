import { useUser } from "@clerk/clerk-react";
import Header from "../components/Header";
import { useState, useRef } from "react";
import axios from "axios";
import "../styles/DragAndDropPage.css";

function DragAndDropPage() {
  const { isSignedIn } = useUser();
  const [pdfText, setPdfText] = useState("");
  const [aiSuggestions, setAiSuggestions] = useState("");
  const [errorMessage, setErrorMessage] = useState("");
  const fileInputRef = useRef(null); // Reference to the file input element

  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) {
      setErrorMessage("No file selected.");
      return;
    }
    const formData = new FormData();
    formData.append("file", file);

    try {
      // Укажите полный URL для запроса
      const response = await axios.post("http://127.0.0.1:5000/upload", formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      });
      const { results } = response.data;
      setPdfText(results.original_text || "No text extracted.");
      setAiSuggestions(results.ai_text || "AI did not generate any suggestions.");
      setErrorMessage("");
    } catch (error) {
      setErrorMessage("Error uploading file. Please try again.");
      console.error(error);
    }
  };

  const triggerFileInput = () => {
    // Simulate a click on the hidden file input
    fileInputRef.current.click();
  };

  return (
    <div className="drag-and-drop-container">
      {isSignedIn ? (
        <>
          <Header />
          <div className="drag-and-drop-header">
            <h1 className="drag-and-drop-title">Upload Your Document</h1>
            <p className="drag-and-drop-subtitle">
              Drag and drop a PDF document here or click to upload for AI analysis and suggestions.
            </p>
            <div className="drag-and-drop-upload-box" onClick={triggerFileInput}>
              <input
                type="file"
                accept="application/pdf"
                onChange={handleFileUpload}
                ref={fileInputRef} // Connect the input to the ref
                className="drag-and-drop-input"
              />
              <p className="drag-and-drop-upload-text">
                Drag and drop your file here or click to select.
              </p>
            </div>
            {errorMessage && <p className="drag-and-drop-error">{errorMessage}</p>}
          </div>

          <div className="drag-and-drop-content">
            {/* Left Section - Original Text */}
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

            {/* Right Section - AI Suggestions */}
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
