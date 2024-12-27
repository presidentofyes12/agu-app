import React, {useState} from 'react';
import Menu from '@mui/material/Menu';
import MenuItem from '@mui/material/MenuItem';
import Button from '@mui/material/Button';
import {useNavigate} from '@reach/router';

import CreateChannel from 'views/components/dialogs/create-channel';
import JoinChannel from 'views/components/dialogs/join-channel';
import useTranslation from 'hooks/use-translation';
import useModal from 'hooks/use-modal';
import Plus from 'svg/plus';

const ChannelAddMenu = () => {
    const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
    const navigate = useNavigate();
    const open = Boolean(anchorEl);
    const [t] = useTranslation();
    const [, showModal] = useModal();

    const openMenu = (event: React.MouseEvent<HTMLButtonElement>) => {
        setAnchorEl(event.currentTarget);
    };

    const closeMenu = () => {
        setAnchorEl(null);
    };

    const create = () => {
        showModal({
            body: <CreateChannel onSuccess={(id) => {
                showModal(null);
                navigate(`/channel/${id}`).then();
            }}/>
        })

        closeMenu();
    }

    const join = () => {
        showModal({
            body: <JoinChannel onSuccess={(id) => {
                showModal(null);
                navigate(`/channel/${id}`).then();
            }}/>
        })

        closeMenu();
    }

    return <>
        <button onClick={openMenu}  className='btn btn_success'><Plus height={18}/> New Proposal</button>
        <Menu anchorEl={anchorEl} open={open} onClose={closeMenu}>
            <MenuItem dense onClick={create}>{t('Create a New Proposal')}</MenuItem>
            <MenuItem dense onClick={join}>{t('Join in a Proposal')}</MenuItem>
        </Menu>
    </>
}

export default ChannelAddMenu;