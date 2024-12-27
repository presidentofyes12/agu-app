import React from 'react';
import { Grid, Card, CardContent, Typography, Box, Button } from '@mui/material';
import { Link } from '@reach/router';
import { Product, Stall } from 'types';
import useTranslation from 'hooks/use-translation';

interface CombinedListProps {
  stalls: Stall[];
  products: Product[];
}

const CombinedList: React.FC<CombinedListProps> = ({ stalls, products }) => {
  const [t] = useTranslation();

  return (
    <div>
      {stalls.map((stall) => {
        console.log("All products list: ", products);
        console.log("All stalls list: ", stalls);
        const stallProducts = products.filter(product => product.stall_id === stall.id);
        console.log("All products matching to stalls: ", stallProducts);

        return (
          <Box key={stall.id} mb={4}>
            <Link to={`/marketplace/stall/${stall.id}`} style={{ textDecoration: 'none', color: 'inherit' }}>
              <Typography variant="h4" component="h2">{stall.name}</Typography>
              <Typography variant="body1" mb={2}>{stall.description}</Typography>
            </Link>
            {stallProducts.length > 0 ? (
              <Grid container spacing={2}>
                {stallProducts.map((product) => (
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
            ) : (
              <Typography variant="body1">{t('No products available for this stall')}</Typography>
            )}
          </Box>
        );
      })}
    </div>
  );
};

export default CombinedList;