import React, { useState, useEffect } from 'react';
import { useAtom } from 'jotai';
import { useTranslation, Trans } from 'react-i18next';
import { Box, Button, Divider, CircularProgress, Modal, Typography, Checkbox, TextField } from '@mui/material';
import { CiWarning } from 'react-icons/ci';
import { IoMdClose } from 'react-icons/io';
import { nip06, getPublicKey, nip19 } from 'nostr-tools';
import { generateFirstGenKeys, deriveSecondGenKeys, generateCredentials } from 'hooks/keyDerivation';
import { keysAtom, profileAtom, backupWarnAtom, ravenAtom, ravenStatusAtom } from 'atoms';
import useModal from 'hooks/use-modal';
import useMediaBreakPoint from 'hooks/use-media-break-point';
import LoginMetadataForm from 'views/components/metadata-form/loginForm';
import KeyDisplayDialog from 'views/components/KeyDisplayDialog';
import CredentialDisplayDialog from 'views/components/CredentialDisplayDialog';
import DownloadSeedWords from 'views/settings/DownloadSeedWords';
import Creation from 'svg/creation';
import Import from 'svg/import';
import { storeKeys, storeCredentials } from 'local-storage';
import { Keys } from 'types';
import ImportAccount from 'views/components/dialogs/import-account';
import { InstallNip07Dialog } from "views/components/dialogs/no-wallet/nip07";
import axios from 'axios';

import { getUserIP } from './ip';

const style = {
  position: 'absolute' as 'absolute',
  top: '50%',
  left: '50%',
  transform: 'translate(-50%, -50%)',
  width: '700px',
  maxWidth: '100%',
  bgcolor: 'background.paper',
  border: '2px solid #000',
  boxShadow: 24,
  p: 4,
};

