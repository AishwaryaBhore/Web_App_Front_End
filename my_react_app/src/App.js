// import logo from './logo.svg';
import Navbar from './Nav.js';
import SignUp from './SignUp.js';
import Login from './Login.js';
import LoggedInContent from './Afterlogin.js';
import 'bootstrap/dist/css/bootstrap.min.css'; // Import Bootstrap CSS
import { BrowserRouter as Router, Route, Routes} from 'react-router-dom';

import './App.css';
import React, { useState } from 'react';

//function App() {
//   return (
//       <Router>
//            <div className="app-container">
//            <Navbar/>
//                <Routes>
//                    <Route path="/signup" element={<Signup/>}/>
//                    <Route path="/login" element={<Login/>} />
//                </Routes>
//            </div>
//       </Router>
//  );
//}
function App() {
  return (
    <Router>
      <div className="app-container">
        <Navbar />
        <Routes>
          <Route path="/signup" element={<SignUp />} />
          <Route path="/login" element={<Login />} />
          <Route path="/upload" element={<LoggedInContent/>}/>
        </Routes>
      </div>
    </Router>
  );
}
export default App;
