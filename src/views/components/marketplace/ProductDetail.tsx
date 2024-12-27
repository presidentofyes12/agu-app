import React, { useEffect, useState } from 'react';
import { RouteComponentProps } from '@reach/router';
import { useMarketplace } from 'hooks/useMarketplace';
import { Product } from 'types';

interface ProductDetailProps extends RouteComponentProps {
  productId?: string;
}

const ProductDetail: React.FC<ProductDetailProps> = ({ productId }) => {
  const { products } = useMarketplace();
  const [product, setProduct] = useState<Product | null>(null);

  useEffect(() => {
    if (productId) {
      // TODO: Fetch product details
    }
  }, [productId]);

  const handleAddToCart = () => {
    // TODO: Implement add to cart functionality
  };

  if (!product) {
    return <div>Loading...</div>;
  }

  return (
    <div>
      <h1>{product.name}</h1>
      <p>{product.description}</p>
      <p>Price: {product.price} {product.currency}</p>
      <button onClick={handleAddToCart}>Add to Cart</button>
    </div>
  );
};

export default ProductDetail;