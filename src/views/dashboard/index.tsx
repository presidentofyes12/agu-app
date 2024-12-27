import { Link, RouteComponentProps } from "@reach/router";
import { Helmet } from "react-helmet";
import AppWrapper from "views/components/app-wrapper";
import AppMenu from "views/components/app-menu";
import { useEffect, useState, useRef, useMemo } from "react";
import { Card, CardContent } from "@mui/material";
import { FaHeartbeat } from "react-icons/fa";
import { FaCloudUploadAlt } from "react-icons/fa";
import { FaFileImage } from "react-icons/fa";
import QRCode from 'qrcode.react';

import { useAtom } from "jotai";
import { keysAtom, profileAtom, ravenAtom } from "atoms";
import LoadingComponent from "views/components/LoadingComponent";
import DashboardContent from "views/components/app-content/DashboardContent";

import Box from '@mui/material/Box';
import { useNavigate } from '@reach/router';
import { nip19 } from 'nostr-tools';
import useModal from 'hooks/use-modal';
import ProfileDialog from 'views/components/dialogs/profile';

import { useRecoilState } from "recoil";
import { manageUserState, userState } from "state/userState";
import { FaArrowLeft } from "react-icons/fa6";

import { extractTextAndImage, fileUpload, formatTime } from "util/function";
import { SET_NOTE, SET_SEARCH_NOTE, SET_STOCK_NOTE } from "util/actionTypes";

const Dashboard = (props: RouteComponentProps) => {
  const [isPreviewMode, setIsPreviewMode] = useState(false);
  const [note, setNote] = useState("");
  const [notePicture, setNotePicture] = useState(null);
  const [pictureUploadPending, setPictureUploadPending] = useState(false);
  const [isNoteCreating, setIsNoteCreating] = useState(false);
  const [raven] = useAtom(ravenAtom);
  const [profile] = useAtom(profileAtom);
  const [searchText, setSearchText] = useState("");
  const [showSearchResult, setShowSearchResult] = useState(false);
  const [keys] = useAtom(keysAtom);

  const [getUserState, setUserState] = useRecoilState(userState);
  
  const navigate = useNavigate();
  const [, showModal] = useModal();

  const [qrCodeUrls, setQrCodeUrls] = useState<{ [key: string]: string }>({});
  const qrCodeRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (keys?.pub && !profile?.picture && !qrCodeUrls) {
      generateQRCode(keys?.pub);
    }
  }, [keys?.pub, profile?.picture, qrCodeUrls]);


const generateQRCode = (pubkey: string) => {
  if (qrCodeRef.current) {
    const encodedPubkey = nip19.npubEncode(pubkey);
    const canvas = qrCodeRef.current.querySelector(`canvas[data-pubkey="${encodedPubkey}"]`) as HTMLCanvasElement | null;
    if (canvas) {
      const url = canvas.toDataURL();
      setQrCodeUrls(prev => ({ ...prev, [pubkey]: url }));
    }
  }
};

  useEffect(() => {
    if (keys?.pub && !qrCodeUrls[keys.pub]) {
      generateQRCode(keys.pub);
    }
  }, [keys?.pub, qrCodeUrls]);

  const getProfilePicture = useMemo(() => (user: any) => {
    if (user?.content) {
      const parsedContent = JSON.parse(user.content);
      if (parsedContent.picture) {
        return parsedContent.picture;
      }
    }
    const pubkey = user?.pubkey || keys?.pub;
    return qrCodeUrls[pubkey] || null;
  }, [qrCodeUrls, keys?.pub]);

// profilePicture={getProfilePicture({ pubkey: keys?.pub })}

const handleProfileClick = () => {
  showModal({
    body: (
      <ProfileDialog
        profile={profile}
        pubkey={keys?.pub || ''}
        onDM={() => {
          navigate(`/profile/${nip19.npubEncode(keys?.pub || '')}`).then();
        }}
      />
    ),
    maxWidth: 'xs',
    hideOnBackdrop: true,
  });
};

