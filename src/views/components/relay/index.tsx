// @ts-nocheck
import React, { useState } from 'react';
import { Button, TextField, Typography, Box, CircularProgress } from '@mui/material';
import { toast } from 'react-toastify';
import AppWrapper from 'views/components/app-wrapper';
import AppMenu from 'views/components/app-menu';
import axios from 'axios';

const NostrRelaySetup: React.FC = () => {
  const [nostrKey, setNostrKey] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [assignedPort, setAssignedPort] = useState(null);

  const handleSetupRelay = async () => {
    setIsLoading(true);
    try {
      console.log('Sending setup request to server...');
      const response = await axios.post('http://172.17.0.1:5000/api/setup-relay', { nostrKey });
      console.log('Server response:', response.data);
      if (response.data.success) {
        setAssignedPort(response.data.port);
        toast.success(`Nostr relay and OpenVPN setup completed successfully on port ${response.data.port}`);
      } else {
        toast.error(`Setup failed: ${response.data.error}`);
      }
    } catch (error) {
      console.error('Setup failed:', error);
      toast.error(`Setup failed: ${error.response?.data?.error || error.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <AppWrapper>
      <AppMenu />
    <Box sx={{ p: 4 }}>
      <Typography variant="h4" gutterBottom>
        Set Up Nostr Relay with OpenVPN
      </Typography>
      <TextField
        label="Nostr Private Key"
        value={nostrKey}
        onChange={(e) => setNostrKey(e.target.value)}
        fullWidth
        margin="normal"
      />
      <Button 
        variant="contained" 
        color="primary" 
        onClick={handleSetupRelay}
        disabled={isLoading}
      >
        {isLoading ? <CircularProgress size={24} /> : 'Set Up Relay and VPN'}
      </Button>
      {assignedPort && (
        <Typography variant="body1" sx={{ mt: 2 }}>
          Relay set up on port: {assignedPort}
        </Typography>
      )}
    </Box>
    </AppWrapper>
  );
};

export default NostrRelaySetup;
