import { useEffect, useRef, useState } from 'react';

const Game = () => {
  const canvasRef = useRef(null);
  const [cueBall, setCueBall] = useState({ x: 400, y: 200, radius: 10 });
  const [trajectory, setTrajectory] = useState({ angle: 45, length: 200 });

  // Draw pool table and cue ball on canvas
  const drawTable = (ctx) => {
    ctx.clearRect(0, 0, ctx.canvas.width, ctx.canvas.height); // Clear previous frame
    ctx.beginPath();
    ctx.arc(cueBall.x, cueBall.y, cueBall.radius, 0, 2 * Math.PI);
    ctx.fillStyle = 'red';
    ctx.fill();

    // Draw trajectory
    let endX = cueBall.x + trajectory.length * Math.cos(Math.PI / 180 * trajectory.angle);
    let endY = cueBall.y - trajectory.length * Math.sin(Math.PI / 180 * trajectory.angle);
    ctx.beginPath();
    ctx.moveTo(cueBall.x, cueBall.y);
    ctx.lineTo(endX, endY);
    ctx.strokeStyle = 'green';
    ctx.stroke();
  };

  // Calculate angle of the cue stick based on mouse position
  const calculateAngle = (mouseX, mouseY) => {
    const dx = mouseX - cueBall.x;
    const dy = cueBall.y - mouseY;  // Invert Y for canvas coordinates
    return Math.atan2(dy, dx) * (180 / Math.PI);  // Convert radians to degrees
  };

  // Handle mouse movement and update cue ball position
  const handleMouseMove = async (e) => {
    const mouseX = e.nativeEvent.offsetX;
    const mouseY = e.nativeEvent.offsetY;
    setCueBall({ x: mouseX, y: mouseY });

    // Calculate the angle of the cue stick
    const angle = calculateAngle(mouseX, mouseY);

    // Send updated position and angle to backend API
    const response = await fetch('/api/update-cue-ball', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        x: mouseX,
        y: mouseY,
        angle: angle,
      }),
    });
    
    const data = await response.json();
    setTrajectory({ angle: data.angle, length: trajectory.length }); // Update trajectory from backend
  };

  useEffect(() => {
    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');

    const updateCanvas = () => {
      drawTable(ctx);
    };

    updateCanvas();

    canvas.addEventListener('mousemove', handleMouseMove);
    return () => {
      canvas.removeEventListener('mousemove', handleMouseMove);
    };
  }, [cueBall, trajectory]);

  return (
    <div>
      <h1>Pool Game Simulation</h1>
      <canvas
        ref={canvasRef}
        width={800}
        height={400}
        style={{ border: '1px solid black' }}
      />
    </div>
  );
};

export default Game;
