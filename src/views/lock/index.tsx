import React, { useEffect, useState } from "react";
import { Link, RouteComponentProps, useNavigate } from "@reach/router";
import Box from "@mui/material/Box";
import Card from "@mui/material/Card";
import { Helmet } from "react-helmet";
import useMediaBreakPoint from "hooks/use-media-break-point";
import useTranslation from "hooks/use-translation";
import { toast } from "react-toastify";
import { FaLockOpen } from "react-icons/fa";

import { getCredentials, getKeys } from 'local-storage';
import { storeKeys, storeCredentials } from 'local-storage';
import { getPublicKey } from 'nostr-tools';
import { deriveSecondGenKeys, generateCredentials } from 'hooks/keyDerivation';
import { nip06 } from 'nostr-tools';
//import { privateKeyFromSeedWords } from 'nostr-tools';
import CredentialDisplayDialog from 'views/components/CredentialDisplayDialog';
import { getUserIP } from './ip';

const LockPage = (_: RouteComponentProps) => {
  const { isSm } = useMediaBreakPoint();
  const [isAccountExist, setIsAccountExist] = useState(false);
  const [isAccountLoading, setIsAccountLoading] = useState(true);
  const [username, setUsername] = useState('');
  const [enteredPassword, setEnteredPassword] = useState('');
  const [t] = useTranslation();
  const [recoveredUsername, setRecoveredUsername] = useState('');
  const [recoveredPassword, setRecoveredPassword] = useState('');
  const [showRecoveredCredentials, setShowRecoveredCredentials] = useState(false);


  useEffect(() => {
    const storedPassword = window.localStorage.getItem("password");
    if (storedPassword) {
      setIsAccountExist(true);
      setEnteredPassword(storedPassword);
    } else {
      setIsAccountExist(false);
    }
    setIsAccountLoading(false);
  }, []);

  const handleCreateAccount = async () => {
    const userIP = await getUserIP();
    await storeCredentials(username, enteredPassword, userIP);
    window.localStorage.setItem("initLock", "initLock");
    setIsAccountExist(true);
    alert("Account created successfully!");
  };

  const handleLogin = async () => {
    const storedCredentials = await getCredentials();
    const currentIP = await getUserIP();
    
    if (storedCredentials) {
      const matchedCredential = storedCredentials.find(
        cred => cred.username === username && cred.password === enteredPassword
      );

      if (matchedCredential) {
        if (matchedCredential.ip === currentIP) {
          const keys = await getKeys();
          if (keys) {
            localStorage.setItem("auth", "true");
            localStorage.removeItem('isLocked');
            window.location.href = "/home";
          } else {
            alert("Error: Keys not found. Please reset your account.");
          }
        } else {
          alert("Unauthorized device. Please use the device you created your account with.");
        }
      } else {
        alert("Invalid username or password. Please try again.");
      }
    } else {
      alert("No stored credentials found. Please create an account first.");
    }
  };

  if (isAccountLoading) {
    return <div>Loading...</div>;
  }

  const handleReset = () => {
    const result = window.confirm("Are you sure  ? To reset your password ? ");
    if (result) {
      window.localStorage.removeItem("username");
      window.localStorage.removeItem("password");
      window.localStorage.removeItem("initLock");
      window.localStorage.removeItem("keys")
      window.localStorage.removeItem("auth")
      window.location.href="/login"
    }
  };

  const handleRecovery = async (firstGenMnemonic: string) => {
    try {
      const firstGenPrivateKey = nip06.privateKeyFromSeedWords(firstGenMnemonic);
      const secondGen = deriveSecondGenKeys(firstGenPrivateKey);
      const credentials = generateCredentials(secondGen.privateKey);
      
      await storeKeys({ pub: getPublicKey(secondGen.privateKey), priv: secondGen.privateKey });
      
      const userIP = await getUserIP();
      await storeCredentials(credentials.username, credentials.password, userIP);
      
      setRecoveredUsername(credentials.username);
      setRecoveredPassword(credentials.password);
      setShowRecoveredCredentials(true);
    } catch (error) {
      console.error('Error in handleRecovery:', error);
      toast("Failed to recover account. Please try again.");
    }
  };
  
  return (
    <>
      <Helmet>
        <title>{t("Locked")}</title>
      </Helmet>
      <Box sx={{ width: isSm ? "590px" : "96%" }}>
        <Card sx={{ p: "26px 32px 46px 32px" }} className="auth_form">
          {isAccountExist ? (
            <>
              <h4 className="text-center">UnLock Screen</h4>
              <div>
                <div>
                  <input
                    type="text"
                    placeholder="Enter username"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                  />
                  <input
                    type="password"
                    placeholder="Enter password"
                    value={enteredPassword}
                    onChange={(e) => setEnteredPassword(e.target.value)}
                  />
                  <button
                    className="mr-3 btn btn_success"
                    onClick={handleLogin}
                  >
                    <span className="mr-2">
                      <FaLockOpen />
                    </span>
                    UnLock
                  </button>
                  <button
                    onClick={(e) => handleReset()}
                    className=" btn btn_success"
                  >
                    Account Reset by Nsec{" "}
                  </button>
                  <button
                    onClick={(e) => handleRecovery("rifle sure pitch cause camera burden iron stairs riot idea ankle argue")}
                    className=" btn btn_success"
                  >
                    Credentials Test{" "}
                  </button>
                </div>
              </div>
            </>
          ) : (
            <>
              {window.localStorage.getItem("keys") ? (
                <>
                  <h4 className="text-center">Setup Password</h4>
                  <div>
                    <input
                      className="form-control"
                      type="text"
                      placeholder="Enter username"
                      value={username}
                      onChange={(e) => setUsername(e.target.value)}
                    />
                    <input
                      className="form-control"
                      type="password"
                      placeholder="Enter password"
                      value={enteredPassword}
                      onChange={(e) => setEnteredPassword(e.target.value)}
                    />
                    <button
                      className="btn btn_success mt-3 mr-3"
                      onClick={handleCreateAccount}
                    >
                      Setup Password
                    </button>
                    <Link to="/login">
                      <button className="btn btn_primary mt-3 mr-3">
                        Create/Import Account
                      </button>
                    </Link>
                  </div>
                </>
              ) : (
                <>
                  <h4 className="text-center">No Account Founded </h4>
                  <p>
                    Please login to Nostr Account and Setup Password at first{" "}
                  </p>
                  <div>
                    <Link to="/login">
                      <button className="btn btn_primary mt-3 mr-3">
                        Create/Import Account
                      </button>
                    </Link>
                  </div>
                </>
              )}
            </>
          )}
        </Card>
      </Box>
    <CredentialDisplayDialog
      open={showRecoveredCredentials}
      onClose={() => setShowRecoveredCredentials(false)}
      username={recoveredUsername}
      password={recoveredPassword}
    />
    </>
  );
};

export default LockPage;
