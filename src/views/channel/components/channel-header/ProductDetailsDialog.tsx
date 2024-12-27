import React, { useState } from 'react';
import Dialog from '@mui/material/Dialog';
import DialogTitle from '@mui/material/DialogTitle';
import DialogContent from '@mui/material/DialogContent';
import DialogActions from '@mui/material/DialogActions';
import TextField from '@mui/material/TextField';
import Button from '@mui/material/Button';
import { Channel } from 'types';

interface ProductDetailsDialogProps {
  open: boolean;
  onClose: () => void;
  onSubmit: (details: ProductDetails) => void;
  proposal: Channel;
}

interface ProductDetails {
  price: number;
  quantity: number;
  comment: string;
  images: string[];
}

const ProductDetailsDialog: React.FC<ProductDetailsDialogProps> = ({ open, onClose, onSubmit, proposal }) => {
  const [price, setPrice] = useState('');
  const [quantity, setQuantity] = useState('');
  const [comment, setComment] = useState('');
  const [images, setImages] = useState<string[]>([]);

  const handleSubmit = () => {
    onSubmit({
      price: parseFloat(price),
      quantity: parseInt(quantity),
      comment,
      images,
    });
  };

  const handleImageUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    // This is a placeholder for image upload functionality
    // You would typically handle file uploads here, possibly to a server
    // and then set the returned URLs to the images state
    console.log('Image upload placeholder');
    // setImages([...event.target.files].map(file => URL.createObjectURL(file)));
  };

  return (
    <Dialog open={open} onClose={onClose}>
      <DialogTitle>Submit Proposal to Marketplace</DialogTitle>
      <DialogContent>
        <TextField
          label="Price"
          type="number"
          value={price}
          onChange={(e) => setPrice(e.target.value)}
          fullWidth
          margin="normal"
        />
        <TextField
          label="Quantity"
          type="number"
          value={quantity}
          onChange={(e) => setQuantity(e.target.value)}
          fullWidth
          margin="normal"
        />
        <TextField
          label="Additional Comments"
          multiline
          rows={4}
          value={comment}
          onChange={(e) => setComment(e.target.value)}
          fullWidth
          margin="normal"
        />
        <input
          accept="image/*"
          style={{ display: 'none' }}
          id="raised-button-file"
          multiple
          type="file"
          onChange={handleImageUpload}
        />
        <label htmlFor="raised-button-file">
          <Button variant="contained" component="span">
            Upload Images
          </Button>
        </label>
        {/* You could display uploaded image previews here */}
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>Cancel</Button>
        <Button onClick={handleSubmit}>Submit</Button>
      </DialogActions>
    </Dialog>
  );
};

export default ProductDetailsDialog;