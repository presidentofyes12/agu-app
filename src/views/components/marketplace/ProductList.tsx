import React from 'react';
import { Grid } from '@mui/material';
import { Product } from 'types';
import ProposalProductView from './ProposalProductView';
import ProductView from './ProductView';

interface ProductListProps {
  products: Product[];
}

const ProductList: React.FC<{ products: Product[] }> = ({ products }) => {
  return (
    <Grid container spacing={2}>
      {products.map(product => (
        <Grid item xs={12} sm={6} md={4} key={product.id}>
          {product.proposalId ? (
            <ProposalProductView product={product} />
          ) : (
            <ProductView product={product} />
          )}
        </Grid>
      ))}
    </Grid>
  );
};

export default ProductList;