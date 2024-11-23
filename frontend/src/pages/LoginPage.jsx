import { useNavigate } from 'react-router-dom';

function LoginPage() {
  const navigate = useNavigate();

  return (
    <div className="container text-center py-5">
      <h1 className="mb-4">Login Page</h1>
      <p>Please click the button below to proceed.</p>
      <button className="btn btn-primary mt-4" onClick={() => navigate('/drag-and-drop')}>
        Login
      </button>
    </div>
  );
}

export default LoginPage;
