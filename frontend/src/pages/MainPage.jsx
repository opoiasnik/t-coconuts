import { useNavigate } from 'react-router-dom';
import { useClerk, useUser } from '@clerk/clerk-react'; // Импортируем Clerk
import '../styles/MainPage.css';

function MainPage() {
  const navigate = useNavigate();
  const { user } = useUser(); // Получаем информацию о пользователе из Clerk
  const { openSignIn } = useClerk(); // Функция для открытия окна авторизации

  const handleGetStartedClick = () => {
    if (user) {
      // Если пользователь авторизован, переходим на страницу загрузки
      navigate('/upload');
    } else {
      // Если пользователь не авторизован, открываем окно авторизации
      openSignIn();
    }
  };

  return (
    <div className="main-page">
      {/* Left Section */}
      <div className="left-section">
        <div className="bubble-container">
          <div className="bubble">
            <span>📄 Upload Document</span>
            <p>Drag and drop your document for analysis</p>
          </div>
          <div className="bubble2">
            <span>🧐 AI Analysis</span>
            <p>Our AI evaluates your document for improvements</p>
          </div>
          <div className="bubble">
            <span>💡 Suggestions</span>
            <p>Receive actionable feedback and recommendations</p>
          </div>
          <div className="bubble2">
            <span>✅ Approve Changes</span>
            <p>Accept or modify the AI's suggestions</p>
          </div>
        </div>
      </div>

      {/* Right Section */}
      <div className="right-section">
        <h1>
          Enhance Your Documents with <span className="highlight">SmartValidator AI</span>
        </h1>
        <p className="description">
          Upload your contracts or documents and let our AI analyze and suggest improvements.
          Approve or customize changes to perfect your documents.
        </p>
        <button className="btn" onClick={handleGetStartedClick}>
          Get Started →
        </button>
      </div>
    </div>
  );
}

export default MainPage;
