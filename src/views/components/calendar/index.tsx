import React, { useState, useEffect, useCallback } from 'react';
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
  Typography,
  CircularProgress,
  Snackbar,
  Select,
  MenuItem,
  FormControl,
  InputLabel
} from '@mui/material';
import { ravenAtom, profilesAtom, channelAtom, activeProposalIdAtom, keysAtom, directMessagesAtom } from 'atoms';
import NewKinds from 'raven/raven';
import RavenEvents from 'raven/raven';
import ExtendedFilter from 'raven/raven';
import ExtendedKind from 'raven/raven';
import useTranslation from 'hooks/use-translation';
import { formatMessageDateTime } from 'helper';
import { RouteComponentProps } from '@reach/router';
import { nip19 } from 'nostr-tools';
import useLiveDirectContacts from 'hooks/use-live-direct-contacts';
import { Helmet } from 'react-helmet';
import AppWrapper from 'views/components/app-wrapper';
import AppMenu from 'views/components/app-menu';
import AppContent from 'views/components/app-content';

interface CalendarProps extends RouteComponentProps {}

export interface EventSuggestion {
  id: string;
  root: string;
  content: string;
  creator: string;
  created: number;
  mentions: string[];
  proposalID: string;
  finalDateTime?: string;
}

const Calendar: React.FC<CalendarProps> = (props) => {
  console.log("Starting Calendar component");

  const [t] = useTranslation();
  const [raven] = useAtom(ravenAtom);
  const [profiles] = useAtom(profilesAtom);
  const [channel] = useAtom(channelAtom);
  const [activeProposalId] = useAtom(activeProposalIdAtom);
  const [keys] = useAtom(keysAtom);

  const [timeRange, setTimeRange] = useState<[number, number]>([9, 17]);
  const [startDate, setStartDate] = useState<string>(new Date().toISOString().split('T')[0]);
  const [endDate, setEndDate] = useState<string>(new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString().split('T')[0]);
  const [eventSuggestions, setEventSuggestions] = useState<EventSuggestion[]>([]);
  const [showDialog, setShowDialog] = useState(false);
  const [selectedSuggestion, setSelectedSuggestion] = useState<EventSuggestion | null>(null);
  const [finalDateTime, setFinalDateTime] = useState<string>('');
  const [recipientPubKey, setRecipientPubKey] = useState<string>('');
  const [isLoading, setIsLoading] = useState(false);
  //const [isIntervalLoading, setIsIntervalLoading] = useState(false);
  const [snackbarMessage, setSnackbarMessage] = useState<string | null>(null);
  const [finalizedEvents, setFinalizedEvents] = useState<EventSuggestion[]>([]);
const [isCountering, setIsCountering] = useState(false);
const [counteredSuggestionId, setCounteredSuggestionId] = useState<string | null>(null);

  const [directMessages] = useAtom(directMessagesAtom);
  const directContacts = useLiveDirectContacts();

  // Replace recipientPubKey state with selectedContact
  const [selectedContact, setSelectedContact] = useState<string>('');

const fetchEventSuggestions = useCallback(async (isInitialLoad = false) => {
  if (!raven || !keys) {
    console.log('Raven or keys not available, skipping fetchEventSuggestions', { raven, keys });
    return;
  }
  if (isInitialLoad) {
    setIsLoading(true);
  }
  try {
    console.log('Fetching calendar suggestions...');
    const messages = await raven.fetchCalendarSuggestions();
    console.log('Fetched messages:', messages);
    
    const newSuggestions: EventSuggestion[] = [];
    const newFinalizedEvents: EventSuggestion[] = [];

    messages.forEach(msg => {
      const content = JSON.parse(msg.content);
      if (content.type === 'event_suggestion') {
        newSuggestions.push({
          id: msg.id,
          root: msg.tags.find(tag => tag[0] === 'e')?.[1] || '',
          content: msg.content,
          creator: msg.pubkey,
          created: msg.created_at,
          mentions: msg.tags.filter(tag => tag[0] === 'p').map(tag => tag[1]),
          proposalID: msg.tags.find(tag => tag[0] === 'e')?.[1] || '',
        });
      } else if (content.type === 'event_finalized') {
        newFinalizedEvents.push({
          id: msg.id,
          root: msg.tags.find(tag => tag[0] === 'e')?.[1] || '',
          content: msg.content,
          creator: msg.pubkey,
          created: msg.created_at,
          mentions: msg.tags.filter(tag => tag[0] === 'p').map(tag => tag[1]),
          proposalID: msg.tags.find(tag => tag[0] === 'e')?.[1] || '',
          finalDateTime: content.finalDateTime,
        });
      }
    });

    console.log('New suggestions:', newSuggestions);
    console.log('New finalized events:', newFinalizedEvents);

    setEventSuggestions(prevSuggestions => {
      const existingIds = new Set(prevSuggestions.map(s => s.id));
      const uniqueNewSuggestions = newSuggestions.filter(s => !existingIds.has(s.id));
      return [...prevSuggestions, ...uniqueNewSuggestions];
    });

    setFinalizedEvents(prevEvents => {
      const existingIds = new Set(prevEvents.map(e => e.id));
      const uniqueNewEvents = newFinalizedEvents.filter(e => !existingIds.has(e.id));
      return [...prevEvents, ...uniqueNewEvents];
    });

  } catch (error) {
    console.error('Error fetching event suggestions:', error);
    setSnackbarMessage(t('Failed to fetch event suggestions. Please try again.'));
  } finally {
    if (isInitialLoad) {
      setIsLoading(false);
    }
  }
}, [raven, keys, t]);

  useEffect(() => {
    if (raven && keys) {
      console.log("Raven and keys are available, starting to fetch event suggestions");
      fetchEventSuggestions(true);
      const interval = setInterval(() => fetchEventSuggestions(false), 30000);
      return () => clearInterval(interval);
    } else {
      console.log("Raven or keys not available", { raven, keys });
    }
  }, [raven, keys, fetchEventSuggestions]);

  useEffect(() => {
    if (raven) {
      const handleCalendarSuggestion = (suggestions: EventSuggestion[]) => {
        setEventSuggestions(prevSuggestions => {
          const newSuggestions = suggestions.filter(s => 
            !prevSuggestions.some(ps => ps.id === s.id)
          );
          return [...prevSuggestions, ...newSuggestions];
        });
      };

      raven.onCalendarSuggestion(handleCalendarSuggestion);

      return () => {
        raven.offCalendarSuggestion(handleCalendarSuggestion);
      };
    }
  }, [raven]);

  const handleSendSuggestion = async () => {
    if (!raven) {
      console.error('Raven is not initialized');
      setSnackbarMessage(t('Unable to send suggestion. Please try again later.'));
      return;
    }

    if (!selectedContact) {
      console.log('No contact selected');
      setSnackbarMessage(t('Please select a recipient'));
      return;
    }

    const suggestion = JSON.stringify({
      type: 'event_suggestion',
      dateRange: [
        new Date(startDate).toISOString(),
        new Date(endDate).toISOString()
      ],
      timeRange: timeRange,
      isCounterSuggestion: isCountering,
      originalSuggestionId: counteredSuggestionId
    });

    console.log('Sending suggestion:', suggestion);

    try {
      setIsLoading(true);
      const result = await raven.publishCalendarSuggestion(selectedContact, suggestion);
      console.log('Send result:', result);
      console.log('Message tags:', result.tags);
      setSnackbarMessage(t('Event suggestion sent successfully!'));
      setSelectedContact('');
      await fetchEventSuggestions(true);
    } catch (error) {
      console.error('Error sending event suggestion:', error);
      setSnackbarMessage(t('Failed to send event suggestion. Please try again.'));
    } finally {
      setIsLoading(false);
    }

    setIsCountering(false);
    setCounteredSuggestionId(null);
  };

const handleIgnore = (suggestion: EventSuggestion) => {
  setEventSuggestions(prevSuggestions => prevSuggestions.filter(s => s.id !== suggestion.id));
  setSnackbarMessage(t('Suggestion ignored and removed'));
};

  const handleRespondToSuggestion = async (suggestion: EventSuggestion, response: 'accept' | 'counter' | 'ignore') => {
    console.log("handleRespondToSuggestion called", { suggestion, response });

    if (!raven) {
      console.error('Raven is not initialized');
      return;
    }
    const content = JSON.parse(suggestion.content);
    console.log('Parsed suggestion content:', content);

    if (response === 'accept') {
      setSelectedSuggestion(suggestion);
      setShowDialog(true);
    } else if (response === 'counter') {
      setTimeRange(content.timeRange);
      setStartDate(content.dateRange[0]);
      setEndDate(content.dateRange[1]);
      setRecipientPubKey(suggestion.creator);
      console.log('Set up counter suggestion', { timeRange: content.timeRange, startDate: content.dateRange[0], endDate: content.dateRange[1], recipientPubKey: suggestion.creator });
    } else {
      const responseMessage = JSON.stringify({
        type: 'event_response',
        originalSuggestionId: suggestion.id,
        response: 'ignored',
      });
      console.log('Sending ignore response:', responseMessage);
      try {
        setIsLoading(true);
        const result = await raven.sendDirectMessage(suggestion.creator, responseMessage, [], suggestion.proposalID);
        console.log('Ignore response sent:', result);
        setEventSuggestions(prevSuggestions => prevSuggestions.filter(s => s.id !== suggestion.id));
      } catch (error) {
        console.error('Error sending ignore response:', error);
        setSnackbarMessage(t('Failed to send ignore response. Please try again.'));
      } finally {
        setIsLoading(false);
      }
    }
    await fetchEventSuggestions(true);
  };

const handleCounter = (suggestion: EventSuggestion) => {
  const content = JSON.parse(suggestion.content);
  setTimeRange(content.timeRange);
  setStartDate(new Date(content.dateRange[0]).toISOString().split('T')[0]);
  setEndDate(new Date(content.dateRange[1]).toISOString().split('T')[0]);
  setRecipientPubKey(suggestion.creator);
  setIsCountering(true);
  setCounteredSuggestionId(suggestion.id);
};

const handleAccept = async (suggestion: EventSuggestion) => {
  setSelectedSuggestion(suggestion);
  setShowDialog(true);
};

const handleFinalizeEvent = async () => {
  if (!raven || !selectedSuggestion || !finalDateTime) {
    console.error('Missing required data for finalizing event', { raven, selectedSuggestion, finalDateTime });
    return;
  }

  const finalizeMessage = JSON.stringify({
    type: 'event_finalized',
    originalSuggestionId: selectedSuggestion.id,
    finalDateTime: finalDateTime,
    suggestedBy: selectedSuggestion.creator,
    ...JSON.parse(selectedSuggestion.content)
  });

  try {
    setIsLoading(true);
    const result = await raven.publishCalendarSuggestion(selectedSuggestion.creator, finalizeMessage);
    console.log('Finalize message sent:', result);
    setShowDialog(false);
    setEventSuggestions(prevSuggestions => prevSuggestions.filter(s => s.id !== selectedSuggestion.id));
    setFinalizedEvents(prevEvents => [...prevEvents, {
      ...selectedSuggestion,
      finalDateTime: finalDateTime
    }]);
    setSnackbarMessage(t('Event finalized successfully!'));
  } catch (error) {
    console.error('Error sending finalize message:', error);
    setSnackbarMessage(t('Failed to finalize event. Please try again.'));
  } finally {
    setIsLoading(false);
  }
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
  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' });
  };
  return `${formatDate(start)} - ${formatDate(end)}`;
};

  return (
    <>
      <Helmet>
        <title>{t("NostrChat - Calendar")}</title>
      </Helmet>
      <AppWrapper>
        <AppMenu />
        <AppContent>
          <Box sx={{ width: '100%', maxWidth: 600, mx: 'auto', mt: 4 }}>
            <Typography variant="h4" sx={{ mb: 4 }}>
              {isCountering ? t('Counter Event Suggestion') : t('Event Suggestion')}
            </Typography>
      <Box sx={{ mb: 2 }}>
        <FormControl fullWidth>
          <InputLabel id="contact-select-label">{t("Select Recipient")}</InputLabel>
          <Select
            labelId="contact-select-label"
            value={selectedContact}
            onChange={(e) => setSelectedContact(e.target.value as string)}
            label={t("Select Recipient")}
          >
            {directContacts.map((contact) => (
              <MenuItem key={contact.pub} value={contact.pub}>
                {profiles.find(p => p.creator === contact.pub)?.name || contact.npub}
              </MenuItem>
            ))}
          </Select>
        </FormControl>
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
        disabled={!selectedContact}
      >
        {isCountering ? t('Send Counter Suggestion') : t('Send Event Suggestion')}
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
          console.log("Rendering suggestion with content:", content);
          return (
            <Box key={suggestion.id} sx={{ border: '1px solid #ccc', borderRadius: 2, p: 2, mb: 2 }}>
              <Box>{t('Suggested by')}: {profiles.find(p => p.creator === suggestion.creator)?.name || formatPublicKey(suggestion.creator)}</Box>
              <Box>{t('Suggested time range')}: {formatTimeRange(content.timeRange)}</Box>
<Box>
  {t('Suggested date range')}: {content.dateRange ? 
    formatDateRange(content.dateRange[0], content.dateRange[1]) 
    : 'Invalid date range'}
</Box>
<Box sx={{ mt: 1 }}>
  <Button onClick={() => handleAccept(suggestion)}>{t('Accept')}</Button>
  <Button onClick={() => handleCounter(suggestion)}>{t('Counter')}</Button>
  <Button onClick={() => handleIgnore(suggestion)}>{t('Ignore')}</Button>
</Box>
            </Box>
          );
        })}
      </Box>

