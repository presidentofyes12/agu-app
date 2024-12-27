// External imports first
import React, { useEffect, useState } from 'react';
import { useAtom } from 'jotai';
import { RouteComponentProps, useNavigate } from '@reach/router';
import { Card, CardContent } from '@mui/material';
import { Button } from '@mui/material';

import Tooltip from '@mui/material/Tooltip';
import TextField from '@mui/material/TextField';
import Box from '@mui/material/Box';
import InputAdornment from '@mui/material/InputAdornment';
import IconButton from '@mui/material/IconButton';
import { useTheme } from '@mui/material/styles';
import { Helmet } from 'react-helmet';
import { nip19 } from 'nostr-tools';
import useTranslation from 'hooks/use-translation';
import AppWrapper from 'views/components/app-wrapper';
import AppContent from 'views/components/app-content';
import SettingsMenu from 'views/settings/components/settings-menu';
import SettingsHeader from 'views/settings/components/settings-header';
import SettingsContent from 'views/settings/components/settings-content';
import { toast } from 'react-toastify';
import CopyToClipboard from 'components/copy-clipboard';
import { keysAtom } from 'atoms';
import ContentCopy from 'svg/content-copy';
import Information from 'svg/information';
import { generateWeb3Profile } from 'util/function';

// Then local imports
import DownloadSeedWords from "./DownloadSeedWords"
import { useModularDAO } from '../../hooks/useModularDAO';
import { balanceAtom, isConnectedAtom, accountAtom } from '../../state/web3State';

