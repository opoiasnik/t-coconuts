import { useUser } from "@clerk/clerk-react";
import Header from "../components/Header";
import Footer from "../components/Footer";
import { useState, useRef } from "react";
import axios from "axios";
import "../styles/DragAndDropPage.css";
import MicIcon from "@mui/icons-material/Mic";
import VolumeUpIcon from "@mui/icons-material/VolumeUp";
import VolumeOffIcon from "@mui/icons-material/VolumeOff";
import ArrowDropDownIcon from "@mui/icons-material/ArrowDropDown";
import IconButton from "@mui/material/IconButton";
import DiffMatchPatch from "diff-match-patch";
import DiffComponent from "../components/Diff";

function DragAndDropPage() {
  const { isSignedIn } = useUser();
  const [pdfFile, setPdfFile] = useState(null); // Selected PDF file
  const [pdfText, setPdfText] = useState(""); // Extracted text from PDF
  const [aiSuggestions, setAiSuggestions] = useState([]); // AI Suggestions as React elements
  const [instructions, setInstructions] = useState(""); // User instructions
  const [errorMessage, setErrorMessage] = useState("");
  const [isRecording, setIsRecording] = useState(false); // Voice recording state
  const [isResponseReceived, setIsResponseReceived] = useState(false); // Tracks if model response is received
  const [explanation, setExplanation] = useState(""); // Explanation of changes
  const [isDropdownVisible, setIsDropdownVisible] = useState(false); // Controls dropdown visibility
  const fileInputRef = useRef(null);
  const recognitionRef = useRef(null);

  const dmp = new DiffMatchPatch();

  const handleFileSelect = (event) => {
    const file = event.target.files[0];
    if (!file) {
      setErrorMessage("No file selected.");
      return;
    }
    setPdfFile(file);
    setErrorMessage("");
    setPdfText(""); // Reset PDF text when a new file is selected
    setAiSuggestions([]); // Reset AI suggestions
  };

  const handleCancelUpload = () => {
    setPdfFile(null);
    setPdfText("");
    setAiSuggestions([]);
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
      const uploadResponse = await axios.post("http://127.0.0.1:5000/upload", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });

      const { results } = uploadResponse.data;
      const extractedText = results.text || "No text extracted.";
      setPdfText(extractedText);

      if (instructions.trim() && extractedText.trim()) {
        const promptResponse = await axios.post("http://127.0.0.1:5000/process_prompt", {
          instructions,
          document_text: extractedText,
        });

        const { analysis, explanation } = promptResponse.data;

        setAiSuggestions(highlightDifferences(extractedText, analysis || ""));
        setExplanation(explanation.trim());

        setIsResponseReceived(true);
      } else {
        setErrorMessage("Please provide instructions and ensure the text is extracted successfully.");
      }
    } catch (error) {
      setErrorMessage("Error processing the file or instructions. Please try again.");
      console.error(error);
    }
  };

  const handleSpeakChanges = async () => {
    try {
      const response = await axios.get("http://127.0.0.1:5000/speak_changes", {
        responseType: "blob", // Expecting an audio file
      });

      // Create a URL object for playing the audio
      const audioUrl = URL.createObjectURL(response.data);
      const audio = new Audio(audioUrl);
      audio.play();
    } catch (error) {
      console.error("Error fetching audio:", error);
      alert("Unable to fetch audio. Please try again.");
    }
  };

  const toggleDropdownVisibility = () => {
    setIsDropdownVisible(!isDropdownVisible);
  };

  const highlightDifferences = (original, updated) => {
    const diffs = dmp.diff_main(original, updated);
    dmp.diff_cleanupSemantic(diffs);

    const processedDiffs = [];
    for (let i = 0; i < diffs.length; i++) {
      const [type, text] = diffs[i];

      if (type === -1 && diffs[i + 1] && diffs[i + 1][0] === 1) {
        // Substitution detected
        const [nextType, nextText] = diffs[i + 1];
        processedDiffs.push({
          type: "substitution",
          originalText: text,
          newText: nextText,
        });
        i++; // Skip the next diff as it's part of the substitution
      } else if (type === 1) {
        // Addition
        processedDiffs.push({
          type: "added",
          text: text,
        });
      } else if (type === -1) {
        // Deletion
        processedDiffs.push({
          type: "removed",
          text: text,
        });
      } else {
        // No change
        processedDiffs.push({
          type: "equal",
          text: text,
        });
      }
    }

    return processedDiffs.map((diff, index) => {
      if (diff.type === "substitution") {
        return (
          <DiffComponent
            key={index}
            type="substitution"
            originalText={diff.originalText}
            newText={diff.newText}
          />
        );
      } else if (diff.type === "added") {
        return (
          <DiffComponent
            key={index}
            type="added"
            text={diff.text}
            originalText=""
          />
        );
      } else if (diff.type === "removed") {
        return (
          <DiffComponent
            key={index}
            type="removed"
            text={diff.text}
            originalText={diff.text}
          />
        );
      } else {
        return <span key={index}>{diff.text}</span>;
      }
    });
  };

  const renderExplanation = (explanationText) => {
    const lines = explanationText.split('\n');

    return lines.map((line, index) => {
      // Process headings and lists
      if (line.startsWith('**') && line.endsWith('**')) {
        // It's a heading
        const title = line.replace(/\*\*/g, '');
        return <h5 key={index}>{title}</h5>;
      } else if (line.startsWith('- ')) {
        // List item
        return <li key={index}>{line.substring(2)}</li>;
      } else if (line === '') {
        // Empty line
        return <br key={index} />;
      } else {
        // Regular text
        return <p key={index}>{line}</p>;
      }
    });
  };

  return (
    <div className="drag-and-drop-container overflow-hidden">
      {isSignedIn ? (
        <>
          <Header />
          <div className="drag-and-drop-header">
            <h1 className="drag-and-drop-title">Document Processing</h1>
            <p className="drag-and-drop-subtitle">
              Provide instructions and upload a PDF document for analysis and suggestions.
            </p>

            <div className="instructions-input-container">
              <textarea
                className="instructions-input"
                placeholder="Enter your instructions for processing the document..."
                value={instructions}
                onChange={(e) => setInstructions(e.target.value)}
              />
            </div>

            <div
              className={`drag-and-drop-upload-box ${pdfFile ? "success-upload" : ""}`}
              onClick={!pdfFile ? () => fileInputRef.current.click() : undefined}
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
                {pdfText || <p className="drag-and-drop-placeholder">No document uploaded yet.</p>}
              </div>
            </div>

            <div className="drag-and-drop-column">
              <div className="ai-suggestions-header">
                <h3 className="drag-and-drop-section-title">AI Suggestions</h3>
                <div className="icon-buttons">
                  <IconButton
                    onClick={handleSpeakChanges}
                    aria-label="speak changes"
                    color={isResponseReceived ? "primary" : "default"}
                  >
                    {isResponseReceived ? <VolumeUpIcon /> : <VolumeOffIcon />}
                  </IconButton>
                  <IconButton
                    onClick={toggleDropdownVisibility}
                    aria-label="toggle explanation visibility"
                  >
                    <ArrowDropDownIcon />
                  </IconButton>
                </div>
              </div>
              {isDropdownVisible && (
                <div className="dropdown-box">
                  <h4>Explanation of Changes:</h4>
                  <div className="explanation-content">
                    {renderExplanation(explanation)}
                  </div>
                </div>
              )}
              <div className="drag-and-drop-text-box ai-suggestions">
                {aiSuggestions.length > 0 ? aiSuggestions : <p>No suggestions yet.</p>}
              </div>
            </div>
          </div>

          <Footer />
        </>
      ) : (
        <h1 className="drag-and-drop-unauthorized">You are not authorized to access this page</h1>
      )}
    </div>
  );
}

export default DragAndDropPage;
