import React, { useState, useRef } from 'react';
import axios from 'axios';

const Camera = () => {
  const [isStreaming, setIsStreaming] = useState(false);
  const [capturedImage, setCapturedImage] = useState(null);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadedImage, setUploadedImage] = useState(null);

  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  let mediaStream = useRef(null);

  const startCamera = async () => {
    try {
      mediaStream.current = await navigator.mediaDevices.getUserMedia({ video: true });
      videoRef.current.srcObject = mediaStream.current;
      setIsStreaming(true);
    } catch (err) {
      console.error('Error accessing webcam: ', err);
    }
  };

  const stopCamera = () => {
    if (mediaStream.current) {
      mediaStream.current.getTracks().forEach(track => track.stop());
      videoRef.current.srcObject = null;
    }
    setIsStreaming(false);
  };

  const capturePhoto = () => {
    const canvas = canvasRef.current;
    const context = canvas.getContext('2d');
    canvas.width = videoRef.current.videoWidth;
    canvas.height = videoRef.current.videoHeight;
    context.drawImage(videoRef.current, 0, 0, canvas.width, canvas.height);

    canvas.toBlob(async (blob) => {
      if (blob) {
        await uploadImage(blob);
      }
    }, 'image/png');
    stopCamera();
  };

  const uploadImage = async (blob) => {
    if (!blob) return;

    const formData = new FormData();
    formData.append('file', blob, 'captured-image.png');

    try {
      setIsUploading(true);
      const response = await axios.post('http://localhost:4000/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });

      const data = await response.data;

      if (response.status === 200) {
        setUploadedImage(data.image); 
      } else {
        alert('Error uploading image: ' + data);
      }
    } catch (error) {
      console.error('Error:', error);
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div className="relative w-full h-screen flex flex-col items-center justify-center">
      <div className="relative w-full max-w-3xl h-[60vh]"> {/* Limit the camera's height */}
        <video
          ref={videoRef}
          autoPlay
          className="w-full h-full object-cover absolute top-0 left-0 rounded-lg shadow-lg" // Tailwind styling for video
        />
      </div>
      <div className="absolute bottom-10 w-full text-center">
        {!isStreaming ? (
          <button
            onClick={startCamera}
            className="px-6 py-3 text-lg bg-blue-600 text-white rounded-md cursor-pointer m-2 w-3/4 sm:w-1/2"
          >
            Start Camera
          </button>
        ) : (
          <button
            onClick={stopCamera}
            className="px-6 py-3 text-lg bg-red-600 text-white rounded-md cursor-pointer m-2 w-3/4 sm:w-1/2"
          >
            Stop Camera
          </button>
        )}
        {isUploading && (
          <div className="text-white text-xl">Uploading...</div>
        )}
        {uploadedImage && (
          <div className="mt-4">
            <h2 className="text-2xl font-semibold">Processed Image</h2>
            <img
              src={`data:image/png;base64,${uploadedImage}`}
              alt="Processed"
              className="mx-auto mt-4 max-w-full rounded-lg"
            />
          </div>
        )}
        <button
          onClick={capturePhoto}
          disabled={!isStreaming}
          className="px-6 py-3 text-lg bg-green-600 text-white rounded-md cursor-pointer m-2 w-3/4 sm:w-1/2"
        >
          Capture Photo
        </button>
  
        
      </div>
  
      <canvas ref={canvasRef} className="hidden" />
    </div>
  );
};

const buttonStyle = {
  padding: '10px 20px',
  fontSize: '18px',
  backgroundColor: '#007bff',
  color: 'white',
  border: 'none',
  borderRadius: '5px',
  cursor: 'pointer',
  margin: '10px',
  width: '80%',
};

export default Camera;