const SettingsKeysPage = (_: RouteComponentProps) => {
  const [keys] = useAtom(keysAtom);
  const navigate = useNavigate();
  const theme = useTheme();
  const [t] = useTranslation();
  const [reveal, setReveal] = useState(false);
  const [revealWS, setRevealWS] = useState(false);
  const [revealSP, setRevealSP] = useState(false);
  const [isConnected] = useAtom(isConnectedAtom);
  const [account] = useAtom(accountAtom);
  const { connectWallet } = useModularDAO();
  const [web3Profile, setWeb3Profile] = useState<any>({
    wsec: 'Loading',
    wpub: 'Loading',
    balance: 'Loading',
  });
  const initWeb3Wallet = async (isToast: boolean) => {
    if (keys) {
      const w3Profile = await generateWeb3Profile(keys.priv);
      setWeb3Profile({ ...w3Profile });
      if (isToast) {
        toast('Wallet Refrashed !');
      }
    }
  };
  useEffect(() => {
    if (!keys) {
      navigate('/login').then();
    }
    initWeb3Wallet(false);
  }, [keys]);

  if (!keys) {
    return null;
  }

  const pub = nip19.npubEncode(keys.pub);

  return (
    <>
      <Helmet>
        <title>{t('NostrChat - Keys')}</title>
      </Helmet>
      <AppWrapper>
        <SettingsMenu />
        <AppContent>
          <SettingsHeader section={t('Keys')} />
          <SettingsContent>
            {localStorage.getItem('seedWords') ? (
              <div className="col-12 col-md-8 offset-md-2 mb-5">
                <Card>
                  <CardContent>
                    <div className="nostr_keys">
                      <h4> Mnemonic Seed Phrase</h4>
                      <hr />

                      <TextField
                        sx={{ mb: '30px' }}
                        label={t('Your Seed Phrase')}
                        value={
                          revealSP
                            ? localStorage.getItem('seedWords')
                            : 'x'.repeat(64)
                        }
                        fullWidth
                        type={revealSP ? 'text' : 'password'}
                        helperText={
                          <Box
                            component="span"
                            sx={{
                              fontWeight: 'bold',
                              color: theme.palette.warning.main,
                              fontSize: '18px',
                              opacity: 0.7,
                            }}
                          >
                            {t(
                              'Important: Your mnemonic seed phrase has been displayed under your user profile. Please ensure to keep it safe as it is crucial for recovering your account if needed.'
                            )}
                          </Box>
                        }
                        InputProps={{
                          readOnly: true,
                          endAdornment: (
                            <InputAdornment position="end">
                              <Tooltip title={reveal ? t('Hide') : t('Reveal')}>
                                <IconButton
                                  onClick={() => {
                                    setRevealSP(!revealSP);
                                  }}
                                >
                                  {revealSP ? (
                                    <>
                                      <button className="btn btn_success">
                                        Hide
                                      </button>
                                    </>
                                  ) : (
                                    <>
                                      <button className="btn btn_success">
                                        Show
                                      </button>
                                    </>
                                  )}
                                </IconButton>
                              </Tooltip>
                              <CopyToClipboard
                                copy={`${localStorage.getItem('seedWords')}`}
                              >
                                <IconButton>
                                  <ContentCopy height={22} />
                                </IconButton>
                              </CopyToClipboard>
                            </InputAdornment>
                          ),
                        }}
                      />
                      <DownloadSeedWords
                        text={`${localStorage.getItem('seedWords')}`}
                        title=""
                      />
                    </div>
                  </CardContent>
                </Card>
              </div>
            ) : (
              ''
            )}
            <div className="col-12 col-md-8 offset-md-2">
              <Card>
                <CardContent>
                  <div className="nostr_keys">
                    <h4>Nostr Keys</h4>
                    <hr />
                    {(() => {
                      if (keys?.priv === 'nip07' || keys?.priv === 'none') {
                        return (
                          <Box
                            sx={{
                              mb: '50px',
                              color: theme.palette.text.secondary,
                              fontSize: '0.8em',
                              display: 'flex',
                              alignItems: 'center',
                            }}
                          >
                            <Information height={18} />
                            <Box sx={{ ml: '6px' }}>
                              {keys?.priv === 'nip07'
                                ? t(
                                    'See your private key on the extension app.'
                                  )
                                : t('No private key provided.')}
                            </Box>
                          </Box>
                        );
                      }

                      const priv = nip19.nsecEncode(keys.priv);
                      return (
                        <>
                          <Box
                            sx={{
                              mb: '30px',
                              color: theme.palette.text.secondary,
                              fontSize: '0.8em',
                            }}
                          >
                            {t(
                              'Please make sure you save a copy of your private key.'
                            )}
                          </Box>
                          <TextField
                            sx={{ mb: '30px' }}
                            label={t('Private key')}
                            value={reveal ? priv : 'x'.repeat(64)}
                            fullWidth
                            type={reveal ? 'text' : 'password'}
                            helperText={
                              <Box
                                component="span"
                                sx={{
                                  fontWeight: 'bold',
                                  color: theme.palette.warning.main,
                                  opacity: 0.7,
                                }}
                              >
                                {t(
                                  'This is your Nostr private key. Do not share it with anyone else!'
                                )}
                              </Box>
                            }
                            InputProps={{
                              readOnly: true,
                              endAdornment: (
                                <InputAdornment position="end">
                                  <Tooltip
                                    title={reveal ? t('Hide') : t('Reveal')}
                                  >
                                    <IconButton
                                      onClick={() => {
                                        setReveal(!reveal);
                                      }}
                                    >
                                      {reveal ? (
                                        <>
                                          <button className="btn btn_success">
                                            Hide
                                          </button>
                                        </>
                                      ) : (
                                        <>
                                          <button className="btn btn_success">
                                            Show
                                          </button>
                                        </>
                                      )}
                                    </IconButton>
                                  </Tooltip>
                                  <CopyToClipboard copy={priv}>
                                    <IconButton>
                                      <ContentCopy height={22} />
                                    </IconButton>
                                  </CopyToClipboard>
                                </InputAdornment>
                              ),
                            }}
                          />
                        </>
                      );
                    })()}
                    <TextField
                      label={t('Public key')}
                      value={pub}
                      fullWidth
                      InputProps={{
                        readOnly: true,
                        endAdornment: (
                          <InputAdornment position="end">
                            <CopyToClipboard copy={pub}>
                              <IconButton>
                                <ContentCopy height={22} />
                              </IconButton>
                            </CopyToClipboard>
                          </InputAdornment>
                        ),
                      }}
                    />
                  </div>
                  <div className="web3_keys mt-5">
                    <h4 onClick={e => console.log()}>Web3 Wallet Keys</h4>
                    <hr />
                    <h5>
                      Your Balance is :{' '}
                      <span className="color_text">{web3Profile.balance}</span>{' '}
                    </h5>
                    <TextField
                      label={t('Web3 Wallet Private key')}
                      value={revealWS ? web3Profile.wsec : 'x'.repeat(64)}
                      type={!revealWS ? 'password' : 'text'}
                      style={{ marginBottom: '20px', marginTop: '20px' }}
                      helperText={
                        <Box
                          component="span"
                          sx={{
                            fontWeight: 'bold',
                            color: theme.palette.warning.main,
                            opacity: 0.7,
                          }}
                        >
                          {t(
                            'This is your Web3 private key. Do not share it with anyone else!'
                          )}
                        </Box>
                      }
                      fullWidth
                      InputProps={{
                        readOnly: true,
                        endAdornment: (
                          <InputAdornment position="end">
                            <Tooltip title={revealWS ? t('Hide') : t('Reveal')}>
                              <IconButton
                                onClick={() => {
                                  setRevealWS(!revealWS);
                                }}
                              >
                                {revealWS ? (
                                  <>
                                    <button className="btn btn_success">
                                      Hide
                                    </button>
                                  </>
                                ) : (
                                  <>
                                    <button className="btn btn_success">
                                      Show
                                    </button>
                                  </>
                                )}
                              </IconButton>
                            </Tooltip>
                            <CopyToClipboard copy={web3Profile.wsec}>
                              <IconButton>
                                <ContentCopy height={22} />
                              </IconButton>
                            </CopyToClipboard>
                          </InputAdornment>
                        ),
                      }}
                    />
                    <TextField
                      label={t('Public key')}
                      value={web3Profile.wpub}
                      fullWidth
                      InputProps={{
                        readOnly: true,
                        endAdornment: (
                          <InputAdornment position="end">
                            <CopyToClipboard copy={web3Profile.wpub}>
                              <IconButton>
                                <ContentCopy height={22} />
                              </IconButton>
                            </CopyToClipboard>
                          </InputAdornment>
                        ),
                      }}
                    />
                    <div style={{ textAlign: 'right' }}>
                      <button
                        className="btn btn_success mt-5"
                        onClick={e => initWeb3Wallet(true)}
                      >
                        {' '}
                        Refrash Wallet{' '}
                      </button>
                    </div>
                  </div>
                </CardContent>
              </Card>
                    {!isConnected && (
                      <Button 
                        onClick={connectWallet}
                        className="btn btn_success"
                      >
                       Connect Wallet
                      </Button>
                    )}
            </div>
          </SettingsContent>
        </AppContent>
      </AppWrapper>
    </>
  );
};

export default SettingsKeysPage;
