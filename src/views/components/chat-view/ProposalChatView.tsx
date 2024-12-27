// @ts-nocheck

import React, { useEffect, useMemo, useRef, useState } from 'react';
import { toast } from 'react-toastify';
import { useAtom } from 'jotai';
import uniq from 'lodash.uniq';
import { darken } from '@mui/material';
import Box from '@mui/material/Box';
import Button from '@mui/material/Button';
import { useTheme } from '@mui/material/styles';
import Typography from '@mui/material/Typography';
import Tooltip from '@mui/material/Tooltip';
import { grey } from '@mui/material/colors';
import Divider from '@mui/material/Divider';
import useTranslation from 'hooks/use-translation';
import useStyles from 'hooks/use-styles';
import MessageView from 'views/components/message-view';
import {
  FormControl,
  Select,
  MenuItem,
  InputLabel
} from '@mui/material';
import {
  ravenAtom,
  activeProposalIdAtom,
  readMarkMapAtom,
  tempPrivAtom,
  keysAtom,
  channelAtom,
  proposalCommitteesAtom,
  channelsAtom,
  directContactsAtom
} from 'atoms';
import { Message, Committee, Channel, Proposal } from 'types';
import {
  formatMessageTime,
  formatMessageDate,
} from 'helper';
import { SCROLL_DETECT_THRESHOLD, PLATFORM } from 'const';
import { separateByAgreement } from 'util/function';

