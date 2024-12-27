import React, { useEffect, useState } from "react";
import { RouteComponentProps, useNavigate } from "@reach/router";

const OtherPage = (_: RouteComponentProps) => {
  return (
    <>
      <div className="center_vh">
        <div className="center_vh_content">
          <h4>You are not Authenticated !!!</h4>
          <a className="btn btn_success" href="/lock">
            Go to Login Page
          </a>
        </div>
      </div>
    </>
  );
};

export default OtherPage;
