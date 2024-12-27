import { useEffect, useMemo, useState } from 'react';
import { useAtom } from 'jotai';
import { RouteComponentProps, useLocation, useNavigate } from '@reach/router';
import { Helmet } from 'react-helmet';
import isEqual from 'lodash.isequal';
import Box from '@mui/material/Box';
import CircularProgress from '@mui/material/CircularProgress';
import AppWrapper from 'views/components/app-wrapper';
import AppContent from 'views/components/app-content';
import AppMenu from 'views/components/app-menu';
import ChannelHeader from 'views/channel/components/channel-header';
import ProposalChatInput from 'views/components/chat-input/ProposalIndex';
import ProposalChatView from 'views/components/chat-view/ProposalChatView';
import ThreadChatView from 'views/components/thread-chat-view';
import ChannelCard from 'views/components/channel-card';
import useTranslation from 'hooks/use-translation';
import useLiveChannels from 'hooks/use-live-channels';
import useLiveChannel from 'hooks/use-live-channel';
import useLivePublicMessages from 'hooks/use-live-public-messages';
import useToast from 'hooks/use-toast';
import {
  channelAtom,
  keysAtom,
  ravenAtom,
  ravenStatusAtom,
  threadRootAtom,
  channelToJoinAtom,
  leftChannelListAtom,
} from 'atoms';
import {
  ACCEPTABLE_LESS_PAGE_MESSAGES,
  GLOBAL_CHAT,
  MESSAGE_PER_PAGE,
} from 'const';
import ProposalIndexExpired from 'views/components/chat-input/ProposalIndexExpired';
import { resultBool, returnAgreed } from 'views/channel/components/channel-header';
import { isTimeRemaining } from 'util/function';
import { isSha256 } from 'util/crypto';
import { permVotingPeriod, votingPeriod } from 'util/constant';

const isPermanentProposal = (proposalName: string) => {
  return permanentProposalsArray.some((proposal) => proposal.name === proposalName);
};

const votedAgree = (userPubKey: any, channel: any) => {
  return returnAgreed(channel).some((vote: { voter: string }) => vote.voter === userPubKey);
}

const permanentProposalsArray = [
  {
    name: 'Mostr',
    about: '{"problem":"Lack of connection between Fediverse and Nostr","solution":"","targetAudience":"","qualifications":"","purpose":"A platform feature enabling dynamic and flexible presentation of content.","approach":"A platform feature enabling dynamic and flexible presentation of content.","outcome":"A platform feature enabling dynamic and flexible presentation of content.","timeline":"","budget":"","callToAction":"","voting":[],"proposalID":""}',
    picture: '',
  },
  {
    name: 'Ephemeral Relays',
    about: '{"problem":"Need for temporary communication channels","solution":"","targetAudience":"","qualifications":"","purpose":"Temporary communication channels that expire after a set duration.","approach":"Temporary communication channels that expire after a set duration.","outcome":"Temporary communication channels that expire after a set duration.","timeline":"","budget":"","callToAction":"","voting":[],"proposalID":""}',
    picture: '',
  },
  {
    name: 'Public and private AI profiles for version control',
    about: '{"problem":"Lack of version control for AI profiles","solution":"","targetAudience":"","qualifications":"","purpose":"Profiles that manage and track changes in AI models and datasets.","approach":"Profiles that manage and track changes in AI models and datasets.","outcome":"Profiles that manage and track changes in AI models and datasets.","timeline":"","budget":"","callToAction":"","voting":[],"proposalID":""}',
    picture: '',
  },
  {
    name: 'Marketplace',
    about: '{"problem":"Need for a decentralized marketplace","solution":"","targetAudience":"","qualifications":"","purpose":"A decentralized marketplace for trading goods and services.","approach":"A decentralized marketplace for trading goods and services.","outcome":"A decentralized marketplace for trading goods and services.","timeline":"","budget":"","callToAction":"","voting":[],"proposalID":""}',
    picture: '',
  },
  {
    name: 'Smart contract',
    about: '{"problem":"Need for automated and self-executing contracts","solution":"","targetAudience":"","qualifications":"","purpose":"Automated and self-executing contracts with predefined rules.","approach":"Automated and self-executing contracts with predefined rules.","outcome":"Automated and self-executing contracts with predefined rules.","timeline":"","budget":"","callToAction":"","voting":[],"proposalID":""}',
    picture: '',
  },
  {
    name: 'NewLaw/Everyone is right/Force for peace',
    about: '{"problem":"Need for a fair governance system","solution":"","targetAudience":"","qualifications":"","purpose":"A governance system promoting universal fairness and conflict resolution.","approach":"A governance system promoting universal fairness and conflict resolution.","outcome":"A governance system promoting universal fairness and conflict resolution.","timeline":"","budget":"","callToAction":"","voting":[],"proposalID":""}',
    picture: '',
  },
  {
    name: 'Withdrawal Rights/Disclaimer/ Privacy standards',
    about: '{"problem":"Need for user rights and privacy policies","solution":"","targetAudience":"","qualifications":"","purpose":"User rights and privacy policies ensuring data protection and transparency.","approach":"User rights and privacy policies ensuring data protection and transparency.","outcome":"User rights and privacy policies ensuring data protection and transparency.","timeline":"","budget":"","callToAction":"","voting":[],"proposalID":""}',
    picture: '',
  },
  {
    name: 'Embedded application',
    about: '{"problem":"Need for seamless application integration","solution":"","targetAudience":"","qualifications":"","purpose":"Integration of applications directly within the platform for seamless user experience.","approach":"Integration of applications directly within the platform for seamless user experience.","outcome":"Integration of applications directly within the platform for seamless user experience.","timeline":"","budget":"","callToAction":"","voting":[],"proposalID":""}',
    picture: '',
  },
  {
    name: 'Multi ID system',
    about: '{"problem":"Need for secure management of multiple identities","solution":"","targetAudience":"","qualifications":"","purpose":"A system allowing users to manage multiple identities securely.","approach":"A system allowing users to manage multiple identities securely.","outcome":"A system allowing users to manage multiple identities securely.","timeline":"","budget":"","callToAction":"","voting":[],"proposalID":""}',
    picture: '',
  },
  {
    name: "If you don't rate, you can't be rated.",
    about: '{"problem":"Lack of user participation in ratings","solution":"","targetAudience":"","qualifications":"","purpose":"A feedback system encouraging user participation in ratings.","approach":"A feedback system encouraging user participation in ratings.","outcome":"A feedback system encouraging user participation in ratings.","timeline":"","budget":"","callToAction":"","voting":[],"proposalID":""}',
    picture: '',
  },
  {
    name: 'Privacy, scalability, security, transparency, decentralization, and identification.',
    about: '{"problem":"Need for core platform principles","solution":"","targetAudience":"","qualifications":"","purpose":"Core principles guiding platform development and operations.","approach":"Core principles guiding platform development and operations.","outcome":"Core principles guiding platform development and operations.","timeline":"","budget":"","callToAction":"","voting":[],"proposalID":""}',
    picture: '',
  },
  {
    name: 'Autotranslate',
    about: '{"problem":"Need for multilingual support","solution":"","targetAudience":"","qualifications":"","purpose":"Automatic translation feature for multilingual support.","approach":"Automatic translation feature for multilingual support.","outcome":"Automatic translation feature for multilingual support.","timeline":"","budget":"","callToAction":"","voting":[],"proposalID":""}',
    picture: '',
  },
];

