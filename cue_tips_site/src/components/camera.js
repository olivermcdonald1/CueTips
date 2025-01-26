import React, { useState, useRef } from 'react';
import axios from 'axios';

const Camera = () => {
  const [isStreaming, setIsStreaming] = useState(false);
  const [capturedImage, setCapturedImage] = useState(null); // State to store captured image
  const [isUploading, setIsUploading] = useState(false); // State to track upload status
  const [uploadedImage, setUploadedImage] = useState(null);

  const videoRef = useRef(null);
  const canvasRef = useRef(null); // Ref for canvas element
  let mediaStream = useRef(null);

  const startCamera = async () => {
    try {
      // Request webcam access
      mediaStream.current = await navigator.mediaDevices.getUserMedia({ video: true });

      // Attach the stream to the video element
      videoRef.current.srcObject = mediaStream.current;
      setIsStreaming(true);
    } catch (err) {
      console.error("Error accessing webcam: ", err);
    }
  };

  const stopCamera = () => {
    // Stop all tracks in the stream to release the webcam
    if (mediaStream.current) {
      mediaStream.current.getTracks().forEach(track => track.stop());
      videoRef.current.srcObject = null;
     }
    setIsStreaming(false);
  };

  const capturePhoto = () => {
    // Get the canvas context and draw the current video frame
    const canvas = canvasRef.current;
    const context = canvas.getContext('2d');
    
    // Set the canvas dimensions to match the video
    canvas.width = videoRef.current.videoWidth;
    canvas.height = videoRef.current.videoHeight;
    
    // Draw the current frame of the video on the canvas
    context.drawImage(videoRef.current, 0, 0, canvas.width, canvas.height);
  
    // Convert the canvas to a base64 image string
    const imageData = canvas.toDataURL('image/png');

    canvas.toBlob(async (blob) => {
      if (blob) {
        await uploadImage(blob);
      }
    }, 'image/png');
    stopCamera();
    
    // Pass the captured image to uploadImage
  };
  

  const uploadImage = async (blob) => {
    if (!blob) return;
  
    const formData = new FormData();
    formData.append('file', blob, 'captured-image.png');
  
    try {
      const response = await axios.post('http://localhost:4000/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });
      
      console.log(response)
      const data = await response.data;

      if (response.status == 200) {
        setUploadedImage(data.image); // Set the base64 image response

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
    <div>
      <h1>Camera</h1>
      <video ref={videoRef} autoPlay width="100%" height="auto" />
      <div>
        {!isStreaming ? (
          <button onClick={startCamera}>Start Camera</button>
        ) : (
          <button onClick={stopCamera}>Stop Camera</button>
        )}
        <button onClick={capturePhoto} disabled={!isStreaming}>Capture Photo</button>

        {isUploading && (
          <div className="font-5xl text-white">Extracting Balls</div>
        )}
        {uploadedImage && (
        <div>
          <h2>Processed Image</h2>
          <img src={`data:image/png;base64,${uploadedImage}`} alt="Processed" />
        </div>
      )}
      </div>

      {/* {capturedImage && (
        <div>
          <h2>Captured Photo</h2>
          <img src={capturedImage} alt="Captured" />
        </div>
      )} */}

      {/* Hidden canvas element used for capturing the photo */}
      <canvas ref={canvasRef} style={{ display: 'none' }} />
    </div>
  );
};

export default Camera;
