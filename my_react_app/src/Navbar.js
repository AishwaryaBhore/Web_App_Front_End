// Import necessary modules
import React from 'react';
import './Navbar.css';

// Define the Navbar component
import Nav from 'react-bootstrap/Nav';

function Navbar() {
  return (
    <div class="topnav">
        <a class="active" href="#home">Home</a>
        <a href="#news">News</a>
        <a href="#contact">Contact</a>
        <a href="#about">About</a>
    </div>

 );
 };

// Export the Navbar component
export default Navbar;
