// KeyDisplayDialog.tsx
import React from 'react';
import { 
  Dialog, 
  DialogTitle, 
  DialogContent, 
  DialogActions, 
  Button, 
  TextField
} from '@mui/material';
import { nip19 } from 'nostr-tools';

interface KeyDisplayDialogProps {
  open: boolean;
  onClose: () => void;
  publicKey: string;
  privateKey: string;
}

const KeyDisplayDialog: React.FC<KeyDisplayDialogProps> = ({ 
  open, 
  onClose, 
  publicKey, 
  privateKey 
}) => {
  const npub = nip19.npubEncode(publicKey);
  const nsec = nip19.nsecEncode(privateKey);

  return (
    <Dialog open={open} onClose={onClose}>
      <DialogTitle>Your Public and Private Keys</DialogTitle>
      <DialogContent>
        <p>Please write down these keys and store them securely. You will need them to recover your account.</p>
        <TextField
          margin="dense"
          label="Public Key (npub)"
          type="text"
          fullWidth
          value={npub}
          InputProps={{
            readOnly: true,
          }}
        />
        <TextField
          margin="dense"
          label="Private Key (nsec)"
          type="text"
          fullWidth
          value={nsec}
          InputProps={{
            readOnly: true,
          }}
        />
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>I've written down my keys</Button>
      </DialogActions>
    </Dialog>
  );
};

export default KeyDisplayDialog;