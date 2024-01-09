// Login.js

import React, { useState } from 'react';
import './Login.css';
import LoggedInContent from './Afterlogin.js';

function Login() {
  const [loginData, setLoginData] = useState({
    username: '',
    password: '',
  });

  const [loginErrors, setLoginErrors] = useState({
    username: '',
    password: '',
  });

  const handleLoginInputChange = (e) => {
    const { name, value } = e.target;
    setLoginData((prevData) => ({
      ...prevData,
      [name]: value,
    }));
    setLoginErrors((prevErrors) => ({
      ...prevErrors,
      [name]: '',
    }));
  };

  const validateLoginForm = () => {
    let isValid = true;
    const newLoginErrors = { username: '', password: '' };

    if (!loginData.username.trim()) {
      newLoginErrors.username = 'Username is required';
      isValid = false;
    }

    if (!loginData.password.trim()) {
      newLoginErrors.password = 'Password is required';
      isValid = false;
    }

    setLoginErrors(newLoginErrors);
    return isValid;
  };

  const handleLoginSubmit = async (e) => {
    e.preventDefault();

    if (validateLoginForm()) {
      try {
        console.log('Login Data:', loginData);

        const response = await fetch('http://localhost:8080/login', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(loginData),
        });

        if (response.status === 200) {
          // Handle successful login
          console.log('User successfully logged in!');

        } else {
          // Handle failed login
          console.error('Login failed:', response.statusText);
        }
      } catch (error) {
        console.error('Error during login:', error);
      }
    } else {
      console.log('Login form validation failed.');
    }
  };

  const handleAfterLoginClick = () => {
    window.location.href = 'http://localhost:3000/upload/';

  };


  return (
    <div className="login-form">
      <h1>Login</h1>
      <form onSubmit={handleLoginSubmit}>
        <div className="form-group">
          <label htmlFor="username">Username</label>
          <input
            type="text"
            id="username"
            name="username"
            value={loginData.username}
            onChange={handleLoginInputChange}
            placeholder="Enter your username"
          />
          <span className="error-message">{loginErrors.username}</span>
        </div>

        <div className="form-group">
          <label htmlFor="password">Password</label>
          <input
            type="password"
            id="password"
            name="password"
            value={loginData.password}
            onChange={handleLoginInputChange}
            placeholder="Enter your password"
          />
          <span className="error-message">{loginErrors.password}</span>
        </div>

        <button type="submit" className="green-button" onClick={handleAfterLoginClick}>
          Log In
        </button>
      </form>
    </div>
  );
}
export default Login;
