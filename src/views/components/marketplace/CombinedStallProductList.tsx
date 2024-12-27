import React from 'react';
import { Link } from '@reach/router';
import { Box, Typography, Grid, Card, CardContent, Button } from '@mui/material';
import { Stall, Product } from 'types';
import useTranslation from 'hooks/use-translation';

interface CombinedStallProductListProps {
  stalls: Stall[];
  products: Product[];
}

const CombinedStallProductList: React.FC<CombinedStallProductListProps> = ({ stalls, products }) => {
  const [t] = useTranslation();
  console.log("Every stall: ", stalls);
  console.log("Every product: ", products);
  stalls.map((stall) => {
    const stallProducts = products.filter(product => product.id === stall.id);
    //console.log("All products with matching stalls: ", stallProducts);
  });
  return (
    <Box>
      {stalls.map((stall) => (
        <Box key={stall.id} mb={4}>
          <Typography variant="h4" component="h2">
            <Link to={`/marketplace/stall/${stall.id}`} style={{ textDecoration: 'none', color: 'inherit' }}>
              {stall.name}
            </Link>
          </Typography>
          <Typography variant="body1" mb={2}>{stall.description}</Typography>
          <Grid container spacing={2}>
            {products
              .filter(product => product.stall_id === stall.id)
              .map((product) => (
                <Grid item xs={12} sm={6} md={4} key={product.id}>
                  <Card>
                    <CardContent>
                      <Typography variant="h6" component="h3">{product.name}</Typography>
                      <Typography variant="body2">{product.description}</Typography>
                      <Typography variant="body1" mt={1}>
                        {t('Price: {{price}} {{currency}}', { price: product.price, currency: product.currency })}
                      </Typography>
                      <Link to={`/marketplace/product/${product.id}`}>
                        <Button variant="contained" color="primary" sx={{ mt: 2 }}>
                          {t('View Details')}
                        </Button>
                      </Link>
                    </CardContent>
                  </Card>
                </Grid>
              ))}
          </Grid>
        </Box>
      ))}
    </Box>
  );
};

export default CombinedStallProductList;
