import React, { useState } from 'react';
import './App.css';

function App() {
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [registrationMessage, setRegistrationMessage] = useState('');

  const handleRegister = async () => {
    try {
      // Replace 'YOUR_BACKEND_API' with the actual URL of your backend API
      const response = await fetch('http://your-backend-api/register', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ username, email, password }),
      });

      const result = await response.json();

      if (response.ok) {
        // Display success message
        setRegistrationMessage('Registration successful! Check your email for verification.');
      } else {
        // Display error message
        setRegistrationMessage(result.message || 'Registration failed.');
      }
    } catch (error) {
      console.error('Error during registration:', error.message);
      setRegistrationMessage('Registration failed. Please try again later.');
    }

    // Clear the input fields after registration
    setUsername('');
    setEmail('');
    setPassword('');
  };

  return (
    <div className="App">
      <h1>User Registration</h1>
      <div>
        <label>Username: </label>
        <input type="text" value={username} onChange={(e) => setUsername(e.target.value)} />
      </div>
      <div>
        <label>Email: </label>
        <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} />
      </div>
      <div>
        <label>Password: </label>
        <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} />
      </div>
      <button onClick={handleRegister}>Register</button>

      {/* Display registration message */}
      {registrationMessage && <p>{registrationMessage}</p>}
    </div>
  );
}

export default App;
