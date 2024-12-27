// @ts-nocheck

import React, { useState, useEffect } from 'react';
import { useAtom } from 'jotai';
import Box from '@mui/material/Box';
import Button from '@mui/material/Button';
import { useTheme } from '@mui/material/styles';
import ChannelMenu from 'views/channel/components/channel-header/channel-menu';
import { FaHeart, FaHeartBroken } from 'react-icons/fa';
import { toast } from 'react-toastify';
import AppContentHeaderBase from 'views/components/app-content-header-base';
import useStyle from 'hooks/use-styles';
import { channelAtom, keysAtom, ravenAtom } from 'atoms';
import { Product, Proposal } from 'types';
import { permVotingPeriod, votingPeriod } from 'util/constant';
import {
  isTimeRemaining,
  registerDataOnChain,
  separateByAgreement,
} from 'util/function';

import ProductDetailsDialog from './ProductDetailsDialog';
import CountdownButton from './CountDownButton';

const isPermanentProposal = (proposalName: string) => {
  return permanentProposalsArray.some((proposal) => proposal.name === proposalName);
};

export const resultBool = (channel: any) => {
  const parsedAbout = JSON.parse(channel.about);
  const { agreed, nonAgreed } = separateByAgreement(parsedAbout.voting);
  return agreed.length > nonAgreed.length;
};

export const returnAgreed = (channel: any) => {
  const parsedAbout = JSON.parse(channel.about);
  const { agreed, nonAgreed } = separateByAgreement(parsedAbout.voting);
  return agreed;
};

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