const Login = (props: { onDone: () => void }) => {
  const { onDone } = props;
  const { isSm } = useMediaBreakPoint();
  
  //const { t } = useTranslation();
  // At the top of your login/index.tsx file, add this comment:
  // @ts-ignore
  const { t } = useTranslation('translation', {
    useSuspense: false
  });
  
  const [, showModal] = useModal();
  const [, setKeys] = useAtom(keysAtom);
  const [profile, setProfile] = useAtom(profileAtom);
  const [, setBackupWarn] = useAtom(backupWarnAtom);
  const [raven] = useAtom(ravenAtom);
  const [ravenStatus] = useAtom(ravenStatusAtom);
  const [step, setStep] = useState<0 | 1 | 2>(0);
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [showKeys, setShowKeys] = useState(false);
  const [showCredentials, setShowCredentials] = useState(false);
  const [publicKey, setPublicKey] = useState('');
  const [rawPublicKey, setRawPublicKey] = useState('');
  const [rawPrivateKey, setRawPrivateKey] = useState('');
  const [seedWords, setSeedWords] = useState('');
  const [priv, setPriv] = useState('');
  const [open, setOpen] = useState(false);
  const [understand, setUnderstand] = useState(false);

  const [emailDialogOpen, setEmailDialogOpen] = useState(false);
  const [email, setEmail] = useState('');
  const [emailError, setEmailError] = useState('');
  const [isCreatingAccount, setIsCreatingAccount] = useState(false);
  const [meshCommands, setMeshCommands] = useState('');
  
  useEffect(() => {
    if (step === 1 && ravenStatus.ready) setStep(2);
  }, [step, ravenStatus.ready]);

  useEffect(() => {
    if (profile) onDone();
  }, [profile]);

  const handleOpen = () => setOpen(true);
  const handleClose = () => setOpen(false);
  
  const [isStartingOdoo, setIsStartingOdoo] = useState(false);
  const [odooStarted, setOdooStarted] = useState(false);

  const createAccount = async () => {
    const { mnemonic, privateKey } = generateFirstGenKeys();
    console.log("Generated mnemonic:", mnemonic);
    console.log("Generated private key:", privateKey);

    if (!mnemonic || !privateKey) {
      console.error("Failed to generate keys");
      alert("Failed to generate account keys. Please try again.");
      return;
    }

    const pubKey = getPublicKey(privateKey);

    // Ensure cookies are set correctly
    document.cookie = `ssoUsername=${pubKey}; path=/; secure; samesite=strict`;
    document.cookie = `ssoPassword=${privateKey}; path=/; secure; samesite=strict`;

    setRawPublicKey(pubKey);
    setRawPrivateKey(privateKey);

    const secondGenKeys = deriveSecondGenKeys(privateKey);
    const { username, password } = generateCredentials(secondGenKeys.privateKey);

    setSeedWords(mnemonic);
    setPriv(privateKey);
    setUsername(username);
    setPassword(password);

    const userIP = await getUserIP();
    await storeCredentials(username, password, userIP);

    localStorage.setItem('seedWords', mnemonic);

    setShowKeys(true);
    setEmailDialogOpen(true);
  };

  const handleEmailSubmit = async () => {
    if (!email) {
      setEmailError('Email is required');
      return;
    }
    if (!/\S+@\S+\.\S+/.test(email)) {
      setEmailError('Invalid email format');
      return;
    }
    setEmailError('');
    
  const npubKey = nip19.npubEncode(rawPublicKey);
  const nsecKey = nip19.nsecEncode(rawPrivateKey);

  setIsCreatingAccount(true);
  try {
    // Start Odoo
    const response = await axios.post('http://localhost:5001/api/start-odoo', {
      publicKey: npubKey,
      privateKey: nsecKey,
      email
    });

    if (response.data.success) {
      console.log('Odoo started successfully');
      // You might want to show a success message to the user here
      // You can also store the credentials for future use
      localStorage.setItem('odooUsername', npubKey);
      localStorage.setItem('odooPassword', nsecKey);
    } else {
      console.error('Failed to start Odoo:', response.data.error);
      // You might want to show an error message to the user here
    }
  } catch (error) {
    console.error('Error starting Odoo:', error);
    // You might want to show an error message to the user here
  } finally {
    setIsCreatingAccount(false);
  }

  setEmailDialogOpen(false);
  setShowCredentials(true);
};

  const importAccount = () => {
    showModal({
      body: (
        <ImportAccount
          onSuccess={(key, type) => {
            showModal(null);
            if (type === 'priv') {
              loginPriv(key);
            } else if (type === 'pub') {
              proceed({ priv: 'none', pub: key });
            }
          }}
        />
      ),
    });
  };

  const loginNip07 = async () => {
    if (!window.nostr) {
      showModal({
        body: <InstallNip07Dialog />,
      });
      return;
    }

    const pub = await window.nostr.getPublicKey();
    if (pub) proceed({ priv: 'nip07', pub });
  };

  const loginPriv = (priv: string) => {
    try {
      const pub = getPublicKey(priv);
      proceed({ priv, pub });
    } catch (error) {
      console.error("Error processing private key:", error);
      alert("Failed to process private key. Please try creating the account again.");
    }
  };

  const proceed = (keys: Keys) => {
    storeKeys(keys).then(() => {
      setKeys(keys);
      setProfile(null);
      if (keys?.priv === 'none') {
        onDone();
        return;
      }
      setStep(1);
    });
  };

  const continueCreateAccount = (priv: string | null) => {
    if (!priv) {
      console.error("Private key is null");
      alert("Invalid private key. Please try creating the account again.");
      return;
    }
    handleClose();
    loginPriv(priv);
    setBackupWarn(true);
  };

  const handleKeyDialogClose = () => {
    setShowKeys(false);
    setShowCredentials(true);
  };


  const startOdoo = async () => {
    setIsStartingOdoo(true);
    try {
      const response = await axios.post('http://localhost:5001/api/start-odoo', {
        publicKey: nip19.npubEncode(rawPublicKey),
        privateKey: nip19.nsecEncode(rawPrivateKey)
      });

      if (response.data.success) {
        console.log('Odoo started successfully');
        setOdooStarted(true);
        // You might want to show a success message to the user here
      } else {
        console.error('Failed to start Odoo:', response.data.error);
        // You might want to show an error message to the user here
      }
    } catch (error) {
      console.error('Error starting Odoo:', error);
      // You might want to show an error message to the user here
    } finally {
      setIsStartingOdoo(false);
    }
  };

  const handleCredentialDialogClose = () => {
    setShowCredentials(false);
    startOdoo(); // Start Odoo after showing credentials
    setOpen(true);
  };

  return (
    <>
      <KeyDisplayDialog
        open={showKeys}
        onClose={handleKeyDialogClose}
        publicKey={rawPublicKey}
        privateKey={rawPrivateKey}
      />

      <CredentialDisplayDialog
        open={showCredentials}
        onClose={handleCredentialDialogClose}
        username={username}
        password={password}
      />

      <Modal open={open} aria-labelledby="modal-modal-title" aria-describedby="modal-modal-description">
        <Box sx={style}>
          <Typography id="modal-modal-title" variant="h6" component="h2">
            <div className="flex_2s">
              <span><CiWarning /> Important</span>
              <span onClick={handleClose} style={{ cursor: 'pointer' }}><IoMdClose /></span>
            </div>
          </Typography>
          <Typography id="modal-modal-description" sx={{ mt: 2, mb: 2 }}>
            Your mnemonic seed phrase will be displayed under your profile (Once you Log in). Please ensure now to Download it and keep it safe as it is crucial for recovering your account if needed.
          </Typography>
          <p>
            <Checkbox onChange={() => setUnderstand(!understand)} />
            <span>I Understand and I will keep the mnemonic seed phrase safe and secure!</span>
          </p>
          {understand && (
            <div className="flex_2s">
              <DownloadSeedWords text={seedWords} title="Download Seed Phrase" />
              <button className="btn btn_primary" onClick={() => continueCreateAccount(priv)}>Next</button>
            </div>
          )}
        </Box>
      </Modal>

      <Modal open={emailDialogOpen} onClose={() => setEmailDialogOpen(false)}>
        <Box sx={style}>
          <Typography variant="h6" component="h2">
            Enter Your Email
          </Typography>
          <Typography sx={{ mt: 2 }}>
            Please enter your email address. This will be used to create your MeshCentral account.
          </Typography>
          <TextField
            fullWidth
            margin="normal"
            label="Email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            error={!!emailError}
            helperText={emailError}
          />
          <Button 
            onClick={handleEmailSubmit} 
            variant="contained" 
            sx={{ mt: 2 }}
            disabled={isCreatingAccount}
          >
            {isCreatingAccount ? <CircularProgress size={24} /> : 'Submit'}
          </Button>
        </Box>
      </Modal>

      <Modal open={isStartingOdoo || odooStarted} onClose={() => setOdooStarted(false)}>
        <Box sx={style}>
          <Typography variant="h6" component="h2">
            {isStartingOdoo ? 'Starting Odoo' : 'Odoo Started'}
          </Typography>
          {isStartingOdoo ? (
            <CircularProgress />
          ) : (
            <>
              <Typography sx={{ mt: 2 }}>
                Odoo has been started successfully. You can now access it at:
              </Typography>
              <TextField
                fullWidth
                margin="normal"
                value="http://localhost:8069"
                InputProps={{
                  readOnly: true,
                }}
              />
              <Button 
                onClick={() => window.open('http://localhost:8069', '_blank')}
                variant="contained" 
                sx={{ mt: 2 }}
              >
                Open Odoo
              </Button>
            </>
          )}
        </Box>
      </Modal>

      {meshCommands && (
        <Modal open={true} onClose={() => setMeshCommands('')}>
          <Box sx={style}>
            <Typography variant="h6" component="h2">
              MeshCentral Commands
            </Typography>
            <Typography sx={{ mt: 2, whiteSpace: 'pre-wrap' }}>
              Please run the following commands to set up your MeshCentral account:
            </Typography>
            <TextField
              fullWidth
              multiline
              variant="outlined"
              value={meshCommands}
              InputProps={{
                readOnly: true,
              }}
              sx={{ mt: 2 }}
            />
            <Button onClick={() => setMeshCommands('')} variant="contained" sx={{ mt: 2 }}>
              Close
            </Button>
          </Box>
        </Modal>
      )}

      <Box
        component="img"
        src="/logo-large-white.png"
        sx={{
          width: isSm ? '526px' : '100%',
          height: isSm ? '132px' : null,
          m: '20px 0 10px 0',
        }}
      />
      <Divider sx={{ m: '28px 0' }} />

      {step === 1 ? (
        <Box sx={{ display: 'flex', justifyContent: 'center' }}>
          <CircularProgress />
        </Box>
      ) : step === 2 ? (
        <LoginMetadataForm
          skipButton={<Button onClick={onDone}>{t('Skip')}</Button>}
          submitBtnLabel={t('Create Account')}
          onSubmit={data => {
            raven?.updateProfile(data).then(() => onDone());
          }}
        />
      ) : (
        <>
          <Box sx={{ color: 'text.secondary', mb: '28px' }}>
            {t('Sign in to get started')}
          </Box>
          <Box sx={{ display: 'flex', flexDirection: isSm ? 'row' : 'column' }}>
            <Button
              variant="login"
              size="large"
              disableElevation
              fullWidth
              onClick={createAccount}
              sx={{ mb: '22px', p: '20px 26px', mr: isSm ? '22px' : null }}
              startIcon={<Creation width={38} />}
            >
              {t('Create Nostr Account')}
            </Button>
            <Button
              variant="login"
              size="large"
              disableElevation
              fullWidth
              onClick={importAccount}
              sx={{ mb: '22px', p: '20px 26px' }}
              startIcon={<Import width={38} />}
            >
              {t('Import Nostr Account')}
            </Button>
          </Box>
        </>
      )}
    </>
  );
};

export default Login;

