import React, { useState } from 'react';
import Button from '@mui/material/Button';
import DialogActions from '@mui/material/DialogActions';
import DialogContent from '@mui/material/DialogContent';
import DialogTitle from '@mui/material/DialogTitle';
import { TextField } from '@mui/material';
import { nip06, nip19 } from 'nostr-tools';
import { DecodeResult } from 'nostr-tools/lib/nip19';

import CloseModal from 'components/close-modal';
import useModal from 'hooks/use-modal';
import useTranslation from 'hooks/use-translation';
import { toast } from 'react-toastify';

const ImportAccount = (props: {
  onSuccess: (key: string, type: 'pub' | 'priv') => void;
}) => {
  const { onSuccess } = props;
  const [, showModal] = useModal();
  const [t] = useTranslation();
  const [userKey, setUserKey] = useState('');
  const [isInvalid, setIsInvalid] = useState(false);
  const [seed, setSeed] = useState(false);
  const [seedText, setSeedText] = useState('');

  const handleClose = () => {
    showModal(null);
  };

  const handleSubmit = () => {
    if (seed) {
      try {
        const priv = nip06.privateKeyFromSeedWords(seedText);
        onSuccess(priv, 'priv');
      } catch (error: any) {
        if (error.message) {
          toast.error(error.message);
        } else {
          toast.error('Invalid Mnemonic or try later again !');
        }
      }
    } else {
      if (userKey.startsWith('nsec') || userKey.startsWith('npub')) {
        let dec: DecodeResult;
        try {
          dec = nip19.decode(userKey);
          console.log('decoded', dec);
        } catch (e) {
          setIsInvalid(true);
          return;
        }

        const key = dec.data as string;
        if (dec.type === 'nsec') {
          onSuccess(key, 'priv');
        } else if (dec.type === 'npub') {
          onSuccess(key, 'pub');
        } else {
          setIsInvalid(true);
        }
      } else {
        setIsInvalid(true);
      }
    }
  };

  const handleUserKeyChange = (
    e: React.ChangeEvent<HTMLTextAreaElement | HTMLInputElement>
  ) => {
    setUserKey(e.target.value);
    setIsInvalid(false);
  };

  return (
    <>
      <DialogTitle>
        {t('Import Account')}
        <CloseModal onClick={handleClose} />
      </DialogTitle>
      <DialogContent sx={{ pb: '0' }}>
        {!seed ? (
          <TextField
            fullWidth
            autoComplete="off"
            autoFocus
            value={userKey}
            onChange={handleUserKeyChange}
            placeholder={t('Enter nsec or npub')}
            error={isInvalid}
            helperText={isInvalid ? t('Invalid key') : ' '}
            inputProps={{
              autoCorrect: 'off',
            }}
            onKeyPress={e => {
              if (e.key === 'Enter') {
                handleSubmit();
              }
            }}
          />
        ) : (
          <TextField
            fullWidth
            autoComplete="off"
            autoFocus
            value={seedText}
            onChange={e => setSeedText(e.target.value)}
            placeholder={t('Enter  mnemonic seed phrase')}
            error={isInvalid}
            helperText={isInvalid ? t('Invalid mnemonic') : ' '}
            inputProps={{
              autoCorrect: 'off',
            }}
            onKeyPress={e => {
              if (e.key === 'Enter') {
                handleSubmit();
              }
            }}
          />
        )}
      </DialogContent>
      <DialogActions style={{ padding: '0 23px', margin: '30px 0 ' }}>
        <div className="flex_2s" style={{ width: '100%' }}>
          <button className="btn btn_primary" onClick={e => setSeed(!seed)}>
            {!seed ? t('Login by Seed Phrase') : t('Login by nsec or npub')}
          </button>
          <button className="btn btn_success" onClick={handleSubmit}>
            {t('Submit')}
          </button>
        </div>
      </DialogActions>
    </>
  );
};

export default ImportAccount;
