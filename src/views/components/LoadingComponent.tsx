import React from 'react';
import './loading.css'
const LoadingComponent = () => {
  return (
    <div className='loading_page'>
      <div className='lds_roller'>
        <div></div>
        <div></div>
        <div></div>
        <div></div>
        <div></div>
        <div></div>
        <div></div>
        <div></div>
      </div>
    </div>
  );
};

export default LoadingComponent;
