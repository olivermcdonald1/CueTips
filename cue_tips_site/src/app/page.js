'use client'
import React, { useState } from 'react';
import axios from 'axios';
import Camera from '../components/camera';  // Ensure Camera component is imported

const Home = () => {
  const [svgContent, setSvgContent] = useState(null);  // To store the SVG response
  const [cueAngle, setCueAngle] = useState(45); // Example cue angle, you can modify it as needed

  // Function to handle the button click and simulate the path
  const handleSimulateClick = async () => {
    try {
      // Send cue_angle to /sim endpoint for simulation
      const response = await axios.post('http://localhost:4000/sim', {
        cue_angle: cueAngle,  // Send the cue angle value
      });

      if (response.status === 200) {
        setSvgContent(response.data.svg); // Set the SVG content received from the simulation
      } else {
        alert('Error during simulation: ' + response.data.message);
      }
    } catch (error) {
      console.error('Error during simulation process:', error);
      alert('An error occurred during the simulation process.');
    }
  };

  return (
    <div className="font-cakra text-white opacity-100">
      {/* Simulate Path Button */}
      <button
        onClick={handleSimulateClick}
        className="bg-red-500 text-white py-2 px-4 font-7l rounded mt-4"
      >
        Simulate Path
      </button>

      {/* Cue angle input */}
      <div className="mt-4">
        <label className="block text-lg">Cue Angle</label>
        <input
          type="number"
          value={cueAngle}
          onChange={(e) => setCueAngle(Number(e.target.value))}
          className="mt-2 px-4 py-2 rounded border"
        />
      </div>

      {/* Camera Component with SVG passed as prop */}
      <Camera svgContent={svgContent} />
    </div>
  );
};

export default Home;
