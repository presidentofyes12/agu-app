import React, { useEffect, useState } from 'react';
import { useLocation } from '@reach/router';
import { useAtom } from 'jotai';
import { Box } from '@mui/material';
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
import { PROPOSAL_TYPES, proposalTypes, votingPeriod } from 'util/constant';
import { isTimeRemaining } from 'util/function';

import FilterProposalDropdown from './FilterProposalDropdown';

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
      {c.id ==
      'f412192fdc846952c75058e911d37a7392aa7fd2e727330f4344badc92fb8a22' ? (
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

/*
Mostr
Ephemeral Relays
Public and private AI profiles for version control
Marketplace
Smart contract
NewLaw/Everyone is right/Force for peace
Withdrawal Rights/Disclaimer/ Privacy standards 
Embedded application 
Multi ID system 
If you don't rate, you can't be rated.
Privacy, scalability,  security,  transparency,  decentralization,  and identification.
Autotranslate
*/

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


  return (
    <>
      {typeof c === 'object' && c.id && c.name ? (
        <div>
          <ListItem
            key={c.id}
            label={c.name}
            href={`/channel/${encodeURIComponent(JSON.stringify({ name: c.name, id: c.id }))}`}
            selected={isSelected}
            hasUnread={hasUnread}
          />
        </div>
      ) : (
        <div>
          <ListItem
            key={c.id}
            label={JSON.parse(c.content).name}
            href={`/channel/${JSON.parse(JSON.parse(c.content).about).proposalID}`}
            selected={isSelected}
            hasUnread={hasUnread}
          />
        </div>
      )}
    </>
  );
};

const proposalExists = (proposals: any[] | undefined, name: string) => {
  return proposals?.some((proposal) => JSON.parse(proposal.content).name === name) || false;
};

const ChannelList = () => {
  const theme = useTheme();
  const [t] = useTranslation();
  const channels = useLiveChannels();
  const [raven] = useAtom(ravenAtom);
  const [allProposal, setAllProposal] = useState<any>([]);
  const [fetchedAllProposal, setFetchedAllProposal] = useState<any>([]);
  const [filterType, setfilterType] = useState(PROPOSAL_TYPES.all);
  const [, showMessage] = useToast();

  useEffect(() => {
  const init = async () => {
    const allProposal = await raven?.fetchAllProposal();
    console.log("allprops", allProposal);
    setFetchedAllProposal(allProposal);
    if (filterType === PROPOSAL_TYPES.all) {
      setAllProposal(allProposal);
    } else {
      filterProposalsByTime();
    }

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

      for (const proposal of permanentProposals) {
      if (!proposalExists(allProposal, proposal.name)) {
        console.log("All Proposals:");
        console.log(allProposal);
        raven?.createChannel(proposal).then((ev) => {
          console.log(ev.id);
          setFetchedAllProposal((prevProposals: any[]) => [...prevProposals, ev]);
        }).catch((e) => {
          showMessage(e.toString(), 'error');
        });
      } else {
        console.log("Already exists!");
      }
    }
  };
  init();
}, []);

  useEffect(() => {
    console.log(filterType);
    const init = async () => {
      filterProposalsByTime();
    };
    init();
  }, [filterType]);

  function filterProposalsByTime(  ) {
    let filteredProposals = [];
    if (filterType === PROPOSAL_TYPES.active) {
      filteredProposals = fetchedAllProposal.filter((proposal: any) => {
        console.log(proposal.created_at, votingPeriod)
        return !isTimeRemaining(proposal.created_at , votingPeriod);
      });
    } else if (filterType === PROPOSAL_TYPES.expired) {
      filteredProposals = fetchedAllProposal.filter((proposal: any) => {
        return isTimeRemaining(proposal.created_at, votingPeriod);
      });
    } else if (filterType === PROPOSAL_TYPES.all) {
      filteredProposals = fetchedAllProposal;
    }

    setAllProposal(filteredProposals);
  }
  return (
    <>
      <div>
        <Box
          sx={{
            mt: '10px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
          }}
        >
          <Box
            sx={{
              fontFamily: 'Faktum, sans-serif',
              fontWeight: 'bold',
              color: theme.palette.primary.dark,
            }}
          >
            <h3 onClick={async e => console.log('p...', channels)}>
              {t('Proposal History')}
            </h3>
          </Box>
          <ChannelAddMenu />
        </Box>
        <hr />
        {(() => {
          if (channels.length === 1) {
            return (
              <Box
                component="span"
                sx={{
                  color: theme.palette.primary.dark,
                  fontSize: '85%',
                  opacity: '0.6',
                }}
              >
                <h4 className="text-center">
                  {t('No Proposal Finded')} <CiFileOff />
                </h4>
              </Box>
            );
          } else {
            return channels.map(c => <ChannelListItem key={c.id} c={c} />);
          }
        })()}
      </div>

      <div>
        <Box
          sx={{
            mt: '50px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
          }}
        >
          <Box
            sx={{
              fontFamily: 'Faktum, sans-serif',
              fontWeight: 'bold',
              color: theme.palette.primary.dark,
            }}
          >
            <h3 onClick={e => console.log(allProposal)}>
              {t(`${filterType} Proposal `)}
            </h3>
          </Box>
          <FilterProposalDropdown proposalTypeSetter={setfilterType} />
        </Box>

        {(() => {
  if (!allProposal || allProposal.length === 0) {
    return (
      <Box
        component="span"
        sx={{
          color: theme.palette.primary.dark,
          fontSize: '85%',
          opacity: '0.6',
        }}
      >
        <h4 className="text-center">
          {t('No Proposal Found')} <CiFileOff />
        </h4>
      </Box>
    );
  } else {
    return allProposal.map((c: any) => (
      <>
        <AllProposalChannelListItem key={c.id} c={c} />
      </>
    ));
  }
})()}
      </div>
    </>
  );
};

export default ChannelList;