// qrCodeUrl={qrCodeUrl}

  useEffect(() => {
    const init = async () => {
      const stockNotes = await raven?.fetchStockNote();
      manageUserState(
        SET_STOCK_NOTE,
        { data: stockNotes },
        setUserState,
        getUserState
      );
    };
    if (raven) {
      init();
    }
  }, [raven]);

  const doneCreateNote = (createdEvent: any) => {
    setIsNoteCreating(false);
    setNotePicture(null);
    setIsPreviewMode(false);
    setNote("");
    manageUserState(
      SET_NOTE,
      { data: { ...createdEvent, user: { content: JSON.stringify(profile) } } },
      setUserState,
      getUserState
    );
  };
  const handleNoteSubmit = () => {
    raven?.createNote(
      `
      ${note}
      ${notePicture}
    `,
      doneCreateNote,keys?.priv
    );
  };
  const keyDownHandler = async (event: any) => {
    if (event.key.toLocaleLowerCase() == "enter") {
      setShowSearchResult(true);
      // Scroll down by 500 pixels
      window.scrollBy({
        top: 500,
        behavior: "smooth", // You can change this to 'auto' for instant scrolling
      });
      const searchNote = await raven?.searchOnNostr(searchText);
      manageUserState(
        SET_SEARCH_NOTE,
        { data: searchNote },
        setUserState,
        getUserState
      );
    }
  };
  return (
    <>
      <Helmet>
        <title>Home</title>
      </Helmet>
      <AppWrapper>
        <AppMenu />
        <DashboardContent>
          <div className="search_bar">
            <input
              placeholder="#BTC"
              className="form-control"
              onChange={(e) => setSearchText(e.target.value)}
              value={searchText}
              onKeyDown={(e) => keyDownHandler(e)}
              type="text"
            />
          </div>
          <div className="row">
            <div className="mt-5 col-12 col-md-8 offset-md-2">
              <Card>
                <CardContent>
                  <div className="row pb-4 mt-5">
                    <div className="col-sm-11 ms-auto">
<div className="user_profile_box">
  <Box onClick={handleProfileClick} sx={{ cursor: 'pointer' }}>
    {profile?.picture ? (
      <img src={profile.picture} alt="Profile" />
    ) : qrCodeUrls[keys?.pub || ''] ? (
      <img src={qrCodeUrls[keys?.pub || '']} alt="QR Code" />
    ) : (
      <div ref={qrCodeRef}>
        <QRCode value={nip19.npubEncode(keys?.pub || '')} data-pubkey={nip19.npubEncode(keys?.pub || '')} />
      </div>
    )}
  </Box>
  <div>
    <Box
      onClick={handleProfileClick}
      sx={{
        fontWeight: '600',
        mr: '5px',
        cursor: 'pointer',
        '& h5': {
          '&:hover': {
            textDecoration: 'underline',
          },
        },
      }}
    >
      <h5 onClick={handleProfileClick}>Hi {profile?.name}</h5>
    </Box>
    <p>
      <strong>{profile?.about ? profile.about : "N/A"}</strong>
    </p>
  </div>
</div>
                      <div className="mb-3 mt-4">
                        {isPreviewMode ? (
                          <div className="note_preview">
                            <h4> {note} </h4>
                            {notePicture ? <img src={notePicture} /> : ""}
                          </div>
                        ) : (
                          <>
                            <textarea
                            maxLength={200}
                              style={{
                                background: "transparent",
                                border: "0",
                                fontSize: "26px",
                                color: "white",
                              }}
                              className="form-control"
                              rows={3}
                              onChange={(e) => setNote(e.target.value)}
                              placeholder="What's on your mind ? [200]"
                              value={note}
                            />
                            {notePicture ? (
                              <p>
                                <FaFileImage /> File Uploaded !!
                              </p>
                            ) : (
                              ""
                            )}
                          </>
                        )}
                      </div>
                      <div>
                        <div className="upload_panal">
                          {!pictureUploadPending ? (
                            <span
                              className="cp"
                              onClick={(e) =>
                                document
                                  .getElementById("upload_note_image")
                                  ?.click()
                              }
                            >
                              <input
                                id="upload_note_image"
                                type="file"
                                onChange={(e) =>
                                  fileUpload(
                                    e,
                                    setNotePicture,
                                    setPictureUploadPending
                                  )
                                }
                                accept="image/*"
                                style={{ display: "none" }}
                              />
                              <button className="btn btn_primary">
                                <FaCloudUploadAlt /> <span>Upload Image</span>
                              </button>
                            </span>
                          ) : (
                            ""
                          )}
                          <button
                            onClick={(e) => setIsPreviewMode(!isPreviewMode)}
                            className="btn btn_success"
                          >
                            {isPreviewMode ? "Edit Note" : "Preview"}
                          </button>
                          {isNoteCreating ? (
                            <button className="btn btn_success">
                              Sending ...
                            </button>
                          ) : pictureUploadPending ? (
                            <button className="btn btn_success">
                              File Processing ...
                            </button>
                          ) : (
                            <button
                              onClick={(e) => handleNoteSubmit()}
                              className="btn btn_success"
                            >
                              Send
                            </button>
                          )}
                        </div>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>
          <div className="row">
            {showSearchResult ? (
              <div className="col-12 col-md-8 offset-md-2">
                {getUserState.searchedNote.length < 1 ? (
                  <>
                    <LoadingComponent />
                  </>
                ) : (
                  <div className="mt-5">
                    <div
                      style={{
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "space-between",
                      }}
                    >
                      <button
                        className="btn btn_success"
                        onClick={(e) => {
                          setShowSearchResult(false);
                          setSearchText("");
                        }}
                      >
                        <span>
                          <FaArrowLeft />
                        </span>
                        Go to Home
                      </button>
                      <h4>Search result for "#{searchText}"</h4>
                    </div>
                    <hr />

{getUserState.searchedNote.map((note: any, i) => (
  <Card className="mb-4 pb-4" key={i}>
    <div className="col-sm-11 ms-auto mt-5">
      <div className="user_profile_box user_profile_link">
        <img src={getProfilePicture(note.user) || '/img/loading.gif'} alt="User" />
        <div>
          <Link to={"#"}>
            <h5 style={{ textTransform: "capitalize" }}>
              {note.user?.content
                ? JSON.parse(note.user.content).name
                : "Nostr User"}
            </h5>
          </Link>
          <p> {formatTime(note.created_at)} </p>
        </div>
      </div>
                          {/* main post  title and pic */}
                          <div className="mb-3 mt-4 post_content">
                            {extractTextAndImage(note.content).text ? (
                              <p> {extractTextAndImage(note.content).text} </p>
                            ) : (
                              ""
                            )}
                            {extractTextAndImage(note.content).img ? (
                              <img
                                src={extractTextAndImage(note.content).img}
                              />
                            ) : (
                              ""
                            )}
                          </div>
                          <div>
                            <div className="upload_panal">
                              <div className="post_reaction_item">
                                <span className="reaction_icon">
                                  <FaHeartbeat />
                                </span>
                                <span> {note.tags.length} </span>
                              </div>
                            </div>
                          </div>
                        </div>
                      </Card>
                    ))}
                  </div>
                )}
              </div>
            ) : (
              <div className="col-12 col-md-8 offset-md-2">
                {getUserState.stockNote.length < 1 ? (
                  <>
                    <LoadingComponent />
                  </>
                ) : (
                  <div className="mt-5">
                    {getUserState.stockNote.map((note: any, i) => (
  <Card className="mb-4 pb-4" key={i}>
    <div className="col-sm-11 ms-auto mt-5">
      <div className="user_profile_box user_profile_link">
        <img src={getProfilePicture(note.user) || '/img/loading.gif'} alt="User" />
        <div>
          <Link to={"#"}>
            <h5 style={{ textTransform: "capitalize" }}>
              {note.user?.content
                ? JSON.parse(note.user.content).name
                : "Nostr User"}
            </h5>
          </Link>
          <p> {formatTime(note.created_at)} </p>
        </div>
      </div>
                          {/* main post  title and pic */}
                          <div className="mb-3 mt-4 post_content">
                            {extractTextAndImage(note.content).text ? (
                              <p> {extractTextAndImage(note.content).text} </p>
                            ) : (
                              ""
                            )}
                            {extractTextAndImage(note.content).img ? (
                              <img
                                src={extractTextAndImage(note.content).img}
                              />
                            ) : (
                              ""
                            )}
                          </div>
                          <div>
                            <div className="upload_panal">
                              <div className="post_reaction_item">
                                <span className="reaction_icon">
                                  <FaHeartbeat />
                                </span>
                                <span> {note.tags.length} </span>
                              </div>
                            </div>
                          </div>
                        </div>
                      </Card>
                    ))}
                  </div>
                )}
              </div>
            )}
          </div>
        </DashboardContent>
      </AppWrapper>
    </>
  );
};

export default Dashboard;