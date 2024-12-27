import React, { useState, useMemo } from 'react';
import { Box, Button } from '@mui/material';
import { useTheme } from '@mui/material/styles';
import { useAtom } from 'jotai';
import { useLocation, useNavigate } from '@reach/router';
import useTranslation from 'hooks/use-translation';
import ListItem from 'views/components/app-menu/list-item';
import StartDM from 'views/components/dialogs/start-dm'; // Ensure this import is correct
import useLiveDirectContacts from 'hooks/use-live-direct-contacts';
import useLiveDirectMessages from 'hooks/use-live-direct-messages';
import useModal from 'hooks/use-modal'; // Ensure this import is correct
import { directMessageAtom, directMessagesAtom, keysAtom, profilesAtom, readMarkMapAtom, showRequestsAtom, ravenAtom } from 'atoms';
import Plus from 'svg/plus';
import { DirectContact } from 'types';
import { truncateMiddle } from 'util/truncate';

const DmListItem = (props: { contact: DirectContact, onAddUserClick: (contact: DirectContact) => void, isDmRequest: boolean }) => {
    const { contact, onAddUserClick, isDmRequest } = props;
    const navigate = useNavigate();
    const [profiles] = useAtom(profilesAtom);
    const [directMessage] = useAtom(directMessageAtom);
    const [readMarkMap] = useAtom(readMarkMapAtom);
    const [keys] = useAtom(keysAtom);
    const location = useLocation();
    const messages = useLiveDirectMessages(contact.pub);

    const lMessage = messages[messages.length - 1];
    const hasUnread = keys?.priv !== 'none' && !!(readMarkMap[contact.pub] && lMessage && lMessage.created > readMarkMap[contact.pub]);

    const profile = profiles.find(x => x.creator === contact.pub);
    const label = profile?.name || truncateMiddle(contact.npub, 28, ':');
    const isSelected = contact.pub === directMessage && location.pathname.startsWith('/dm/');

    const handleItemClick = () => {
        if (isDmRequest) {
            onAddUserClick(contact);
        } else {
            navigate(`/dm/${contact.npub}`);
        }
    };

    return (
        <div onClick={handleItemClick}>
            <ListItem 
                label={label} 
                href={isDmRequest ? '#' : `/dm/${contact.npub}`}
                selected={isSelected} 
                hasUnread={hasUnread}
            />
        </div>
    );
}


