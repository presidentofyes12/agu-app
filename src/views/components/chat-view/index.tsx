import React, { useEffect, useRef, useState } from 'react';
import { Box, darken } from '@mui/material';
import Divider from '@mui/material/Divider';
import { useTheme } from '@mui/material/styles';
import Button from '@mui/material/Button';
import { useAtom } from 'jotai';
import { activeProposalIdAtom, channelAtom, proposalCommitteesAtom } from 'atoms';

import MessageView from 'views/components/message-view';
import useStyles from 'hooks/use-styles';
import useTranslation from 'hooks/use-translation';
import { formatMessageDate, formatMessageTime } from 'helper';
import { Message, Committee, Channel } from 'types';
import { SCROLL_DETECT_THRESHOLD } from 'const';
import { keysAtom, ravenAtom, readMarkMapAtom, tempPrivAtom, channelsAtom } from 'atoms';
import { notEmpty } from 'util/misc';

const ChatView = (props: { messages: Message[], separator: string, loading?: boolean, isDM?: boolean }) => {
  const { separator, messages, loading, isDM } = props;
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
  const [activeProposalId] = useAtom(activeProposalIdAtom);
  const [channel] = useAtom(channelAtom);
  const [channels] = useAtom(channelsAtom);
  const [proposalCommittees, setProposalCommittees] = useAtom(proposalCommitteesAtom);

  const filteredMessages = messages.filter(message => message.proposalID === activeProposalId);

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

      if (readMarkMap[separator] === undefined) {
        raven?.updateReadMarkMap({ ...readMarkMap, ...{ [separator]: Math.floor(Date.now() / 1000) } });
        return;
      }

      const lMessage = messages[messages.length - 1];
      if (lMessage.created > readMarkMap[separator]) {
        raven?.updateReadMarkMap({ ...readMarkMap, ...{ [separator]: Math.floor(Date.now() / 1000) } });
      }
    }
  }, [separator, isAtBottom, messages, readMarkMap, keys]);

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
    const messageIds = Array.from(document.querySelectorAll('.message[data-visible=true]')).map(el => el.getAttribute('data-id')).filter(notEmpty);
    if (messageIds.length === 0) return;

    const now = Math.floor(Date.now() / 1000)
    const relIds = messageIds.map(m => messages.find(x => x.id === m)?.reactions?.filter(x => x.creator !== keys?.pub).filter(l => now - l.created <= 600).map(l => l.id) || []).flat();

    let interval: any;
    const timer = setTimeout(() => {
      raven?.listenMessages(messageIds, relIds);
      interval = setInterval(() => {
        raven?.listenMessages(messageIds, relIds);
      }, 10000);
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
  // <p>{channel.description}</p>

  const addMember = (proposalId: string) => {
    if (!channels) {
      console.error('Channels not found');
      return;
    }

    const channel = channels.find((ch: Channel) => ch.id === proposalId);

    if (!channel) {
      console.error('Channel not found');
      return;
    }

    const creator = channel.creator;
    const voters = JSON.parse(channel.about).voting.map((vote: { voter: string }) => vote.voter);

    setProposalCommittees((prevCommittees: Committee[]) => {
      return prevCommittees.map((committee, index) => {
        if (index === 0 && !committee.members.includes(creator)) {
          return {
            ...committee,
            members: [...committee.members, creator],
          };
        } else if (index === 1) {
          const newMembers = voters.filter((voter: string) => !committee.members.includes(voter));
          return {
            ...committee,
            members: [...committee.members, ...newMembers],
          };
        }
        return committee;
      });
    });
  };

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

  return (
    <Box ref={ref} sx={{ mt: 'auto', ...styles.scrollY }}>
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
              <Divider sx={{ m: '0 24px', fontSize: '0.7em', color: darken(theme.palette.text.secondary, 0.4), mt: i === 0 ? '100px' : null }}>
                {msgDate}
              </Divider>
              <MessageView message={msg} dateFormat='time' compactView={isCompact} />
            </React.Fragment>
          )
        }

        return <MessageView key={msg.id} message={msg} dateFormat='time' compactView={isCompact} />;
      })}
      {(isDM && keys?.priv === 'none' && !tempPriv) && (
        <Box sx={{ textAlign: 'center', m: '20px 0' }}>
          <Button variant="contained" onClick={() => { window.requestPrivateKey().then(); }}>{t('Decrypt chat')}</Button>
        </Box>
      )}
    </Box>
  );
}

export default ChatView;
