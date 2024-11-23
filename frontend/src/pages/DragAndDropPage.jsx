import { useUser } from "@clerk/clerk-react";
import Header from "../components/Header";
import { useState, useRef } from "react";
import axios from "axios";
import "../styles/DragAndDropPage.css";

function DragAndDropPage() {
  const { isSignedIn } = useUser();
  const [pdfText, setPdfText] = useState(""); // Состояние для текста PDF
  const [aiSuggestions, setAiSuggestions] = useState(""); // Состояние для предложений AI
  const [instructions, setInstructions] = useState(""); // Состояние для инструкций
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
    formData.append("instructions", instructions); // Add user instructions to the form

    try {
      // Отправка файла на бэкенд
      const response = await axios.post("http://127.0.0.1:5000/upload", formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      });

      // Обновление состояния текста и предложений
      const { results } = response.data;
      setPdfText(results.text || "No text extracted."); // Убедитесь, что 'text' соответствует результату из бэкенда
      setAiSuggestions(results.ai_text || "AI did not generate any suggestions."); // Отображение предложений
      setErrorMessage("");
    } catch (error) {
      setErrorMessage("Error uploading file. Please try again.");
      console.error(error);
    }
  };

  const triggerFileInput = () => {
    // Симуляция клика по скрытому input
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

            {/* Поле для инструкций */}
            <div className="instructions-input-container">
              <textarea
                className="instructions-input"
                placeholder="Enter your instructions for processing the document..."
                value={instructions}
                onChange={(e) => setInstructions(e.target.value)}
              />
            </div>

            {/* Область для загрузки файла */}
            <div className="drag-and-drop-upload-box" onClick={triggerFileInput}>
              <input
                type="file"
                accept="application/pdf"
                onChange={handleFileUpload}
                ref={fileInputRef} // Привязка к рефу
                className="drag-and-drop-input"
              />
              <p className="drag-and-drop-upload-text">
                Drag and drop your file here or click to select.
              </p>
            </div>
            {errorMessage && <p className="drag-and-drop-error">{errorMessage}</p>}
          </div>

          <div className="drag-and-drop-content">
            {/* Левая секция - исходный текст */}
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

            {/* Правая секция - предложения AI */}
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
