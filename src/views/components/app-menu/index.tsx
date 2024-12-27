import React, { useState } from 'react';
import ChannelList from 'views/components/app-menu/channel-list';
import DmList from 'views/components/app-menu/dm-list';
import AppMenuBase from 'views/components/app-menu-base';
import { useRecoilValue } from 'recoil';
import { userState } from 'state/userState';
import { Link, navigate } from '@reach/router';

const AppMenu = () => {
  const getUserState: any = useRecoilValue(userState);
  const [showPopup, setShowPopup] = useState(false);

  const handleNostrClick = (e: React.MouseEvent<HTMLAnchorElement, MouseEvent>) => {
    e.preventDefault();
    setShowPopup(true);
  };

  const handleContinue = () => {
    setShowPopup(false);
    navigate('/home');
  };

  const handleCancel = () => {
    setShowPopup(false);
  };

  const popupStyles = {
    position: 'fixed' as 'fixed',
    top: 0,
    left: 0,
    width: '100%',
    height: '100%',
    background: 'rgba(0, 0, 0, 0.5)',
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    zIndex: 1000,
  };

  const popupContentStyles = {
    background: 'black',
    padding: '20px',
    borderRadius: '10px',
    textAlign: 'center' as 'center',
    maxWidth: '400px',
    width: '100%',
  };

  const buttonStyles = {
    margin: '10px',
    padding: '10px 20px',
    border: 'none',
    backgroundColor: '#007BFF',
    color: 'white',
    cursor: 'pointer',
    borderRadius: '5px',
    fontSize: '16px',
  };

  const buttonHoverStyles = {
    backgroundColor: '#0056b3',
  };

  return (
    <AppMenuBase>
      <div className="custom_items">
        <Link to="/">Home</Link>
        <a href="/home" onClick={handleNostrClick}>Nostr</a>
        <Link to="/settings/profile">Profile</Link>
        <Link to="/settings/keys">Keys & Wallet</Link>
        <Link to="/marketplace">Marketplace</Link>
        <a href="http://localhost:8069/" target="_blank" rel="noopener noreferrer">Link to Odoo</a>
        <Link to="/storage">Storage</Link>
        <Link to="/calendar">Calendar</Link>
        <Link to="/relay">Relay (Admin Only!)</Link>
      </div>
      {/* <ChannelList /> */}
      <DmList />
      {showPopup && (
        <div style={popupStyles}>
          <div style={popupContentStyles}>
            <h2>Warning: Age-Restricted Content Ahead</h2>
            <p>
              You are about to enter a section of this site that is restricted to individuals 18 years of age and older. 
              This area contains content that may be inappropriate for underage users.
            </p>
            <button 
              style={buttonStyles} 
              onMouseEnter={(e) => (e.currentTarget.style.backgroundColor = buttonHoverStyles.backgroundColor)} 
              onMouseLeave={(e) => (e.currentTarget.style.backgroundColor = buttonStyles.backgroundColor)} 
              onClick={handleContinue}>
                I confirm that I am at least 18 years old
            </button>
            <button 
              style={buttonStyles} 
              onMouseEnter={(e) => (e.currentTarget.style.backgroundColor = buttonHoverStyles.backgroundColor)} 
              onMouseLeave={(e) => (e.currentTarget.style.backgroundColor = buttonStyles.backgroundColor)} 
              onClick={handleCancel}>
                I am under the age of 18
            </button>
          </div>
        </div>
      )}
    </AppMenuBase>
  );
};

export default AppMenu;
