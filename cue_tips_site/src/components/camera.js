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
      mediaStream.current = await navigator.mediaDevices.getUserMedia({
        video: {
          facingMode: 'environment'
        }
      });
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
    <div className="relative min-h-screen flex flex-col items-center justify-between px-4">
      {/* Video Section */}
      <div className="absolute top-[42%] left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-[80%] sm:w-[60%]">
        <video
          ref={videoRef}
          autoPlay loop muted controls playsInline
          className="mx-auto mt-4 w-full rounded-lg"
        />
      </div>
  
      {/* Processed Image Section */}
      {uploadedImage && !isStreaming && (
        <div className="absolute top-[42%] left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-[80%] sm:w-[60%]">        
          <img
            src={`data:image/png;base64,${uploadedImage}`}
            alt="Processed"
            className="mx-auto rounded-lg"
          />
        </div>
      )}
  
      {/* Control Buttons */}
      <div className="absolute bottom-10 w-full text-center">
        {!isStreaming ? (
          <button
            onClick={startCamera}
            className="px-6 py-3 text-lg bg-blue-600 text-white rounded-md cursor-pointer m-2 w-3/4 sm:w-1/2"
          >
            Open Camera
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
  
        <button
          onClick={capturePhoto}
          disabled={!isStreaming}
          className="px-6 py-3 text-lg bg-green-600 text-white rounded-md cursor-pointer m-2 w-3/4 sm:w-1/2"
        >
          Take Photo
        </button>
      </div>
  
      {/* Hidden Canvas for image processing */}
      <canvas ref={canvasRef} className="hidden" />
    </div>
  );
}

export default Camera;
