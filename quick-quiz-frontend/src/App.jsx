import React, { useState, useEffect } from "react";
import { jwtDecode } from 'jwt-decode';
import Dashboard from "./components/Dashboard/Dashboard";
import LoginForm from "./components/Login/LoginForm";
import RegisterForm from "./components/Login/RegisterForm";

function isTokenExpired(token) {
  const decoded = jwtDecode(token);
  const { exp } = decoded;

  if (!exp) {
    return false;
  }

  const currentTimeInSeconds = Date.now() / 1000;
  if (exp < currentTimeInSeconds) {
    return true;
  }
  return false;
}

function App() {
  const [currentView, setCurrentView] = useState("login");
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [user, setUser] = useState(null);

  useEffect(() => {
    const token = localStorage.getItem("token");
    const storedUser = localStorage.getItem("user");
    if(token && isTokenExpired(token)){
      localStorage.removeItem("token");
      localStorage.removeItem("user");
    }
    else if (token && storedUser) {
      setIsAuthenticated(true);
      setUser(JSON.parse(storedUser));
    }
  }, []);

  const handleLogout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("user");
    setIsAuthenticated(false);
    setUser(null);
  };

  if (isAuthenticated && user) {
    return <Dashboard user={user} onLogout={handleLogout} />;
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        <div className="bg-white rounded-2xl shadow-xl overflow-hidden">
          <div className="flex border-b">
            <button
              onClick={() => setCurrentView("login")}
              className={`flex-1 py-4 font-semibold transition-colors ${
                currentView === "login"
                  ? "bg-indigo-600 text-white"
                  : "bg-gray-50 text-gray-600 hover:bg-gray-100"
              }`}
            >
              Login
            </button>
            <button
              onClick={() => setCurrentView("register")}
              className={`flex-1 py-4 font-semibold transition-colors ${
                currentView === "register"
                  ? "bg-indigo-600 text-white"
                  : "bg-gray-50 text-gray-600 hover:bg-gray-100"
              }`}
            >
              Register
            </button>
          </div>

          {currentView === "login" ? (
            <LoginForm
              onSuccess={(userData) => {
                setIsAuthenticated(true);
                setUser(userData);
              }}
            />
          ) : (
            <RegisterForm onSuccess={() => setCurrentView("login")} />
          )}
        </div>
      </div>
    </div>
  );
}

export default App;
