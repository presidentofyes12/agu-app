import React, { useEffect, useState } from "react";
import Joi from "joi";
import Box from "@mui/material/Box";
import TextField from "@mui/material/TextField";
import Button from "@mui/material/Button";
import { CircularProgress } from "@mui/material";
import QRCode from "qrcode.react";
import { nip19 } from "nostr-tools";

import useTranslation from "hooks/use-translation";
import { Metadata } from "types";
import axios from "axios";
import { useAtom } from "jotai";
import { keysAtom } from "atoms";
import { UPLOAD_API_KEY } from "util/constant";

const LoginMetadataForm = (props: {
  values?: Metadata;
  labels?: Metadata;
  submitBtnLabel: string;
  skipButton: React.ReactElement;
  onSubmit: (data: Metadata) => void;
  inProgress?: boolean;
}) => {
  const { skipButton, submitBtnLabel, values, labels, onSubmit, inProgress } =
    props;
  const [name, setName] = useState(values?.name || "");
  const [about, setAbout] = useState(values?.about || "");
  const [picture, setPicture] = useState(values?.picture || "");
  const [t] = useTranslation();
  const [error, setError] = useState("");
  const [errorMessage, setErrorMessage] = useState("");
  const [changed, setChanged] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [keys] = useAtom(keysAtom);

  useEffect(() => {
    if (values && !changed) {
      setName(values.name);
      setAbout(values.about);
      setPicture(values.picture);
    }
  }, [values]);

  const resetError = () => {
    setError("");
    setErrorMessage("");
  };

  const nameChanged = (
    e: React.ChangeEvent<HTMLTextAreaElement | HTMLInputElement>
  ) => {
    resetError();
    setName(e.target.value);
    setChanged(true);
  };

  const aboutChanged = (
    e: React.ChangeEvent<HTMLTextAreaElement | HTMLInputElement>
  ) => {
    resetError();
    setAbout(e.target.value);
    setChanged(true);
  };

  const pictureChanged = (picture: string) => {
    resetError();
    setPicture(picture);
    setChanged(true);
  };

  const submit = () => {
    const scheme = Joi.object({
      name: Joi.string().required(),
      about: Joi.string().empty(""),
      picture: Joi.string()
        .uri({ scheme: "https", allowRelative: false })
        .empty(""),
    }).messages({
      "string.uriCustomScheme": t(
        "Picture must be a valid uri with a scheme matching the https pattern"
      ),
    });

    const metadata = { name, about, picture };
    const validation = scheme.validate(metadata);

    if (validation.error) {
      setError(validation.error.details[0].path[0].toString() || "");
      setErrorMessage(validation.error.details[0].message);
      return;
    }

    onSubmit(metadata);
  };

  const handleFileUpload = (event: any) => {
    if (event.target.files[0]) {
      const formData = new FormData();
      formData.append("image", event.target.files[0]);
      setUploading(true);
      axios
        .post(`https://api.imgbb.com/1/upload?key=${UPLOAD_API_KEY}`, formData)
        .then((response: any) => {
          if (response.data) {
            pictureChanged(response.data.data.url);
          }
          setUploading(false);
        })
        .catch((error: any) => {
          console.error("Upload failed:", error);
        })
        .finally(() => {
          console.log("file upload done");
        });
    }
  };

  return (
    <>
      <div style={{ textAlign: "center" }}>
        <div>
          <div style={{ marginBottom: '20px' }}>
            {picture ? (
              <img className="user_pic" src={picture} />
            ) : (
              keys?.pub && (
                <QRCode
                  value={nip19.npubEncode(keys.pub)}
                  size={150}
                  includeMargin={false}
                  renderAs="svg"
                  style={{
                    width: '150px',
                    height: '150px',
                  }}
                />
              )
            )}
          </div>
          {uploading ? (
            <>
              <CircularProgress size={20} sx={{ mr: "8px" }} /> Uploading Image
              ...
            </>
          ) : (
            <Button
              variant="contained"
              onClick={(e) =>
                document.getElementById("upload_profile_pic")?.click()
              }
            >
              + Upload
            </Button>
          )}
          <br />
          <input
            style={{ visibility: "hidden" }}
            onChange={(e) => handleFileUpload(e)}
            type="file"
            accept="image/x-png,image/gif,image/jpeg"
            id="upload_profile_pic"
          />
        </div>
        <TextField
          label={t(labels?.name || "Name")}
          value={name}
          onChange={nameChanged}
          fullWidth
          autoFocus
          autoComplete="off"
          error={error === "name"}
          helperText={error === "name" ? errorMessage : " "}
        />

        <TextField
          label={t(labels?.about || "About")}
          value={about}
          onChange={aboutChanged}
          fullWidth
          autoComplete="off"
          helperText=""
        />
        <Box sx={{ display: "flex", justifyContent: "space-between" }}>
          <Button
            style={{ marginTop: "20px" }}
            variant="contained"
            disabled={inProgress}
            onClick={submit}
          >
            {inProgress ? "Updating ..." : submitBtnLabel}
          </Button>
        </Box>
      </div>
    </>
  );
};

export default LoginMetadataForm;
