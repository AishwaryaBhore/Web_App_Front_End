//import React from 'react';
import './Nav.css';
import SignUp from './SignUp.js';
import Login from './Login.js';
import React, { useState } from 'react';


function Navbar(){

  const handleSignUpClick = () => {
    window.location.href = 'http://localhost:8080/signup/';

  };

  const handleLoginClick = () => {
      window.location.href = 'http://localhost:8080/login/';

  };


  return(
    <div className="navbar-header">
      <a className="navbar-brand" href="#">Yoan One Solution</a>
    <ul className="nav navbar-nav navbar-right">
      <li><a href="/signup" onClick={handleSignUpClick}>Sign Up</a></li>
      <li><a href="/login" onClick={handleLoginClick}>Login</a></li>
    </ul>
    </div>

);
};
export default Navbar
//import React, { useState } from 'react';
//import './Nav.css';
//import SignUp from './SignUp.js';
//import Login from './Login.js';
//import LoggedInContent from './Afterlogin.js';
//
//function Navbar() {
//  const [isLoggedIn, setIsLoggedIn] = useState(false);
//  const [username, setUsername] = useState('');
//
//  const handleSignUpClick = () => {
//    window.location.href = 'http://localhost:3000/signup/';
//  };
//
//  const handleLoginClick = () => {
//    window.location.href = 'http://localhost:3000/login/';
//  };
//
//  const handleSuccessfulLogin = (user) => {
//    setIsLoggedIn(true);
//    setUsername(user.username);
//  };
//
//  const handleLogout = () => {
//    setIsLoggedIn(false);
//    setUsername('');
//  };
//
//  return (
//    <div className="navbar-header">
//      <a className="navbar-brand" href="#">
//        Yoan One Solution
//      </a>
//      <ul className="nav navbar-nav navbar-right">
//            <li>
//              <a href="/signup" onClick={handleSignUpClick}>
//                Sign Up
//              </a>
//            </li>
//            <li>
//              <a href="/login" onClick={handleLoginClick}>
//                Login
//              </a>
//            </li>
//            <li>
//              <a href="#" onClick={handleLogout}>
//                Logout
//              </a>
//            </li>
//      </ul>
//    </div>
//  );
//}
//
//export default Navbar;
