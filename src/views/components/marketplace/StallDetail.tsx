import React, { useEffect, useState } from 'react';
import { RouteComponentProps } from '@reach/router';
import { useMarketplace } from 'hooks/useMarketplace';
import { Stall, Product } from 'types';
import ProductList from './ProductList';

interface StallDetailProps extends RouteComponentProps {
  stallId?: string;
}

const StallDetail: React.FC<StallDetailProps> = ({ stallId }) => {
  const { stalls, products } = useMarketplace();
  const [stall, setStall] = useState<Stall | null>(null);
  const [stallProducts, setStallProducts] = useState<Product[]>([]);

  useEffect(() => {
    if (stallId) {
      // TODO: Fetch stall details and products
    }
  }, [stallId]);

  if (!stall) {
    return <div>Loading...</div>;
  }

  return (
    <div>
      <h1>{stall.name}</h1>
      <p>{stall.description}</p>
      <ProductList products={stallProducts} />
    </div>
  );
};

export default StallDetail;