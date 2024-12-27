import React from 'react';
import { Box, Typography, Button } from '@mui/material';
import { Product } from 'types';

const ProductView: React.FC<{ product: Product }> = ({ product }) => {
  return (
    <Box>
      <Typography variant="h6">{product.name}</Typography>
      <Typography variant="body1">{product.description}</Typography>
      <Typography variant="body2">Price: {product.price}</Typography>
      <Typography variant="body2">Quantity: {product.quantity}</Typography>
      <Button variant="contained">Add to Cart</Button>
    </Box>
  );
};

export default ProductView;