import React, { useEffect, useState } from 'react';
import { RouteComponentProps } from '@reach/router';
import { useMarketplace } from 'hooks/useMarketplace';
import { Stall, Order } from 'types';

const MerchantDashboard: React.FC<RouteComponentProps> = () => {
  const { stalls } = useMarketplace();
  const [merchantStalls, setMerchantStalls] = useState<Stall[]>([]);
  const [pendingOrders, setPendingOrders] = useState<Order[]>([]);

  useEffect(() => {
    // TODO: Fetch merchant's stalls and pending orders
  }, []);

  const handleCreateStall = () => {
    // TODO: Implement create stall functionality
  };

  const handleCreateProduct = (stallId: string) => {
    // TODO: Implement create product functionality
  };

  const handleUpdateOrderStatus = (orderId: string, status: string) => {
    // TODO: Implement update order status functionality
  };

  return (
    <div>
      <h1>Merchant Dashboard</h1>
      <h2>Your Stalls</h2>
      {merchantStalls.map((stall) => (
        <div key={stall.id}>
          <h3>{stall.name}</h3>
          <button onClick={() => handleCreateProduct(stall.id)}>Add Product</button>
        </div>
      ))}
      <button onClick={handleCreateStall}>Create New Stall</button>
      <h2>Pending Orders</h2>
      {pendingOrders.map((order) => (
        <div key={order.id}>
          <h3>Order #{order.id}</h3>
          <p>Status: {order.status}</p>
          <button onClick={() => handleUpdateOrderStatus(order.id, 'shipped')}>Mark as Shipped</button>
        </div>
      ))}
    </div>
  );
};

export default MerchantDashboard;