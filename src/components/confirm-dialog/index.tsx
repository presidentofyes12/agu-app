import React from 'react';
import DialogTitle from '@mui/material/DialogTitle';
import DialogContent from '@mui/material/DialogContent';
import Button from '@mui/material/Button';
import DialogActions from '@mui/material/DialogActions';
import {DialogContentText} from '@mui/material';

import useTranslation from '../../hooks/use-translation';
import useModal from '../../hooks/use-modal';
import CloseModal from '../close-modal';

const ConfirmDialog = (props: {onConfirm: () => void}) => {
    const [t] = useTranslation();
    const [, showModal] = useModal();

    const handleClose = () => {
        showModal(null);
    };

    const handleConfirm = () => {
        props.onConfirm();
        showModal(null);
    }

    return (
        <div className='p-3'>
            <DialogTitle>{t('Confirmation')}
                <CloseModal onClick={handleClose}/>
            </DialogTitle>
            <DialogContent>
                <DialogContentText>{t('Are you sure?')}</DialogContentText>
            </DialogContent>
            <DialogActions>
                <button className=' btn btn_success' onClick={handleClose}>{t('Cancel')}</button>
                <button className=' btn btn_primary' onClick={handleConfirm}>{t('Confirm')}</button>
            </DialogActions>
        </div>
    );
}

export default ConfirmDialog;
