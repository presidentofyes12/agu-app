import React, { useState } from 'react';
import { 
  Dialog, 
  DialogTitle, 
  DialogContent, 
  DialogActions, 
  Button, 
  TextField
} from '@mui/material';

interface CredentialDisplayDialogProps {
  open: boolean;
  onClose: () => void;
  username: string;
  password: string;
}

const CredentialDisplayDialog: React.FC<CredentialDisplayDialogProps> = ({ 
  open, 
  onClose, 
  username, 
  password 
}) => {
  const [showPassword, setShowPassword] = useState(false);

  return (
    <Dialog open={open} onClose={onClose}>
      <DialogTitle>Your New Account Credentials</DialogTitle>
      <DialogContent>
        <p>Please copy and store these credentials in a safe place. You will need them to log in.</p>
        <TextField
          margin="dense"
          label="Username"
          type="text"
          fullWidth
          value={username}
          InputProps={{
            readOnly: true,
          }}
        />
        <TextField
          margin="dense"
          label="Password"
          type={showPassword ? 'text' : 'password'}
          fullWidth
          value={password}
          InputProps={{
            readOnly: true,
          }}
        />
        <Button onClick={() => setShowPassword(!showPassword)}>
          {showPassword ? 'Hide Password' : 'Show Password'}
        </Button>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>Close</Button>
      </DialogActions>
    </Dialog>
  );
};

export default CredentialDisplayDialog;