const ChannelHeader = () => {
  const [keys] = useAtom(keysAtom);
  const [channel] = useAtom(channelAtom);
  const [raven] = useAtom(ravenAtom);
  const theme = useTheme();
  const styles = useStyle();
  const [productDialogOpen, setProductDialogOpen] = useState(false);

  if (!channel || !keys) {
    return null;
  }

  const isCreator = channel.creator === keys.pub;
  const parsedAbout = JSON.parse(channel.about);
  const { agreed, nonAgreed } = separateByAgreement(parsedAbout.voting);
  const proposalSucceeded = agreed.length > nonAgreed.length;
  const votingEnded = !isTimeRemaining(channel.created, isPermanentProposal(channel.name) ? permVotingPeriod : votingPeriod);

  const hasPicture = channel.picture.startsWith('https://');

  const doVote = (agree: any) => {
    try {
      // Parse the channel's about information
      console.log(channel.about);
      const about = JSON.parse(channel.about);

      // Find the existing vote entry for the current user (keys.pub)
      const existingVoteIndex = about.voting.findIndex(
        (vote: { voter: string }) => vote.voter === keys.pub
      );

      if (existingVoteIndex !== -1) {
        // User has already voted, so replace the existing entry
        about.voting[existingVoteIndex] = { voter: keys.pub, agree };
      } else {
        // User has not voted yet, so push a new entry
        about.voting.push({ voter: keys.pub, agree });
      }

      var metadata = {
        name: channel.name,
        about: JSON.stringify(about),
        picture: channel.picture,
      };

      raven?.voteOnProposal(channel, metadata);
      toast.success('Your vote has been submitted for this Proposal');
    } catch (error) {
      console.error('Error parsing channel about information:', error);
      toast.error('Failed to submit your vote. Please try again.');
    }
  };

  const uploadOnchain = async () => {
    toast.info('Proposal Data syncing with OnChain');
    await registerDataOnChain(keys.priv, JSON.stringify({...channel, about:''}), '');
  };

  const renderChannelAbout = (about: string) => {
    try {
      const parsedAbout = JSON.parse(about);
      return (
        <>
          <p style={{ margin: '0', wordWrap: 'break-word', overflowWrap: 'break-word', whiteSpace: 'normal' }}>
            <span> Purpose: </span>{' '}
            {parsedAbout.purpose || 'N/A'}
          </p>
          <p style={{ margin: '0', wordWrap: 'break-word', overflowWrap: 'break-word', whiteSpace: 'normal' }}>
            <span> Approach: </span>{' '}
            {parsedAbout.approach || 'N/A'}
          </p>
          <p style={{ margin: '0', wordWrap: 'break-word', overflowWrap: 'break-word', whiteSpace: 'normal' }}>
            <span> Outcome: </span>{' '}
            {parsedAbout.outcome || 'N/A'}
          </p>
          <p style={{ margin: '0', wordWrap: 'break-word', overflowWrap: 'break-word', whiteSpace: 'normal' }}>
            <span> Need: </span>{' '}
            {parsedAbout.problem || 'N/A'}
          </p>
        </>
      );
    } catch (error) {
      console.error('Error parsing channel about information:', error);
      return (
        <p style={{ margin: '0', color: 'red' }}>
          Invalid channel about information.
        </p>
      );
    }
  };

  const renderVoteResult = () => {
    try {
      const parsedAbout = JSON.parse(channel.about);
      const { agreed, nonAgreed } = separateByAgreement(parsedAbout.voting);
      return agreed.length > nonAgreed.length ? (
        <button className="btn btn_success">
          Success
          <span className="ml-2">
            <FaHeart />
          </span>
        </button>
      ) : (
        <button className="btn btn_success">
          Proposal Failed
          <span className="ml-2">
            <FaHeartBroken />
          </span>
        </button>
      );
    } catch (error) {
      console.error('Error parsing channel about information:', error);
      return null;
    }
  };

  const renderVoteButtons = () => {
    try {
      const parsedAbout = JSON.parse(channel.about);
      const { agreed, nonAgreed } = separateByAgreement(parsedAbout.voting);
      return (
        <>
          <button
            className="btn btn_success"
            onClick={e => doVote(true)}
          >
            {agreed.length}
            <span className="ml-2">
              <FaHeart />
            </span>
          </button>
          <button
            className="btn btn_primary"
            onClick={e => doVote(false)}
          >
            {nonAgreed.length}
            <span className="ml-2">
              <FaHeartBroken />
            </span>
          </button>
        </>
      );
    } catch (error) {
      console.error('Error parsing channel about information:', error);
      return null;
    }
  };

const submitToMarketplace = async () => {
  if (resultBool(channel)) {
    const productDetails: Product = {
      id: channel.id,
      stall_id: '', // You need to decide how to handle this
      name: channel.name,
      description: JSON.parse(channel.about).problem,
      images: [channel.picture],
      currency: 'USD', // You may want to add this to the proposal form
      price: (channel as Proposal).productDetails?.price || 0,
      quantity: (channel as Proposal).productDetails?.quantity || 0,
      specs: [],
      shipping: [],
      proposalId: channel.id,
    };
    await raven?.createProduct(productDetails);
    // Update the channel to mark it as ready for market
    await raven?.updateProposal({ ...channel, readyForMarket: true } as Proposal);
    toast.success('Proposal submitted to marketplace');
  } else {
    toast.error('Proposal must be approved before submitting to marketplace');
  }
};

  const openProductDetailsDialog = () => {
    setProductDialogOpen(true);
  };

  const handleProductSubmit = async (productDetails) => {
    const product: Product = {
      id: channel.id,
      stall_id: '', // You may need to create a stall for proposals or use a default one
      name: channel.name,
      description: `Purpose: ${parsedAbout.purpose}\nApproach: ${parsedAbout.approach}\nOutcome: ${parsedAbout.outcome}\nNeed: ${parsedAbout.problem}`,
      images: productDetails.images,
      currency: 'USD',
      price: productDetails.price,
      quantity: productDetails.quantity,
      specs: [['Additional Comments', productDetails.comment]],
      shipping: [],
      proposalId: channel.id,
    };

    try {
      await raven?.createProduct(product);
      await raven?.updateProposal({ ...channel, readyForMarket: true } as Proposal);
      setProductDialogOpen(false);
      toast.success('Proposal successfully submitted to marketplace');
    } catch (error) {
      console.error('Error submitting proposal to marketplace:', error);
      toast.error('Failed to submit proposal to marketplace');
    }
  };

  return (
    <div style={{ padding: '40px 0' }}>
      <AppContentHeaderBase>
        <Box sx={{ flexGrow: 1, minWidth: 0 }}>
          <div className="">
            <div>
              {(channel.about) && (
                <div className="flex_2s">
                  <div>
                    <div style={{display:'flex',gap:'10px', alignItems:'center'}}>
                      {hasPicture && (
                        <Box
                          sx={{
                            display: 'flex',
                            mr: '10px',
                            flexShrink: 0,
                          }}
                        >
                          <Box
                            component="img"
                            sx={{
                              width: '50px',
                              height: '50px',
                              borderRadius: theme.shape.borderRadius,
                            }}
                            src={channel.picture}
                            alt={channel.name}
                          />
                        </Box>
                      )}
                      <Box
                        sx={{
                          fontFamily: 'Faktum, sans-serif',
                          ...styles.ellipsis,
                        }}
                      >
                        {channel.name}
                      </Box>
                    </div>
                    <Box
                      sx={{
                        color: theme.palette.primary.dark,
                        fontSize: '96%',
                        ...styles.ellipsis,
                      }}
                    >
                      {(() => {
                        if (false) {
                          return (
                            <p style={{ margin: '0', wordWrap: 'break-word', overflowWrap: 'break-word', whiteSpace: 'normal' }}>
                              This is a permanent proposal.
                            </p>
                          );
                        } else {
                          try {
                            console.log("Channel.about value: ");
                            console.log(channel.about);
                            const parsedAbout = JSON.parse(channel.about);
                            return (
                              <>
                                <p style={{ margin: '0', wordWrap: 'break-word', overflowWrap: 'break-word', whiteSpace: 'normal' }}>
                                  <span> Purpose: </span>{' '}
                                  {parsedAbout.purpose}
                                </p>
                                <p style={{ margin: '0', wordWrap: 'break-word', overflowWrap: 'break-word', whiteSpace: 'normal' }}>
                                  <span> Approach: </span>{' '}
                                  {parsedAbout.approach}
                                </p>
                                <p style={{ margin: '0', wordWrap: 'break-word', overflowWrap: 'break-word', whiteSpace: 'normal' }}>
                                  <span> Outcome: </span>{' '}
                                  {parsedAbout.outcome}
                                </p>
                                <p style={{ margin: '0', wordWrap: 'break-word', overflowWrap: 'break-word', whiteSpace: 'normal' }}>
                                  <span> Need: </span>{' '}
                                  {parsedAbout.problem}
                                </p>
                              </>
                            );
                          } catch (error) {
                            console.error('Error parsing channel about information:', error);
                            return null;
                          }
                        }
                      })()}
                    </Box>
                  </div>
                  <Box
                    sx={{
                      width: '50px',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      flexShrink: 0,
                    }}
                  >
                    <ChannelMenu />
                  </Box>
                </div>
              )}
            </div>
            {/* <ProposalDetails proposal={channel} /> */}
          </div>
          {!isTimeRemaining(channel.created, isPermanentProposal(channel.name) ? permVotingPeriod : votingPeriod) ? (
            <div className="flex_2s mt-3">
              <Box
                sx={{
                  color: theme.palette.primary.dark,
                  fontSize: '96%',
                  ...styles.ellipsis,
                }}
              >
                <span
                  className="text_success bold_m"
                  onClick={e => console.log(JSON.parse(channel.about))}
                >
                  Voting On Progress
                </span>
              </Box>
              <Box
                sx={{
                  color: theme.palette.primary.dark,
                  fontSize: '96%',
                  ...styles.ellipsis,
                }}
              >
                <span>
                  <CountdownButton
                    additionalMinutes={isPermanentProposal(channel.name) ? permVotingPeriod : votingPeriod}
                    createdAt={channel.created}
                  />
                </span>
              </Box>
            </div>
          ) : (
            <div className="flex_2s mt-3">
              <Box
                sx={{
                  color: theme.palette.primary.dark,
                  fontSize: '96%',
                  ...styles.ellipsis,
                }}
              >
                <span
                  className="text_success bold_m"
                  onClick={e => console.log(JSON.parse(channel.about))}
                >
                  Result initialized
                </span>
              </Box>
              <div
                style={{ display: 'flex', gap: '10px', marginBottom: '20px' }}
              >
                {/* Vote Result */}
                <Box
                  sx={{
                    color: theme.palette.primary.dark,
                    fontSize: '96%',
                    ...styles.ellipsis,
                  }}
                >
                  <span>
                    {(() => {
                      try {
                        const parsedAbout = JSON.parse(channel.about);
                        const { agreed, nonAgreed } = separateByAgreement(parsedAbout.voting);
                        return agreed.length > nonAgreed.length ? (
                          <button className="btn btn_success">
                            Success
                            <span className="ml-2">
                              <FaHeart />
                            </span>
                          </button>
                        ) : (
                          <button className="btn btn_success">
                            Proposal Failed
                            <span className="ml-2">
                              <FaHeartBroken />
                            </span>
                          </button>
                        );
                      } catch (error) {
                        console.error('Error parsing channel about information:', error);
                        return null;
                      }
                    })()}
                  </span>
                </Box>
                {/* Vote Down */}
                {channel.creator === keys.pub ? (
                  <Box
                    sx={{
                      color: theme.palette.primary.dark,
                      fontSize: '96%',
                      ...styles.ellipsis,
                    }}
                  >
                    <span>
                      <button
                        className="btn btn_primary"
                        onClick={e => uploadOnchain()}
                      >
                        Sync Proposal With OnChain
                      </button>
                    </span>
                  </Box>
                ) : (
                  ''
                )}
              </div>
            </div>
          )}

          {!isTimeRemaining(channel.created, isPermanentProposal(channel.name) ? permVotingPeriod : votingPeriod) ? (
            <div className="flex_2s mt-2 ">
              <Box
                sx={{
                  color: theme.palette.primary.dark,
                  fontSize: '96%',
                  ...styles.ellipsis,
                }}
              >
                <span className="text_success bold_m"> Received Vote </span>
              </Box>
              <div
                style={{ display: 'flex', gap: '10px', marginBottom: '20px' }}
              >
                {/* Vote Up */}
                <Box
                  sx={{
                    color: theme.palette.primary.dark,
                    fontSize: '96%',
                    ...styles.ellipsis,
                  }}
                >
                  <span>
                    {(() => {
                      try {
                        const parsedAbout = JSON.parse(channel.about);
                        const { agreed } = separateByAgreement(parsedAbout.voting);
                        return (
                          <button
                            className="btn btn_success"
                            onClick={e => doVote(true)}
                          >
                            {agreed.length}
                            <span className="ml-2">
                              <FaHeart />
                            </span>
                          </button>
                        );
                      } catch (error) {
                        console.error('Error parsing channel about information:', error);
                        return null;
                      }
                    })()}
                  </span>
                </Box>
                {/* Vote Down */}
                <Box
                  sx={{
                    color: theme.palette.primary.dark,
                    fontSize: '96%',
                    ...styles.ellipsis,
                  }}
                >
                  <span>
                    {(() => {
                      try {
                        const parsedAbout = JSON.parse(channel.about);
                        const { nonAgreed } = separateByAgreement(parsedAbout.voting);
                        return (
                          <button
                            className="btn btn_primary"
                            onClick={e => doVote(false)}
                          >
                            {nonAgreed.length}
                            <span className="ml-2">
                              <FaHeartBroken />
                            </span>
                          </button>
                        );
} catch (error) {
                        console.error('Error parsing channel about information:', error);
                        return null;
                      }
                    })()}
                  </span>
                </Box>
              </div>
            </div>
          ) : (
            <div className="flex_2s mt-2 ">
              <Box
                sx={{
                  color: theme.palette.primary.dark,
                  fontSize: '96%',
                  ...styles.ellipsis,
                }}
              >
                <span className="text_success bold_m">
                  Received Vote [Done]
                </span>
              </Box>
              <div
                style={{ display: 'flex', gap: '10px', marginBottom: '20px' }}
              >
                {/* Vote Up */}
                <Box
                  sx={{
                    color: theme.palette.primary.dark,
                    fontSize: '96%',
                    ...styles.ellipsis,
                  }}
                >
                  <span>
                    {(() => {
                      try {
                        const parsedAbout = JSON.parse(channel.about);
                        const { agreed } = separateByAgreement(parsedAbout.voting);
                        return (
                          <button className="btn btn_success">
                            {agreed.length}
                            <span className="ml-2">
                              <FaHeart />
                            </span>
                          </button>
                        );
                      } catch (error) {
                        console.error('Error parsing channel about information:', error);
                        return null;
                      }
                    })()}
                  </span>
                </Box>
                {/* Vote Down */}
                <Box
                  sx={{
                    color: theme.palette.primary.dark,
                    fontSize: '96%',
                    ...styles.ellipsis,
                  }}
                >
                  <span>
                    {(() => {
                      try {
                        const parsedAbout = JSON.parse(channel.about);
                        const { nonAgreed } = separateByAgreement(parsedAbout.voting);
                        return (
                          <button className="btn btn_primary">
                            {nonAgreed.length}
                            <span className="ml-2">
                              <FaHeartBroken />
                            </span>
                          </button>
                        );
                      } catch (error) {
                        console.error('Error parsing channel about information:', error);
                        return null;
                      }
                    })()}
                  </span>
                </Box>
              </div>
            </div>
          )}

        {isCreator && (
          <Button onClick={openProductDetailsDialog}>
            Submit to Marketplace
          </Button>
        )}

        <ProductDetailsDialog
          open={productDialogOpen}
          onClose={() => setProductDialogOpen(false)}
          onSubmit={handleProductSubmit}
          proposal={channel}
        />
      </Box>
    </AppContentHeaderBase>
    </div>
  );
};

export default ChannelHeader;