const DmList = () => {
    const theme = useTheme();
    const [showInviteePopup, setShowInviteePopup] = useState(false);
    const [t] = useTranslation();
    const directContacts = useLiveDirectContacts();
    const [, showModal] = useModal();
    const navigate = useNavigate();
    const [directMessages] = useAtom(directMessagesAtom);
    const [showRequests, setShowRequests] = useAtom(showRequestsAtom);
    const [showPopup, setShowPopup] = useState(false);
    const [selectedContact, setSelectedContact] = useState<DirectContact | null>(null);
    const [isSendingRequest, setIsSendingRequest] = useState(false);
    const [raven] = useAtom(ravenAtom);

    const switchShowRequests = () => {
        setShowRequests(!showRequests);
    }

    const search = () => {
        showModal({
            body: <StartDM onSuccess={(id) => {
                showModal(null);
                navigate(`/dm/${id}`).then();
            }} />
        })
    }

const handleAddUserClick = (contact: DirectContact, sendingRequest: boolean = false) => {
    console.log("Selected contact: ", contact); // Debug log
    setSelectedContact(contact);
    setIsSendingRequest(sendingRequest);
    setShowPopup(true);
};

    const handleConfirmDMRequest = () => {
    setShowPopup(false);
    // Logic to add the user and send the confirmation message
    if (selectedContact) {
        // Add the user to the contact list
        const newContact: DirectContact = {
            pub: selectedContact.pub,
            npub: selectedContact.npub,
        };
        const updatedDirectContacts = [...directContacts, newContact];
        const updatedRequests = requests.filter(r => r.pub !== selectedContact.pub);
        
        // Update the directContacts and requests state or perform any necessary state management
        // For example, if using a state management library like Redux:
        // dispatch(updateDirectContacts(updatedDirectContacts));
        // dispatch(updateRequests(updatedRequests));

        // Check if raven is defined before sending the confirmation message
        if (raven) {
            raven.sendDirectMessage(selectedContact.pub, "This DM has been accepted!");
            // Navigate to the DM page after sending the message
            navigate(`/dm/${selectedContact.npub}`);
        } else {
            // Show an error message to the user and prevent navigation
            alert("Unable to send confirmation message. Please try again later.");
            console.error("Raven is undefined, unable to send message.");
        }
    }
};

    const handleConfirm = () => {
        setShowPopup(false);
        search(); // Show the StartDM component after confirmation
    };

    const handleCancel = () => {
        setShowPopup(false);
        setSelectedContact(null);
    };

const combinedSearchAndAddUser = (contact: DirectContact) => {
    handleAddUserClick(contact, true); // For sending a request
};


    const handleInviteeConfirm = () => {
        setShowInviteePopup(false);
    };

    const handleInviteeCancel = () => {
        setShowInviteePopup(false);
    };

    const requests = useMemo(() => directContacts.filter(d => directMessages.find(m => m.peer === d.pub && m.creator !== d.pub) === undefined), [directContacts, directMessages]);
    const dmList = useMemo(() => directContacts.filter(d => requests.find(r => r.pub === d.pub) === undefined), [directContacts, requests]);

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
        zIndex: 2000, // Ensure this is higher than the "direct message" box
    };

    const popupContentStyles = {
        background: 'black',
        padding: '20px',
        borderRadius: '10px',
        textAlign: 'center' as 'center',
        maxWidth: '600px',
        width: '100%',
        zIndex: 2100, // Ensure this is higher than the "direct message" box
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

    return <>
        {showPopup && (  // Ensure the popup is rendered before the rest of the content
            <div style={popupStyles}>
                <div style={popupContentStyles}>
                    <h2>{t('Confirmation of Connection')}</h2>
                    <p>{t('Before proceeding with connecting to another user on this platform, please carefully read and acknowledge the following:')}</p>
                    <p><strong>{t('Important:')}</strong></p>
                    <ul>
                        <li>{t('By choosing to connect, you affirm that you have a personal acquaintance with the user you wish to connect with.')}</li>
                        <li>{t('You may be required to verify your acquaintance with the other user at any time. Failure to provide satisfactory identification when requested may lead to the assumption that you own or control the other user\'s account.')}</li>
                        <li>{t('You must confirm that you have not requested, offered, initiated, or accepted any form of payment in relation to establishing this connection.')}</li>
                    </ul>
                    <p>{t('Please indicate your confirmation that you personally know the user you wish to connect with and that no payment has been requested, offered, initiated, or accepted in association with this connection.')}</p>
                    <button 
    style={buttonStyles} 
    onMouseEnter={(e) => (e.currentTarget.style.backgroundColor = buttonHoverStyles.backgroundColor)} 
    onMouseLeave={(e) => (e.currentTarget.style.backgroundColor = buttonStyles.backgroundColor)} 
    onClick={isSendingRequest ? handleConfirm : handleConfirmDMRequest}>
    {t('I Confirm')}
</button>
<button 
    style={buttonStyles} 
    onMouseEnter={(e) => (e.currentTarget.style.backgroundColor = buttonHoverStyles.backgroundColor)} 
    onMouseLeave={(e) => (e.currentTarget.style.backgroundColor = buttonStyles.backgroundColor)} 
    onClick={handleCancel}>
    {t('Cancel')}
</button>
                </div>
            </div>
        )}

        <Box sx={{
            mt: '40px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between'
        }}>
            <Box sx={{
                fontFamily: 'Faktum, sans-serif',
                fontWeight: 'bold',
                color: theme.palette.primary.dark,
            }}>
                {showRequests ? t('DM Requests') : t('DM Contacts')}
            </Box>
<button onClick={() => combinedSearchAndAddUser(selectedContact!)} className='btn btn_success btn_sm'>
    <span>+</span>  Add User
</button>

        </Box>

        {!showRequests && requests.length > 0 && (
            <Box sx={{ m: '12px 0' }}>
                <Button size='small' onClick={switchShowRequests}>
                    {t(requests.length === 1 ? '{{n}} DM request' : '{{n}} DM requests', { n: requests.length })}
                </Button>
            </Box>
        )}

        {showRequests && (
            <Box sx={{ m: '12px 0' }}>
                <Button size='small' onClick={switchShowRequests}>
                    {t('< Back to DMs')}
                </Button>
            </Box>
        )}

        {(() => {
            const theList = showRequests ? requests : dmList;

            if (theList.length === 0) {
                return <Box component='span' sx={{
                    color: theme.palette.primary.dark,
                    fontSize: '85%',
                    opacity: '0.6',
                }}>{t('No direct message')}</Box>
            }

            return theList.map(p => (
                <div key={p.npub}>
                    <DmListItem contact={p} onAddUserClick={handleAddUserClick} isDmRequest={showRequests} />
                </div>
            ));
        })()}
    </>
}

export default DmList;
