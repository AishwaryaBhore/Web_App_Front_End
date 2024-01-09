// LoggedInContent.js
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import './Afterlogin.css';
function LoggedInContent() {
  const [username] = useState("JohnDoe"); // Replace with the actual username
  const navigate = useNavigate();

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await fetch('http://localhost:8080/upload', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
        });

        if (response.status === 200) {
          // Handle successful upload
          console.log('File uploaded successfully!');
        }
      } catch (error) {
        console.error('Error uploading file:', error);
      }
    };

    fetchData();
  }, []); // Empty dependency array means the effect runs once after the initial render

  const goBack = () => {
    const userDecision = window.confirm("Do you really want to go back?");
    if (userDecision) {
      alert("Going back!");
      navigate(-1); // Use react-router-dom's navigate function for navigation
    } else {
      alert("No option selected.");
    }
  };

  return (
    <>
      <main>
        <div>
          <h5 id="user-info">Logged in as: {username}</h5>
        </div>

        <form method="post" encType="multipart/form-data">
          <div>
            <label htmlFor="file">Choose file to upload</label>
            <input type="file" id="file" name="file" multiple />
          </div>

          <div>
            <button type="submit">Submit</button>
          </div>
        </form>

        <div>
            <a href="http://localhost:3000/login" onclick="return goBack()">Back</a>
        </div>
      </main>
    </>
  );
}

export default LoggedInContent;
