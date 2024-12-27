import * as React from 'react';
import Box from '@mui/material/Box';
import Modal from '@mui/material/Modal';
import Button from '@mui/material/Button';

// Define the type of the proposal object
interface Proposal {
  about: string;
  name: string;
}

interface ProposalDetailsProps {
  proposal: Proposal;
}

const style = {
  position: 'absolute' as 'absolute',
  top: '50%',
  left: '50%',
  width: '90%',
  transform: 'translate(-50%, -50%)',
  bgcolor: 'background.paper',
  border: '2px solid #000',
  boxShadow: 24,
  pt: 2,
  px: 4,
  pb: 3,
};

const ProposalDetails: React.FC<ProposalDetailsProps> = ({ proposal }) => {
  const [open, setOpen] = React.useState(false);
  const handleOpen = () => {
    setOpen(true);
  };
  const handleClose = () => {
    setOpen(false);
  };

  return (
    <div>
      <button
        onClick={handleOpen}
        className="btn btn_success"
        style={{ height: '40px' }}
      >
        Proposal Details
      </button>
      <Modal
        open={open}
        onClose={handleClose}
        aria-labelledby="parent-modal-title"
        aria-describedby="parent-modal-description"
      >
        <Box sx={{ ...style, width: 400 }}>
          <div className="text-center">
            <h2 id="parent-modal-title">Proposal Details</h2>
            <hr />
            <div>
              <h3> {proposal.name} </h3>
            </div>
          </div>
        </Box>
      </Modal>
    </div>
  );
};

export default ProposalDetails;