const ChannelPage = (props: RouteComponentProps) => {
  const [keys] = useAtom(keysAtom);
  const navigate = useNavigate();
  const location = useLocation();
  const [t] = useTranslation();
  const [, showMessage] = useToast();
  const channels = useLiveChannels();
  const channel = useLiveChannel();
  const messages = useLivePublicMessages(channel?.id);
  const [, setChannel] = useAtom(channelAtom);
  const [threadRoot, setThreadRoot] = useAtom(threadRootAtom);
  const [ravenStatus] = useAtom(ravenStatusAtom);
  const [raven] = useAtom(ravenAtom);
  const [channelToJoin, setChannelToJoin] = useAtom(channelToJoinAtom);
  const [leftChannelList] = useAtom(leftChannelListAtom);
  const [loading, setLoading] = useState(false);
  const [hasMore, setHasMore] = useState(true);
  const [notFound, setNotFound] = useState(false);

  const cid = useMemo(
    () =>
      'channel' in props && isSha256(props.channel as string)
        ? (props.channel as string)
        : null,
    [props]
  );

  useEffect(() => {
    // If the user didn't leave global chat for empty channel id
    if (ravenStatus.ready && !cid && !leftChannelList.includes(GLOBAL_CHAT.id))
      navigate(`/channel/${GLOBAL_CHAT.id}`).then();
  }, [cid, ravenStatus.ready]);

  useEffect(() => {
    if (!keys) navigate('/login').then();
  }, [keys]);

  useEffect(() => {
    return () => {
      setChannelToJoin(null);
      setChannel(null);
      setLoading(false);
      setHasMore(true);
      setNotFound(false);
    };
  }, [location.pathname]);

  useEffect(() => {
    if (!cid) return;
    setChannel(channels.find(x => x.id === cid) || null);
  }, [cid, channels]);

  useEffect(() => {
    const fetchPrev = () => {
      if (!hasMore || loading) return;
      setLoading(true);
      raven
        ?.fetchPrevMessages(channel!.id, messages[0].created)
        .then(num => {
          if (num < MESSAGE_PER_PAGE - ACCEPTABLE_LESS_PAGE_MESSAGES) {
            setHasMore(false);
          }
        })
        .finally(() => setLoading(false));
    };
    window.addEventListener('chat-view-top', fetchPrev);

    return () => {
      window.removeEventListener('chat-view-top', fetchPrev);
    };
  }, [messages, channel, hasMore, loading]);

  useEffect(() => {
    const msg = messages.find(x => x.id === threadRoot?.id);
    if (threadRoot && msg && !isEqual(msg, threadRoot)) {
      setThreadRoot(msg);
    }
  }, [messages, threadRoot]);

  useEffect(() => {
    if (ravenStatus.ready && !channel && cid && !channelToJoin) {
      const timer = setTimeout(() => setNotFound(true), 5000);

      raven?.fetchChannel(cid).then(channel => {
        if (channel) {
          setChannelToJoin(channel);
          clearTimeout(timer);
        }
      });

      return () => clearTimeout(timer);
    }
  }, [ravenStatus.ready, channel, cid, channelToJoin]);

  if (!keys) return null;

  if (!ravenStatus.ready) {
    return (
      <Box sx={{ display: 'flex', alignItems: 'center' }}>
        <CircularProgress size={20} sx={{ mr: '8px' }} /> {t('Loading...')}
      </Box>
    );
  }

  if (!cid) {
    return (
      <>
        <Helmet>
          <title>{t('Proposal Details')}</title>
        </Helmet>
        <AppWrapper>
          <AppMenu />
          <AppContent>
            <Box
              sx={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                flexGrow: 1,
                color: 'text.secondary',
                fontSize: '0.8em',
              }}
            >
              {t('Select a Proposal from the menu')}
            </Box>
          </AppContent>
        </AppWrapper>
      </>
    );
  }

  if (!channel) {
    return (
      <>
        <Helmet>
          <title>{t('NostrPulschain')}</title>
        </Helmet>
        <AppWrapper>
          <AppMenu />
          <AppContent>
            <Box
              sx={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                width: '100%',
                height: '100%',
              }}
            >
              {(() => {
                if (channelToJoin) {
                  return (
                    <Box sx={{ maxWidth: '500px', ml: '10px', mr: '10px' }}>
                      <ChannelCard
                        channel={channelToJoin}
                        onJoin={() => {
                          const load = () => {
                            raven?.loadChannel(channelToJoin.id);
                            setChannelToJoin(null);
                          };

                          if (leftChannelList.includes(channelToJoin.id)) {
                            raven
                              ?.updateLeftChannelList(
                                leftChannelList.filter(
                                  x => x !== channelToJoin.id
                                )
                              )
                              .then(load);
                          } else {
                            load();
                          }
                        }}
                      />
                    </Box>
                  );
                }

                if (notFound) return t('Proposal not found');

                return (
                  <>
                    <CircularProgress size={20} sx={{ mr: '8px' }} />{' '}
                    {t('Looking for the Proposal...')}
                  </>
                );
              })()}
            </Box>
          </AppContent>
        </AppWrapper>
      </>
    );
  }

  if (!ravenStatus.syncDone) {
    return (
      <>
        <Helmet>
          <title>{t(`NostrChat - ${channel.name}`)}</title>
        </Helmet>
        <AppWrapper>
          <AppMenu />
          <AppContent>
            <ChannelHeader />
            <Box
              sx={{
                flexGrow: 1,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
              }}
            >
              <CircularProgress size={20} sx={{ mr: '8px' }} />{' '}
              {t('Fetching Proposal Details...')}
            </Box>
            <ProposalChatInput
              separator={channel.id}
              senderFn={() => {
                return new Promise(() => {}).then();
              }}
            />
          </AppContent>
        </AppWrapper>
      </>
    );
  }
  console.log("channel", channel);
  console.log("Agreed members: ", returnAgreed(channel));

  console.log("User pubkey: ", raven?.getPub);

  console.log("True or false: ", votedAgree(raven?.getPub, channel));

  return (
    <>
      <Helmet>
        <title>{t(`NostrChat - ${channel.name}`)}</title>
      </Helmet>
      <AppWrapper>
        <AppMenu />
        <AppContent divide={!!threadRoot}>
          <ChannelHeader />
          <ProposalChatView
            separator={channel.id}
            messages={messages}
            loading={loading}
          />
          {
          (!isTimeRemaining(channel.created, isPermanentProposal(channel.name) ? permVotingPeriod : votingPeriod) || 
          (isTimeRemaining(channel.created, isPermanentProposal(channel.name) ? permVotingPeriod : votingPeriod) && resultBool(channel) && votedAgree(raven?.getPub, channel))) ? (
          <ProposalChatInput
            separator={channel.id}
            senderFn={(message: string, mentions: string[]) => {
              return raven!
                .sendPublicMessage(channel, message, mentions)
                .catch(e => {
                  showMessage(e.toString(), 'error');
                });
            }}
          />
        ) : (
          <ProposalIndexExpired
            separator={channel.id}
            senderFn={(message: string, mentions: string[]) => {
              return raven!
                .sendPublicMessage(channel, message, mentions)
                .catch(e => {
                  showMessage(e.toString(), 'error');
                });
            }}
          />
        )}


        </AppContent>
        {threadRoot && (
          <ThreadChatView
            senderFn={(message: string, mentions: string[]) => {
              return raven!
                .sendPublicMessage(
                  channel,
                  message,
                  [threadRoot.creator, ...mentions],
                  threadRoot.id
                )
                .catch(e => {
                  showMessage(e.toString(), 'error');
                });
            }}
          />
        )}
      </AppWrapper>
    </>
  );
};

export default ChannelPage;