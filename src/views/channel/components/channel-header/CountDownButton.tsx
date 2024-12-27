import React, { useState, useEffect } from 'react';

interface CountdownButtonProps {
  createdAt: number; // Assuming createdAt is a Unix timestamp in seconds
  additionalMinutes: number;
}

const CountdownButton: React.FC<CountdownButtonProps> = ({ createdAt, additionalMinutes }) => {
  const calculateRemainingTime = (): number => {
    const currentTime = Math.floor(Date.now() / 1000);
    const expirationTime = createdAt + additionalMinutes * 60; // 60 seconds in a minute
    const remainingTime = expirationTime - currentTime;

    return remainingTime >= 0 ? remainingTime : -1;
  };

  const [remainingTime, setRemainingTime] = useState(calculateRemainingTime());

  useEffect(() => {
    const timer = setInterval(() => {
      const newRemainingTime = calculateRemainingTime();
      setRemainingTime(newRemainingTime);
      if (newRemainingTime === 0) {
        // Refresh the page when remainingTime reaches 0
        window.location.reload();
      }
    }, 1000);

    return () => clearInterval(timer);
  }, [createdAt, additionalMinutes]);

  const formatTime = (time: number): string => {
    const hours = Math.floor(time / 3600);
    const minutes = Math.floor((time % 3600) / 60);
    const seconds = time % 60;

    return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
  };

  return (
    <button className="btn btn_success">
      {remainingTime >= 0 ? `Remaining Time - ${formatTime(remainingTime)}` : "Time expired"}
    </button>
  );
};

export default CountdownButton;
