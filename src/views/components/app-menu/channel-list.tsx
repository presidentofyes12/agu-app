import React, { useEffect, useState } from 'react';
import { useLocation } from '@reach/router';
import { useAtom } from 'jotai';
import { Box, CircularProgress } from '@mui/material';
import { useTheme } from '@mui/material/styles';

import useTranslation from 'hooks/use-translation';
import useLiveChannels from 'hooks/use-live-channels';
import useLivePublicMessages from 'hooks/use-live-public-messages';
import ChannelAddMenu from 'views/components/app-menu/channel-add-menu';
import ListItem from 'views/components/app-menu/list-item';
import { channelAtom, keysAtom, ravenAtom, readMarkMapAtom } from 'atoms';
import { CiFileOff } from 'react-icons/ci';
import { Channel } from 'types';
import useToast from 'hooks/use-toast';
import { PROPOSAL_TYPES, permVotingPeriod, votingPeriod } from 'util/constant';
import { isTimeRemaining } from 'util/function';

import FilterProposalDropdown from './FilterProposalDropdown';

const isPermanentProposal = (proposalName: string) => {
  return permanentProposalsList.some((proposal) => proposal.name === proposalName);
};

const permanentProposalsList = [
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

const ChannelListItem = (props: { c: Channel }) => {
  const { c } = props;

  const location = useLocation();
  const messages = useLivePublicMessages(c.id);
  const [readMarkMap] = useAtom(readMarkMapAtom);
  const [channel] = useAtom(channelAtom);
  const [keys] = useAtom(keysAtom);

  const lMessage = messages[messages.length - 1];
  const hasUnread =
    keys?.priv !== 'none' &&
    !!(readMarkMap[c.id] && lMessage && lMessage.created > readMarkMap[c.id]);

  const isSelected =
    c.id === channel?.id && location.pathname.startsWith('/channel/');

  return (
    <>
      {c.id === 'f412192fdc846952c75058e911d37a7392aa7fd2e727330f4344badc92fb8a22' ? (
        ''
      ) : (
        <ListItem
          key={c.id}
          label={c.name}
          href={`/channel/${c.id}`}
          selected={isSelected}
          hasUnread={hasUnread}
        />
      )}
    </>
  );
};

const permanentProposals = [
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

const AllProposalChannelListItem = (props: { c: any }) => {
  const { c } = props;

  const location = useLocation();
  const messages = useLivePublicMessages(c.id);
  const [readMarkMap] = useAtom(readMarkMapAtom);
  const [channel] = useAtom(channelAtom);
  const [keys] = useAtom(keysAtom);

  const lMessage = messages[messages.length - 1];
  const hasUnread =
    keys?.priv !== 'none' &&
    !!(readMarkMap[c.id] && lMessage && lMessage.created > readMarkMap[c.id]);

  const isSelected =
    c.id === channel?.id && location.pathname.startsWith('/channel/');

  let label, href;
  if (typeof c === 'object' && c.id && c.name) {
    label = c.name;
    href = `/channel/${encodeURIComponent(JSON.stringify({ name: c.name, id: c.id }))}`;
  } else {
    try {
      const parsedContent = JSON.parse(c.content);
      label = parsedContent.name;
      href = `/channel/${JSON.parse(parsedContent.about).proposalID}`;
    } catch (e) {
      console.error('Failed to parse proposal content:', e);
      return null;
    }
  }

  return (
    <div>
      <ListItem
        key={c.id}
        label={label}
        href={href}
        selected={isSelected}
        hasUnread={hasUnread}
      />
    </div>
  );
};

const proposalExists = (proposals: any[] | undefined, name: string) => {
  return proposals?.some((proposal) => {
    try {
      return JSON.parse(proposal.content).name === name;
    } catch (e) {
      console.error('Failed to parse proposal content:', e);
      return false;
    }
  }) || false;
};

const ChannelList = () => {
  const theme = useTheme();
  const [t] = useTranslation();
  const channels = useLiveChannels();
  const [raven] = useAtom(ravenAtom);
  const [allProposal, setAllProposal] = useState<any[]>([]);
  const [fetchedAllProposal, setFetchedAllProposal] = useState<any[]>([]);
  const [permanentProposalList, setPermanentProposalList] = useState<any[]>([]);
  const [filterType, setfilterType] = useState(PROPOSAL_TYPES.all);
  const [, showMessage] = useToast();
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    const init = async () => {
      try {
        setIsLoading(true);
        const allProposal = await raven?.fetchAllProposal();
        console.log('allprops', allProposal);
        setFetchedAllProposal(allProposal || []);
        if (filterType === PROPOSAL_TYPES.all) {
          setAllProposal(allProposal || []);
        } else {
          filterProposalsByTime();
        }

        const permanentProposalsArray = [];

        for (const proposal of permanentProposals) {
          if (!proposalExists(allProposal, proposal.name)) {
            const newProposal = await raven?.createChannel(proposal);
            if (newProposal) permanentProposalsArray.push(newProposal);
          } else {
            const existingProposal = allProposal?.find((p) => {
              try {
                return JSON.parse(p.content).name === proposal.name;
              } catch (e) {
                console.error('Failed to parse proposal content:', e);
                return false;
              }
            });
            if (existingProposal) {
              permanentProposalsArray.push(existingProposal);
            }
          }
        }

        setPermanentProposalList(permanentProposalsArray);

        console.log('All proposals:', allProposal);
        console.log('All fetched proposals:', fetchedAllProposal);
        console.log('Permanent proposals:', permanentProposalsArray);
      } catch (err) {
        console.error('Error initializing proposals:', err);
        setError(err instanceof Error ? err : new Error('An unknown error occurred'));
      } finally {
        setIsLoading(false);
      }
    };
    init();
  }, [filterType, raven]);

  useEffect(() => {
    console.log(filterType);
    filterProposalsByTime();
  }, [filterType, fetchedAllProposal]);

  function filterProposalsByTime() {
    let filteredProposals = [];
    if (filterType === PROPOSAL_TYPES.active) {
      filteredProposals = fetchedAllProposal.filter((proposal: any) => {
        console.log(proposal.created_at, isPermanentProposal(proposal.name) ? permVotingPeriod : votingPeriod);
        return !isTimeRemaining(proposal.created_at, isPermanentProposal(proposal.name) ? permVotingPeriod : votingPeriod);
      });
    } else if (filterType === PROPOSAL_TYPES.expired) {
      filteredProposals = fetchedAllProposal.filter((proposal: any) => {
        return isTimeRemaining(proposal.created_at, isPermanentProposal(proposal.name) ? permVotingPeriod : votingPeriod);
      });
    } else if (filterType === PROPOSAL_TYPES.all) {
      filteredProposals = fetchedAllProposal;
    }

    setAllProposal(filteredProposals);
  }

  if (isLoading) return <CircularProgress />;
  if (error) return <div>Error: {error.message}</div>;

  return (
    <>
      {/* Proposal History section */}
      <div>
        <Box sx={{ mt: '10px', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <Box sx={{ fontFamily: 'Faktum, sans-serif', fontWeight: 'bold', color: theme.palette.primary.dark }}>
            <h3 onClick={() => console.log('p...', channels)}>{t('Proposal History')}</h3>
          </Box>
          <ChannelAddMenu />
        </Box>
        <hr />
        {channels.length <= 1 ? (
          <Box component="span" sx={{ color: theme.palette.primary.dark, fontSize: '85%', opacity: '0.6' }}>
            <h4 className="text-center">{t('No Proposal Found')} <CiFileOff /></h4>
          </Box>
        ) : (
          channels.map((c) => <ChannelListItem key={c.id} c={c} />)
        )}
      </div>

      {/* All Proposals section */}
      <div>
        <Box sx={{ mt: '50px', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <Box sx={{ fontFamily: 'Faktum, sans-serif', fontWeight: 'bold', color: theme.palette.primary.dark }}>
            <h3 onClick={() => console.log(allProposal)}>{t(`${filterType} Proposal `)}</h3>
          </Box>
          <FilterProposalDropdown proposalTypeSetter={setfilterType} />
        </Box>

        {!allProposal || allProposal.length === 0 ? (
          <Box component="span" sx={{ color: theme.palette.primary.dark, fontSize: '85%', opacity: '0.6' }}>
            <h4 className="text-center">{t('No Proposal Found')} <CiFileOff /></h4>
          </Box>
        ) : (
          allProposal.map((c: any, index: number) => (
            <AllProposalChannelListItem key={c?.id ?? index} c={c} />
          ))
        )}
      </div>

      {/* Permanent Proposals section */}
      <div>
        <Box sx={{ mt: '50px', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <Box sx={{ fontFamily: 'Faktum, sans-serif', fontWeight: 'bold', color: theme.palette.primary.dark }}>
            <h3 onClick={() => console.log(permanentProposalList)}>{t('Permanent Proposals')}</h3>
          </Box>
        </Box>

        {!permanentProposalList || permanentProposalList.length === 0 ? (
          <Box component="span" sx={{ color: theme.palette.primary.dark, fontSize: '85%', opacity: '0.6' }}>
            <h4 className="text-center">{t('No Permanent Proposal Found')} <CiFileOff /></h4>
          </Box>
        ) : (
          permanentProposalList.map((c: any, index: number) => (
            <AllProposalChannelListItem key={c?.id ?? index} c={c} />
          ))
        )}
      </div>
    </>
  );
};

export default ChannelList;