'use client'
import React, { useState, useRef } from 'react';
import axios from 'axios';
import Camera from '../components/camera';  // Ensure Camera component is imported

const Home = () => {
  const [svgContent, setSvgContent] = useState(null);  // To store the SVG response
  const [cueAngle, setCueAngle] = useState(45); // Initial cue angle
  const [error, setError] = useState(null); // State to handle input validation errors
  const [cuePos, setCuePos] = useState(null);  // To store cue position data from the API response
  const [isDragging, setIsDragging] = useState(false); // State for drag status
  const startXRef = useRef(null); // To track initial X coordinate when dragging starts
  const startAngleRef = useRef(null); // To track initial angle during drag

  // Function to handle the button click and simulate the path
  const handleSimulateClick = async () => {
    try {
      // Send cue_angle to /sim endpoint for simulation
      const response = await axios.post('http://localhost:4000/sim', {
        cue_angle: cueAngle,  // Send the cue angle value
      });

      if (response.status === 200) {
        setSvgContent(response.data.svg); // Set the SVG content received from the simulation
        setCuePos(response.data.cue); // Store the cue position data received from the simulation
      } else {
        alert('Error during simulation: ' + response.data.message);
      }
    } catch (error) {
      console.error('Error during simulation process:', error);
      alert('An error occurred during the simulation process.');
    }
  };

  const handleAngleChange = (e) => {
    const value = Number(e.target.value);
    
    // Validate input (ensure it's a valid number within the range)
    if (isNaN(value)) {
      setError('Please enter a valid number');
      return;
    }
    if (value < 0 || value > 180) {
      setError('Angle must be between 0 and 180 degrees');
      return;
    }
    
    setError(null); // Clear error when input is valid
    setCueAngle(value); // Set the cue angle if valid
  };

  // Handle mouse drag to update cue angle
  const handleMouseDown = (e) => {
    setIsDragging(true);
    startXRef.current = e.clientX;
    startAngleRef.current = cueAngle; // Record initial angle
  };

  const handleMouseMove = (e) => {
    if (isDragging) {
      const deltaX = e.clientX - startXRef.current;
      const newAngle = startAngleRef.current + deltaX / 2; // Adjust sensitivity with division factor (e.g., /2)
      
      // Ensure angle stays within 0 to 180 degrees
      if (newAngle >= 0 && newAngle <= 180) {
        setCueAngle(newAngle);
      }
    }
  };

  const handleMouseUp = () => {
    setIsDragging(false);
  };

  // Function to create the cue rotation in SVG using cue_pos data
  const createCueRotation = () => {
    if (!cuePos) return null;  // If no cue position data is available, return null
    
    const { startX, startY, length, angle } = cuePos;
    
    // Calculate the rotation in radians from the cue angle
    const angleInRadians = (angle - 90) * (Math.PI / 180); // Adjust angle for correct orientation

    // Calculate the end point of the cue based on the angle and length
    const cueEndX = startX + length * Math.cos(angleInRadians);
    const cueEndY = startY + length * Math.sin(angleInRadians);

    // Return the SVG line element for the cue stick
    return (
      <line
        x1={startX}
        y1={startY}
        x2={cueEndX}
        y2={cueEndY}
        stroke="white"
        strokeWidth="4"
      />
    );
  };

  return (
    <div
      className="font-cakra text-white opacity-100"
      onMouseMove={handleMouseMove} // Add mousemove event on parent div
      onMouseUp={handleMouseUp} // Handle mouseup event
      onMouseLeave={handleMouseUp} // Optional: handle mouse leave to stop dragging
    >
      {/* Simulate Path Button */}
      <button
        onClick={handleSimulateClick}
        className="bg-red-500 text-white py-2 px-4 font-7l rounded mt-4"
      >
        Simulate Path
      </button>

      {/* Cue angle input */}
      <div className="mt-4">
        <label htmlFor="cueAngle" className="block text-lg">Cue Angle</label>
        <input
          id="cueAngle"
          type="number"
          value={cueAngle}
          onChange={handleAngleChange}
          className="mt-2 px-4 py-2 rounded border"
          min="0"
          max="180"
          step="1"
        />
        {error && <p className="text-red-500 text-sm mt-1">{error}</p>}
      </div>

      {/* Camera Component with SVG passed as prop */}
      <Camera svgContent={svgContent} />

      {/* Render the rotating cue stick as an SVG */}
      <svg
        width="300"
        height="300"
        className="mt-4"
        onMouseDown={handleMouseDown} // Start dragging when mouse is pressed
      >
        {/* Background (Optional) */}
        <circle cx="150" cy="150" r="5" fill="white" />
        
        {/* Render cue stick rotation */}
        {createCueRotation()}
      </svg>
    </div>
  );
};

export default Home;
