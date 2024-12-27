import React from 'react';
import { Card, CardContent, CardMedia, Typography, Button } from '@mui/material';
import { Product } from 'types';

const ProductCard = ({ product }: { product: Product }) => {
  return (
    <Card>
      <CardMedia
        component="img"
        height="140"
        image={product.images[0] || 'placeholder-image-url'}
        alt={product.name}
      />
      <CardContent>
        <Typography gutterBottom variant="h6" component="div">
          {product.name}
        </Typography>
        <Typography variant="body2" color="text.secondary">
          {product.description.slice(0, 100)}...
        </Typography>
        <Typography variant="h6" color="primary" sx={{ mt: 2 }}>
          {product.price} {product.currency}
        </Typography>
        <Button variant="contained" color="primary" sx={{ mt: 1 }}>
          View Details
        </Button>
      </CardContent>
    </Card>
  );
};

export default ProductCard;