<Typography variant="h5" sx={{ mt: 4, mb: 2 }}>{t('Finalized Events')}</Typography>
<Box sx={{ mt: 2 }}>
  {finalizedEvents.map(event => {
    let content;
    try {
      content = JSON.parse(event.content);
    } catch (e) {
      console.error('Error parsing event content:', e);
      content = {};
    }
    return (
      <Box key={event.id} sx={{ border: '1px solid #ccc', borderRadius: 2, p: 2, mb: 2 }}>
        <Box>{t('Suggested by')}: {profiles.find(p => p.creator === event.creator)?.name || formatPublicKey(event.creator)}</Box>
        <Box>{t('Suggested time range')}: {formatTimeRange(content.timeRange)}</Box>
        <Box>{t('Suggested date range')}: {content.dateRange ? 
          formatDateRange(content.dateRange[0], content.dateRange[1]) 
          : 'Invalid date range'}
        </Box>
        <Box>{t('Finalized date and time')}: {event.finalDateTime ? formatMessageDateTime(new Date(event.finalDateTime).getTime()) : 'Not set'}</Box>
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
      
            <Snackbar
              open={!!snackbarMessage}
              autoHideDuration={6000}
              onClose={() => setSnackbarMessage(null)}
              message={snackbarMessage}
            />
          </Box>
        </AppContent>
      </AppWrapper>
    </>
  );
};

export default Calendar;
