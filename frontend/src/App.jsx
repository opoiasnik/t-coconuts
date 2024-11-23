import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import MainPage from './pages/MainPage';
import LoginPage from './pages/LoginPage';
import DragAndDropPage from './pages/DragAndDropPage';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<MainPage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/drag-and-drop" element={<DragAndDropPage />} />
      </Routes>
    </Router>
  );
}

export default App;
