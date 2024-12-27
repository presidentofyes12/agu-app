import React from 'react';
import { Link } from '@reach/router';
import { Stall } from 'types';

interface StallListProps {
  stalls: Stall[];
}

const StallList: React.FC<StallListProps> = ({ stalls }) => {
  return (
    <div>
      {stalls.map((stall) => (
        <div key={stall.id}>
          <Link to={`/marketplace/stall/${stall.id}`}>
            <h2>{stall.name}</h2>
            <p>{stall.description}</p>
          </Link>
        </div>
      ))}
    </div>
  );
};

export default StallList;