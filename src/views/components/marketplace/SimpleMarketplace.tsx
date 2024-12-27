/*import React, { useState, useEffect } from 'react';
import { Grid, Typography, Pagination, Box } from '@mui/material';
import { useMarketplace } from 'hooks/useMarketplace';
import ProductCard from './ProductCard';

const SimpleMarketplace = () => {
  const { products } = useMarketplace();
  const [currentPage, setCurrentPage] = useState(1);
  const productsPerPage = 12;

  const indexOfLastProduct = currentPage * productsPerPage;
  const indexOfFirstProduct = indexOfLastProduct - productsPerPage;
  const currentProducts = products.slice(indexOfFirstProduct, indexOfLastProduct);

  const pageCount = Math.ceil(products.length / productsPerPage);

  const handlePageChange = (event, value) => {
    setCurrentPage(value);
  };

  return (
    <Box sx={{ padding: 3 }}>
      <Typography variant="h4" gutterBottom>Simple Marketplace</Typography>
      <Grid container spacing={3}>
        {currentProducts.map((product) => (
          <Grid item xs={12} sm={6} md={4} lg={3} key={product.id}>
            <ProductCard product={product} />
          </Grid>
        ))}
      </Grid>
      <Box sx={{ display: 'flex', justifyContent: 'center', marginTop: 3 }}>
        <Pagination 
          count={pageCount} 
          page={currentPage} 
          onChange={handlePageChange} 
          color="primary" 
        />
      </Box>
    </Box>
  );
};

export default SimpleMarketplace;*/