const ProposalChatView = (props: { messages: Message[], separator: string, loading?: boolean, isDM?: boolean, isPermanentProposal?: boolean }) => {
  const { separator, messages, loading, isDM, isPermanentProposal } = props;
  const theme = useTheme();
  const styles = useStyles();
  const [t] = useTranslation();
  const ref = useRef<HTMLDivElement | null>(null);
  const [isAtBottom, setIsAtBottom] = useState(true);
  const [firstMessageEl, setFirstMessageEl] = useState<HTMLDivElement | null>(null);
  const [scrollTop, setScrollTop] = useState<number>(0);
  const [raven] = useAtom(ravenAtom);
  const [keys] = useAtom(keysAtom);
  const [tempPriv] = useAtom(tempPrivAtom);
  const [readMarkMap] = useAtom(readMarkMapAtom);
  const [proposalCommittees, setProposalCommittees] = useAtom(proposalCommitteesAtom);

  const [activeProposalId] = useAtom(activeProposalIdAtom);
  const [channel] = useAtom(channelAtom);
  const [channels] = useAtom(channelsAtom);

const [directContacts] = useAtom(directContactsAtom);
const [selectedContact, setSelectedContact] = useState<string | null>(null);

  const scrollToBottom = () => {
    ref.current!.scroll({ top: ref.current!.scrollHeight, behavior: 'auto' });
  }

  useEffect(() => {
    if (ref.current && isAtBottom) {
      scrollToBottom();
    }
  }, [messages]);

  useEffect(() => {
    scrollToBottom();
  }, [separator]);

  useEffect(() => {
    if (isAtBottom && keys?.priv !== 'none') {
      if (messages.length === 0) return;

      if (isPermanentProposal) {
        const permanentProposalReadMarkKey = `permanent_proposal_${separator}`;
        if (readMarkMap[permanentProposalReadMarkKey] === undefined) {
          raven?.updateReadMarkMap({ ...readMarkMap, ...{ [permanentProposalReadMarkKey]: Math.floor(Date.now() / 1000) } });
          return;
        }

        const lMessage = messages[messages.length - 1];
        if (lMessage.created > readMarkMap[permanentProposalReadMarkKey]) {
          raven?.updateReadMarkMap({ ...readMarkMap, ...{ [permanentProposalReadMarkKey]: Math.floor(Date.now() / 1000) } });
        }
      } else {
        if (readMarkMap[separator] === undefined) {
          raven?.updateReadMarkMap({ ...readMarkMap, ...{ [separator]: Math.floor(Date.now() / 1000) } });
          return;
        }

        const lMessage = messages[messages.length - 1];
        if (lMessage.created > readMarkMap[separator]) {
          raven?.updateReadMarkMap({ ...readMarkMap, ...{ [separator]: Math.floor(Date.now() / 1000) } });
        }
      }
    }
  }, [separator, isAtBottom, messages, readMarkMap, keys, isPermanentProposal]);

  useEffect(() => {
    let scrollTimer: any;
    const div = ref.current;

    const handleScroll = () => {
      clearTimeout(scrollTimer);
      scrollTimer = setTimeout(() => {
        setScrollTop(div!.scrollTop);
        const isAtBottom = Math.abs((div!.scrollHeight - div!.scrollTop) - div!.clientHeight) <= SCROLL_DETECT_THRESHOLD
        setIsAtBottom(isAtBottom);
        const isAtTop = (div!.scrollHeight > div!.clientHeight) && div!.scrollTop < SCROLL_DETECT_THRESHOLD;
        if (isAtTop) {
          window.dispatchEvent(new Event('chat-view-top', { bubbles: true }))
        }
      }, 50);
    }

    div?.addEventListener('scroll', handleScroll);
    return () => {
      div?.removeEventListener('scroll', handleScroll);
    }
  }, []);

  useEffect(() => {
    const imageLoaded = () => {
      if (ref.current && isAtBottom) {
        scrollToBottom();
      }
    }

    window.addEventListener('chat-media-loaded', imageLoaded);
    return () => {
      window.removeEventListener('chat-media-loaded', imageLoaded)
    }
  }, [isAtBottom]);

  useEffect(() => {
    if (loading) {
      setFirstMessageEl(ref.current!.querySelector('.message') as HTMLDivElement);
    } else {
      if (firstMessageEl) {
        if (firstMessageEl.previousSibling) {
          (firstMessageEl.previousSibling as HTMLDivElement).scrollIntoView(true);
        }
        setFirstMessageEl(null);
      }
    }
  }, [loading]);

  useEffect(() => {
    const messageIds = Array.from(document.querySelectorAll('.message[data-visible=true]'))
      .map(el => el.getAttribute('data-id'))
      .filter(id => id !== null) as string[];
    if (messageIds.length === 0) return;

    const now = Math.floor(Date.now() / 1000)
    const relIds = messageIds.map(m => messages.find(x => x.id === m)?.reactions?.filter(x => x.creator !== keys?.pub).filter(l => now - l.created <= 600).map(l => l.id) || []).flat();

    let interval: any;
    const timer = setTimeout(() => {
      raven?.listenMessages(
        messageIds.filter(id => id !== null) as string[],
        relIds.filter(id => id !== null) as string[]
      );
    }, 500);

    return () => {
      clearTimeout(timer);
      clearInterval(interval);
    }
  }, [raven, messages, scrollTop]);

  useEffect(() => {
    if (!ref.current) return;

    const observer = new ResizeObserver(() => {
      if (ref.current && isAtBottom) {
        scrollToBottom();
      }
    });

    observer.observe(ref.current);

    return () => {
      observer.disconnect();
    }
  }, [isAtBottom]);

  const filteredMessages = useMemo(() => {
    return messages.filter(message => message.proposalID === activeProposalId);
  }, [messages, activeProposalId]);
  // <p>{channel.description}</p>

const isUserInCommittee = useMemo(() => {
  return proposalCommittees.some(committee => 
    committee.members.includes(keys?.pub || '')
  );
}, [proposalCommittees, keys]);

const addMember = async () => {
  if (!selectedContact || !isUserInCommittee || !channel || !keys) return;

  // Check if the proposal has failed
  const hasProposalFailed = ermHasProposalFailed;
  if (hasProposalFailed) {
    toast.error("Cannot add members to failed proposals");
    return;
  }

  setProposalCommittees((prevCommittees: Committee[]) => {
    return prevCommittees.map((committee, index) => {
      if (index === 1) { // Always add to the second committee
        return {
          ...committee,
          members: [...committee.members, selectedContact]
        };
      }
      return committee;
    });
  });

  // Send DM to the added member
  try {
    const message = `You have been added to a proposal committee. Proposal ID: ${channel.id}, Added by: ${keys.pub}`;
    await raven?.sendDirectMessage(selectedContact, message);
    toast.success("Member added and notified");
  } catch (error) {
    console.error("Failed to send DM", error);
    toast.error("Member added but notification failed");
  }

  setSelectedContact(null); // Reset selection after adding
};

const ermHasProposalFailed = useMemo(() => {
  if (!channel || !(channel as Proposal).about) return false;

  const about = JSON.parse((channel as Proposal).about);
  const { agreed, nonAgreed } = separateByAgreement(about.voting);
  return nonAgreed.length >= agreed.length;
}, [channel]);

  const removeMember = (committeeId: string) => {
    setProposalCommittees((prevCommittees: Committee[]) => {
      return prevCommittees.map(committee => {
        if (committee.id === committeeId) {
          const updatedMembers = [...committee.members];
          updatedMembers.pop();
          return {
            ...committee,
            members: updatedMembers,
          };
        }
        return committee;
      });
    });
  };

useEffect(() => {
  if (channel?.id && channel.creator) {
    setProposalCommittees((prevCommittees: Committee[]) => {
      return prevCommittees.map((committee, index) => {
        if (index === 0 && !committee.members.includes(channel.creator)) {
          return {
            ...committee,
            members: [...committee.members, channel.creator],
          };
        }
        return committee;
      });
    });
  }
}, [channel]);

console.log("Proposal Committees: ", proposalCommittees);
  console.log("Channel: ", channel);
  console.log("Channels: ", channels);


/*
      <div className="committees">
{proposalCommittees.map((committee, index) => (
  <div key={committee.id} className="committee">
    <div className="committee-header">{committee.name}</div>
    <div className="committee-members">
      <p>Members: {committee.members.join(', ')}</p>
      <div className="add-remove-buttons">
        {channel?.id && <button onClick={() => addMember(channel.id)}>Add Member</button>}
        <button onClick={() => removeMember(committee.id)}>Remove Member</button>
      </div>
    </div>
  </div>
))}
      </div>
*/

const ContactDropdown = () => (
  <FormControl fullWidth>
    <InputLabel>Select Contact</InputLabel>
    <Select
      value={selectedContact || ''}
      onChange={(e) => setSelectedContact(e.target.value as string)}
      disabled={!isUserInCommittee}
    >
      {directContacts.map((contact) => (
        <MenuItem key={contact.pub} value={contact.pub}>
          {contact.npub}
        </MenuItem>
      ))}
    </Select>
  </FormControl>
);

  return (
    <Box sx={{ display: 'flex', height: 'calc(100vh - 64px)' }}>
      {/* Chat Section */}
<Box 
  ref={ref} 
  sx={{ 
    flex: 2, 
    mt: 'auto', 
    overflowY: 'auto', // Add this line
    maxHeight: 'calc(100vh - 64px)', // Add this line
    ...styles.scrollY, 
    borderRight: `1px solid ${theme.palette.divider}` 
  }}
>
        <div className="proposal-info">
          <h3>{channel?.name}</h3>
        </div>
        {filteredMessages.map(message => (
          <MessageView 
            key={message.id} 
            message={message} 
            compactView={false} 
            dateFormat="time"
          />
        ))}
        {messages.map((msg, i) => {
          const prevMsg = messages[i - 1];
          const msgDate = formatMessageDate(msg.created);
          const prevMsgDate = prevMsg ? formatMessageDate(prevMsg.created) : null;
          const isCompact = prevMsg ? msg.creator === prevMsg?.creator && formatMessageTime(msg.created) === formatMessageTime(prevMsg.created) : false;

          if (msgDate !== prevMsgDate) {
            return (
              <React.Fragment key={msg.id}>
                <Divider
                  sx={{
                    m: '0 24px',
                    fontSize: '0.7em',
                    color: darken(theme.palette.text.secondary, 0.4),
                    mt: i === 0 ? '100px' : null,
                  }}
                >
                  {msgDate}
                </Divider>
                <MessageView message={msg} dateFormat="time" compactView={isCompact} />
              </React.Fragment>
            );
          }

          return <MessageView key={msg.id} message={msg} dateFormat="time" compactView={isCompact} />;
        })}

        {(channel as Proposal)?.readyForMarket && (channel as Proposal).productDetails && (
          <Box>
            <Typography variant="h6">Marketplace Product Details</Typography>
            <Typography>
              Price: {(channel as Proposal).productDetails?.price ?? 'N/A'}
            </Typography>
            <Typography>
              Quantity: {(channel as Proposal).productDetails?.quantity ?? 'N/A'}
            </Typography>
          </Box>
        )}

        {isDM && keys?.priv === 'none' && !tempPriv && (
          <Box sx={{ textAlign: 'center', m: '20px 0' }}>
            <Button
              variant="contained"
              onClick={() => {
                window.requestPrivateKey().then();
              }}
            >
              {t('Decrypt chat')}
            </Button>
          </Box>
        )}
      </Box>

      {/* Dashboard Section */}
      <Box sx={{ flex: 1, overflow: 'auto', p: 2, backgroundColor: theme.palette.background.default }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Dashboard
        </Typography>

<Box sx={{ mb: 4 }}>
  <Typography variant="h5" component="h2" gutterBottom>
    Committees
  </Typography>
  {proposalCommittees.map((committee, index) => (
    <Box key={committee.id} sx={{ mb: 2, p: 2, backgroundColor: theme.palette.background.paper, borderRadius: 1 }}>
      <Typography variant="h6">{committee.name}</Typography>
      <Typography>Members: {committee.members.join(', ')}</Typography>
      {index === 1 && isUserInCommittee && !ermHasProposalFailed && (
        <Box sx={{ mt: 1 }}>
          <ContactDropdown />
          <Button 
            variant="contained" 
            size="small" 
            sx={{ mt: 1 }} 
            onClick={addMember}
            disabled={!selectedContact || ermHasProposalFailed}
          >
            Add Member
          </Button>
        </Box>
      )}
    </Box>
  ))}
</Box>

        <Box sx={{ mb: 4 }}>
          <Typography variant="h5" component="h2" gutterBottom>
            Proposal Details
          </Typography>
          <Box sx={{ p: 2, backgroundColor: theme.palette.background.paper, borderRadius: 1 }}>
            <Typography><strong>Name:</strong> {channel?.name}</Typography>
            <Typography><strong>Creator:</strong> {channel?.creator}</Typography>
            <Typography><strong>Status:</strong> {(channel as Proposal)?.readyForMarket ? 'Ready for Market' : 'In Progress'}</Typography>
          </Box>
        </Box>

        <Box sx={{ mb: 4 }}>
          <Typography variant="h5" component="h2" gutterBottom>
            Activities
          </Typography>
          {filteredMessages.slice(0, 5).map((message) => (
            <Box key={message.id} sx={{ mb: 2, p: 2, backgroundColor: theme.palette.background.paper, borderRadius: 1 }}>
              <Typography><strong>Contributor:</strong> {message.creator}</Typography>
              <Typography><strong>Message:</strong> {message.content}</Typography>
            </Box>
          ))}
        </Box>

        <Box>
          <Typography variant="h5" component="h2" gutterBottom>
            Rewards
          </Typography>
          <Box sx={{ p: 2, backgroundColor: theme.palette.background.paper, borderRadius: 1 }}>
            <Typography>Reward distribution to be implemented</Typography>
          </Box>
        </Box>
      </Box>
    </Box>
  );
};

export default ProposalChatView;