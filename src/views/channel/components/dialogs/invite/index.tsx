import React, { useState } from 'react';
import DialogContent from '@mui/material/DialogContent';
import DialogTitle from '@mui/material/DialogTitle';
import Box from '@mui/material/Box';
import TextField from '@mui/material/TextField';
import InputAdornment from '@mui/material/InputAdornment';
import Select, { SelectChangeEvent } from '@mui/material/Select';
import MenuItem from '@mui/material/MenuItem';
import Button from '@mui/material/Button';

import CloseModal from 'components/close-modal';
import CopyToClipboard from 'components/copy-clipboard';
import useModal from 'hooks/use-modal';
import useTranslation from 'hooks/use-translation';
import IconButton from '@mui/material/IconButton';
import ContentCopy from 'svg/content-copy';
import { Channel, DirectContact } from 'types';
import { useAtom } from 'jotai';
import { ravenAtom, keysAtom, profilesAtom } from 'atoms';
import useLiveDirectContacts from 'hooks/use-live-direct-contacts';
import { truncateMiddle } from 'util/truncate';

const Invite = (props: { channel: Channel }) => {
    const { channel } = props;
    const [, showModal] = useModal();
    const [t] = useTranslation();
    const [selectedContact, setSelectedContact] = useState('');
    const [raven] = useAtom(ravenAtom);
    const [keys] = useAtom(keysAtom);
    const [profiles] = useAtom(profilesAtom);
    const directContacts = useLiveDirectContacts();

    const handleClose = () => {
        showModal(null);
    };

    const url = `${window.location.protocol}//${window.location.host}/channel/${channel.id}`;

    const handleContactChange = (event: SelectChangeEvent<string>) => {
        setSelectedContact(event.target.value);
    };

    const handleInvite = () => {
        if (selectedContact && raven && keys?.pub) {
            const message = `User with public key ${keys.pub} invited this proposal: ${channel.id}`;
            raven.sendDirectMessage(selectedContact, message);
            alert('Invitation sent successfully!');
        }
    };

    const getContactLabel = (contact: DirectContact) => {
        const profile = profiles.find(x => x.creator === contact.pub);
        return profile?.name || truncateMiddle(contact.npub, 28, ':');
    };

    return (
        <>
            <DialogTitle>{t('Invite People')}<CloseModal onClick={handleClose}/></DialogTitle>
            <DialogContent>
                <Box sx={{pt: '10px'}}>
                    <TextField
                        label="Invitation Link"
                        value={url}
                        fullWidth
                        InputProps={{
                            endAdornment: <InputAdornment position="end">
                                <CopyToClipboard copy={url}>
                                    <IconButton><ContentCopy height={18}/></IconButton>
                                </CopyToClipboard>
                            </InputAdornment>,
                        }}
                    />
                </Box>
                <Box sx={{pt: '10px'}}>
                    <p>OR</p>
                    <TextField
                        label="Proposal ID"
                        value={channel.id}
                        fullWidth
                        InputProps={{
                            endAdornment: <InputAdornment position="end">
                                <CopyToClipboard copy={channel.id}>
                                    <IconButton><ContentCopy height={18}/></IconButton>
                                </CopyToClipboard>
                            </InputAdornment>,
                        }}
                    />
                </Box>
                <Box sx={{pt: '20px'}}>
                    <p>OR</p>
                    <Select
                        value={selectedContact}
                        onChange={handleContactChange}
                        fullWidth
                        displayEmpty
                        inputProps={{ 'aria-label': 'Select contact' }}
                    >
                        <MenuItem value="" disabled>
                            Select a contact to invite
                        </MenuItem>
                        {directContacts.map((contact) => (
                            <MenuItem key={contact.pub} value={contact.pub}>
                                {getContactLabel(contact)}
                            </MenuItem>
                        ))}
                    </Select>
                    <Button 
                        onClick={handleInvite} 
                        disabled={!selectedContact}
                        fullWidth
                        variant="contained"
                        sx={{mt: 2}}
                    >
                        Invite Selected Contact
                    </Button>
                </Box>
            </DialogContent>
        </>
    );
}

export default Invite;