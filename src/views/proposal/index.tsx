import React from 'react';
import { Helmet } from 'react-helmet';
import { RouteComponentProps } from '@reach/router';
import { Card, CardContent } from '@mui/material';
import AppWrapper from 'views/components/app-wrapper';
import AppMenu from 'views/components/app-menu';
import DashboardContent from 'views/components/app-content/DashboardContent';
import ChannelList from 'views/components/app-menu/channel-list';
import logo from './AGU_logo_fully_transparent.png'; // Ensure the correct path to the logo

const Proposal = (props: RouteComponentProps) => {
  return (
    <>
      <Helmet>
        <title>Proposal</title>
      </Helmet>
      <AppWrapper>
        <AppMenu />
        <DashboardContent>
          <div className="row">
            <div className="mt-5 col-12 col-md-8 offset-md-2">
              <Card>
                <CardContent>
                  <div className='proposal_history'>
                    <ChannelList />
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>
        </DashboardContent>
        <img src={logo} alt="AGU Logo" className="agu-logo" />
      </AppWrapper>
      <style>{`
        .agu-logo {
          position: absolute;
          top: 10px;
          left: 275px; /* Adjust the left value as needed to position the logo */
          width: 200px; /* Adjust the size as needed */
          height: auto;
        }
        .proposal_history {
          position: relative;
        }
      `}</style>
    </>
  );
}

export default Proposal;
