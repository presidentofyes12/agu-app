// Calendar.tsx

import React, { useState, useEffect } from 'react';
import { useAtom } from 'jotai';
import { 
  Box, 
  Slider, 
  Button, 
  Dialog, 
  DialogTitle, 
  DialogContent, 
  DialogActions,
  TextField,
  Typography
} from '@mui/material';
import { ravenAtom, profilesAtom, channelAtom, activeProposalIdAtom, keysAtom } from 'atoms';
import { PublicMessage } from 'types';
import useTranslation from 'hooks/use-translation';
import { formatMessageDateTime } from 'helper';
import { RouteComponentProps } from '@reach/router';
import { nip19 } from 'nostr-tools';

interface CalendarProps extends RouteComponentProps {}

// Define a new type that matches our event suggestion structure
interface EventSuggestion {
  id: string;
  root: string;
  content: string;
  creator: string;
  created: number;
  mentions: string[];
  proposalID: string;
}

const Calendar: React.FC<CalendarProps> = (props) => {
  console.log("Starting Calendar");
  const [t] = useTranslation();
  const [raven] = useAtom(ravenAtom);
  const [profiles] = useAtom(profilesAtom);
  const [channel] = useAtom(channelAtom);
  const [activeProposalId] = useAtom(activeProposalIdAtom);
  const [keys] = useAtom(keysAtom);
  
  const [timeRange, setTimeRange] = useState<[number, number]>([9, 17]); // 9 AM to 5 PM
  const [startDate, setStartDate] = useState<string>(new Date().toISOString().split('T')[0]);
  const [endDate, setEndDate] = useState<string>(new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString().split('T')[0]);
  const [eventSuggestions, setEventSuggestions] = useState<EventSuggestion[]>([]);
  const [showDialog, setShowDialog] = useState(false);
  const [selectedSuggestion, setSelectedSuggestion] = useState<EventSuggestion | null>(null);
  const [finalDateTime, setFinalDateTime] = useState<string>('');
  const [recipientPubKey, setRecipientPubKey] = useState<string>('');

  useEffect(() => {
    if (raven && keys) {
      fetchEventSuggestions();
      const interval = setInterval(fetchEventSuggestions, 30000); // Check for new messages every 30 seconds
      return () => clearInterval(interval);
    }
  }, [raven, keys]);

useEffect(() => {
  console.log('Current eventSuggestions:', eventSuggestions);
}, [eventSuggestions]);

const fetchEventSuggestions = async () => {
  if (!raven || !keys) {
    console.log('Raven or keys not available');
    return;
  }
  try {
    console.log('Fetching proposals...');
    const messages = await raven.fetchAllProposal();
    console.log('Fetched messages:', messages);
    
const newSuggestions = messages
  .filter(msg => {
    try {
      const content = JSON.parse(msg.content);
      return content.type === 'event_suggestion' && content.timeRange && content.dateRange;
    } catch (e) {
      console.log(`Error parsing message ${msg.id}:`, e);
      return false;
    }
  })
  .map(msg => ({
    id: msg.id,
    root: msg.tags.find(tag => tag[0] === 'e')?.[1] || '',
    content: msg.content, // Store as string
    creator: msg.pubkey,
    created: msg.created_at,
    mentions: msg.tags.filter(tag => tag[0] === 'p').map(tag => tag[1]),
    proposalID: msg.tags.find(tag => tag[0] === 'e')?.[1] || '',
  }));

    console.log('New suggestions:', newSuggestions);

  setEventSuggestions(prevSuggestions => {
    const existingIds = new Set(prevSuggestions.map(s => s.id));
    const uniqueNewSuggestions = newSuggestions.filter(s => !existingIds.has(s.id));
    console.log('Unique new suggestions:', uniqueNewSuggestions);
    const updatedSuggestions = [...prevSuggestions, ...uniqueNewSuggestions];
    console.log('Updated event suggestions:', updatedSuggestions);
    return updatedSuggestions;
  });

    // console.log('Updated event suggestions:', eventSuggestions);
  } catch (error) {
    console.error('Error fetching event suggestions:', error);
  }
};

const handleSendSuggestion = async () => {
  if (!raven) {
    console.error('Raven is not initialized');
    alert(t('Unable to send suggestion. Please try again later.'));
    return;
  }

  if (!recipientPubKey.trim()) {
    alert(t('Please enter a recipient public key'));
    return;
  }

  let pubkey = recipientPubKey;

  if (recipientPubKey.startsWith('npub1')) {
    try {
      const { type, data } = nip19.decode(recipientPubKey);
      if (type !== 'npub') {
        throw new Error('Not an npub key');
      }
      pubkey = data as string;
    } catch (e) {
      console.error('Error decoding npub:', e);
      alert(t('Invalid npub format'));
      return;
    }
  } else if (!/^[0-9a-fA-F]{64}$/.test(recipientPubKey)) {
    alert(t('Invalid public key format'));
    return;
  }

  console.log('Sending to pubkey:', pubkey);

const suggestion = JSON.stringify({
  type: 'event_suggestion',
  dateRange: [startDate, endDate],
  timeRange: timeRange,
});

  console.log('Sending suggestion:', suggestion);

  try {
    const result = await raven.sendDirectMessage(
      pubkey,
      suggestion,
      [], // No mentions for direct messages
      activeProposalId || undefined
    );
    console.log('Send result:', result);
    console.log('Message tags:', result.tags);
    alert(t('Event suggestion sent successfully!'));
    setRecipientPubKey('');
    fetchEventSuggestions(); // Fetch updated suggestions
  } catch (error) {
    console.error('Error sending event suggestion:', error);
    alert(t('Failed to send event suggestion. Please check the recipient public key and try again.'));
  }
};

const handleRespondToSuggestion = async (suggestion: EventSuggestion, response: 'accept' | 'counter' | 'ignore') => {
  if (!raven) return;
  const content = JSON.parse(suggestion.content);
  if (response === 'accept') {
    setSelectedSuggestion(suggestion);
    setShowDialog(true);
  } else if (response === 'counter') {
    setTimeRange(content.timeRange);
    setStartDate(content.dateRange[0]);
    setEndDate(content.dateRange[1]);
    setRecipientPubKey(suggestion.creator);
  } else {
    const responseMessage = JSON.stringify({
      type: 'event_response',
      originalSuggestionId: suggestion.id,
      response: 'ignored',
    });
    await raven.sendDirectMessage(suggestion.creator, responseMessage, [], suggestion.proposalID);
    setEventSuggestions(prevSuggestions => prevSuggestions.filter(s => s.id !== suggestion.id));
  }
  fetchEventSuggestions(); // Fetch updated suggestions
};

  const handleFinalizeEvent = async () => {
    if (!raven || !selectedSuggestion || !finalDateTime || !channel) return;
    const finalizeMessage = JSON.stringify({
      type: 'event_finalized',
      originalSuggestionId: selectedSuggestion.id,
      finalDateTime: finalDateTime,
    });
    await raven.sendPublicMessage(channel, finalizeMessage, [selectedSuggestion.creator], selectedSuggestion.proposalID);
    setShowDialog(false);
    setEventSuggestions(prevSuggestions => prevSuggestions.filter(s => s.id !== selectedSuggestion.id));
    fetchEventSuggestions(); // Fetch updated suggestions
  };

const formatPublicKey = (pubkey: string) => {
  return pubkey.slice(0, 8) + '...'; // or use nip19.npubEncode(pubkey) if available
};

const formatTimeRange = (range: [number, number] | undefined): string => {
  if (!range || !Array.isArray(range) || range.length < 2) {
    console.error('Invalid time range:', range);
    return 'Invalid time range';
  }
  return `${range[0]}:00 - ${range[1]}:00`;
};

  const formatDateRange = (start: string, end: string): string => {
    return `${formatMessageDateTime(new Date(start).getTime())} - ${formatMessageDateTime(new Date(end).getTime())}`;
  };

  console.log("Event suggestions: ", eventSuggestions);

  return (
    <Box sx={{ width: '100%', padding: 2 }}>
      <Typography variant="h4" gutterBottom>{t('Event Scheduler')}</Typography>
      
      <Box sx={{ mb: 2 }}>
        <TextField
          label={t('Recipient Public Key')}
          value={recipientPubKey}
          onChange={(e) => setRecipientPubKey(e.target.value)}
          fullWidth
          placeholder={t('Enter recipient\'s public key')}
        />
      </Box>
      <Box sx={{ mb: 2 }}>
        <TextField
          label={t('Start Date')}
          type="date"
          value={startDate}
          onChange={(e) => setStartDate(e.target.value)}
          fullWidth
          InputLabelProps={{
            shrink: true,
          }}
        />
      </Box>
      <Box sx={{ mb: 2 }}>
        <TextField
          label={t('End Date')}
          type="date"
          value={endDate}
          onChange={(e) => setEndDate(e.target.value)}
          fullWidth
          InputLabelProps={{
            shrink: true,
          }}
        />
      </Box>
      <Box sx={{ mb: 2 }}>
        <Slider
          value={timeRange}
          onChange={(_, newValue) => setTimeRange(newValue as [number, number])}
          valueLabelDisplay="auto"
          min={0}
          max={24}
          step={1}
          marks
          valueLabelFormat={(value) => `${value}:00`}
        />
        <Box sx={{ mt: 1 }}>{t('Time Range')}: {formatTimeRange(timeRange)}</Box>
      </Box>
<Button 
  variant="contained" 
  onClick={handleSendSuggestion}
  disabled={!recipientPubKey.trim()}
>
  {t('Send Event Suggestion')}
</Button>

      <Typography variant="h5" sx={{ mt: 4, mb: 2 }}>{t('Received Event Suggestions')}</Typography>
      <Box sx={{ mt: 2 }}>
{eventSuggestions.map(suggestion => {
  let content;
  try {
    content = JSON.parse(suggestion.content);
  } catch (e) {
    console.error('Error parsing suggestion content:', e);
    content = {};
  }
  console.log("Suggestion content:", content);
  console.log("Suggestion creator:", suggestion.creator);
  return (
    <Box key={suggestion.id} sx={{ border: '1px solid #ccc', borderRadius: 2, p: 2, mb: 2 }}>
      <Box>{t('Suggested by')}: {profiles.find(p => p.creator === suggestion.creator)?.name || formatPublicKey(suggestion.creator)}</Box>
      <Box>{t('Suggested time range')}: {formatTimeRange(content.timeRange)}</Box>
      <Box>{t('Suggested date range')}: {content.dateRange ? formatDateRange(content.dateRange[0], content.dateRange[1]) : 'Invalid date range'}</Box>
      <Box sx={{ mt: 1 }}>
        <Button onClick={() => handleRespondToSuggestion(suggestion, 'accept')}>{t('Accept')}</Button>
        <Button onClick={() => handleRespondToSuggestion(suggestion, 'counter')}>{t('Counter')}</Button>
        <Button onClick={() => handleRespondToSuggestion(suggestion, 'ignore')}>{t('Ignore')}</Button>
      </Box>
    </Box>
  );
})}
      </Box>

      <Dialog open={showDialog} onClose={() => setShowDialog(false)}>
        <DialogTitle>{t('Finalize Event')}</DialogTitle>
        <DialogContent>
          <TextField
            label={t('Final Date and Time')}
            type="datetime-local"
            value={finalDateTime}
            onChange={(e) => setFinalDateTime(e.target.value)}
            fullWidth
            InputLabelProps={{
              shrink: true,
            }}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowDialog(false)}>{t('Cancel')}</Button>
          <Button onClick={handleFinalizeEvent} disabled={!finalDateTime}>{t('Finalize')}</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default Calendar;