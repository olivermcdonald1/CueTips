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
    <div style={{ position: 'relative', width: '100%', height: '100vh' }}>
      <h1>Camera</h1>
      <video
        ref={videoRef}
        autoPlay
        style={{
          width: '100%',
          height: '100%',
          objectFit: 'cover',
          position: 'absolute',
          top: 0,
          left: 0,
        }}
      />
      <div style={{ position: 'absolute', bottom: '10%', width: '100%', textAlign: 'center' }}>
        {!isStreaming ? (
          <button onClick={startCamera} style={buttonStyle}>Start Camera</button>
        ) : (
          <button onClick={stopCamera} style={buttonStyle}>Stop Camera</button>
        )}
        <button onClick={capturePhoto} disabled={!isStreaming} style={buttonStyle}>Capture Photo</button>

        {isUploading && (
          <div style={{ color: 'white', fontSize: '24px' }}>Uploading...</div>
        )}
        {uploadedImage && (
          <div>
            <h2>Processed Image</h2>
            <img src={`data:image/png;base64,${uploadedImage}`} alt="Processed" />
          </div>
        )}
      </div>

      <canvas ref={canvasRef} style={{ display: 'none' }} />
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
