import React from 'react';
import { Box, Typography, Button } from '@mui/material';
import { Channel, Message } from 'types';

interface DashboardProps {
  channel: Channel;
  messages: Message[];
}

const Dashboard: React.FC<DashboardProps> = ({ channel, messages }) => {
  return (
    <Box sx={{ p: 2 }}>
      <Typography variant="h4">Dashboard</Typography>
      
      {/* Committees */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h5">Committees</Typography>
        {/* Add committee information here */}
      </Box>

      {/* Proposal Details */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h5">Proposal Details</Typography>
        <Typography>Name: {channel.name}</Typography>
        <Typography>Creator: {channel.creator}</Typography>
        {/* Add more proposal details here */}
      </Box>

      {/* Activities */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h5">Activities</Typography>
        {messages.slice(0, 5).map((message) => (
          <Box key={message.id} sx={{ mb: 1 }}>
            <Typography>Contributor: {message.creator}</Typography>
            <Typography>Message: {message.content}</Typography>
          </Box>
        ))}
      </Box>

      {/* Rewards */}
      <Box>
        <Typography variant="h5">Rewards</Typography>
        <Typography>Reward distribution to be implemented</Typography>
      </Box>
    </Box>
  );
};

export default Dashboard;