import React, { useState, useEffect } from 'react';
import { useMarketplace } from 'hooks/useMarketplace';
import { Card, CardContent, Typography, Grid, Button, TextField, Box } from '@mui/material';
import { Link } from '@reach/router';
import useTranslation from 'hooks/use-translation';
import { RouteComponentProps } from '@reach/router';
import { Product } from 'types';
import { Helmet } from 'react-helmet';
import AppWrapper from 'views/components/app-wrapper';
import AppMenu from 'views/components/app-menu';
import AppContent from 'views/components/app-content';

interface MarketplaceProps extends RouteComponentProps {}

const MarketplacePage: React.FC<MarketplaceProps> = (props) => {
  const [t] = useTranslation();
  const { stalls, products } = useMarketplace();
  const [searchQuery, setSearchQuery] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const productsPerPage = 18;

  const filteredProducts = products.filter(product => 
    product.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    product.description.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const indexOfLastProduct = currentPage * productsPerPage;
  const indexOfFirstProduct = indexOfLastProduct - productsPerPage;
  const currentProducts = filteredProducts.slice(indexOfFirstProduct, indexOfLastProduct);
  const totalPages = Math.ceil(filteredProducts.length / productsPerPage);

  const handleSearchChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setSearchQuery(event.target.value);
    setCurrentPage(1);
  };

  const handlePageChange = (newPage: number) => {
    setCurrentPage(newPage);
  };

  const renderProduct = (product: Product) => (
    <Grid item xs={12} sm={6} md={4} key={product.id}>
      <Card className="product-card">
        <CardContent>
          <Typography variant="h6">{product.name}</Typography>
          <Typography variant="body2">{product.description}</Typography>
          <Typography variant="body1">
            {t('Price: {{price}} {{currency}}', { price: product.price, currency: product.currency })}
          </Typography>
          {product.proposalId && (
            <Typography variant="body2">
              This product is based on a proposal.
              <Link to={`/channel/${product.proposalId}`}>View Proposal</Link>
            </Typography>
          )}
          {product.images && product.images.length > 0 && (
            <Box sx={{
              width: '100%',
              height: '200px',
              overflow: 'hidden',
              display: 'flex',
              justifyContent: 'center',
              alignItems: 'center',
            }}>
              <img 
                src={product.images[0]} 
                alt={product.name} 
                style={{
                  maxWidth: '100%',
                  maxHeight: '100%',
                  objectFit: 'contain',
                }}
              />
            </Box>
          )}
        </CardContent>
      </Card>
    </Grid>
  );

  return (
    <>
      <Helmet>
        <title>{t("NostrChat - Marketplace")}</title>
      </Helmet>
      <AppWrapper>
        <AppMenu />
        <AppContent>
    <Box className="marketplace-container" sx={{
      height: 'calc(100vh - 64px)', // Adjust based on your app's header height
      overflow: 'auto',
      padding: '20px',
    }}>
      <Box className="marketplace-content">
        <TextField
          fullWidth
          label={t('Search products')}
          value={searchQuery}
          onChange={handleSearchChange}
          margin="normal"
        />
        
        <Grid container spacing={2}>
          {currentProducts.map(renderProduct)}
        </Grid>
        <Box sx={{ marginTop: '20px', textAlign: 'center' }}>
          <Button 
            disabled={currentPage === 1} 
            onClick={() => handlePageChange(currentPage - 1)}
          >
            {t('Previous')}
          </Button>
          <span style={{ margin: '0 10px' }}>
            {t('Page {{current}} of {{total}}', { current: currentPage, total: totalPages })}
          </span>
          <Button 
            disabled={currentPage === totalPages} 
            onClick={() => handlePageChange(currentPage + 1)}
          >
            {t('Next')}
          </Button>
        </Box>
      </Box>
    </Box>
       </AppContent>
      </AppWrapper>
    </>
  );
};

export default MarketplacePage;