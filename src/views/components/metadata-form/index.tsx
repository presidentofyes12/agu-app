import React, { useEffect, useState } from 'react';
import Joi from 'joi';
import Box from '@mui/material/Box';
import TextField from '@mui/material/TextField';
import Button from '@mui/material/Button';
import { CircularProgress } from '@mui/material';
import { toast } from 'react-toastify';

import useTranslation from 'hooks/use-translation';
// import PictureInput from "views/components/picture-input";
import { Metadata } from 'types';
//import QRCode from 'qrcode';
import axios from 'axios';
import { UPLOAD_API_KEY, proposalTypes } from 'util/constant';

const MetadataForm = (props: {
  values?: Metadata;
  labels?: Metadata;
  submitBtnLabel: string;
  skipButton: React.ReactElement;
  onSubmit: (data: Metadata) => void;
  inProgress?: boolean;
}) => {
  const { skipButton, submitBtnLabel, values, labels, onSubmit, inProgress } =
    props;
  const [name, setName] = useState(values?.name || '');
  const [about, setAbout] = useState(values?.about || '');
  const [picture, setPicture] = useState(values?.picture || '');
  const [t] = useTranslation();
  const [error, setError] = useState('');
  const [errorMessage, setErrorMessage] = useState('');
  const [changed, setChanged] = useState(false);
  const [uploading, setUploading] = useState(false);

  useEffect(() => {
    if (values && !changed) {
      setName(values.name);
      setAbout(values.about);
      setPicture(values.picture);
    }
  }, [values]);

  const resetError = () => {
    setError('');
    setErrorMessage('');
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

  const handleFileUpload = (event: any) => {
    if (event.target.files[0]) {
      const formData = new FormData();
      formData.append('image', event.target.files[0]);
      setUploading(true);
      axios
        .post(`https://api.imgbb.com/1/upload?key=${UPLOAD_API_KEY}`, formData)
        .then((response: any) => {
          if (response.data) {
            console.log('file settled');
            pictureChanged(response.data.data.url);
          }
          setUploading(false);
        })
        .catch((error: any) => {
          console.error('Upload failed:', error);
        })
        .finally(() => {
          console.log('file upload done');
        });
    }
  };

  //  New proposal form
  const [proposalType, setProposalType] = useState('');
  const [formData, setFormData] = useState<{
    problem: string;
    solution: string;
    targetAudience: string;
    qualifications: string;
    purpose: string;
    approach: string;
    outcome: string;
    timeline: string;
    budget: string;
    callToAction: string;
    voting:object
  }>({
    problem: '',
    solution: '',
    targetAudience: '',
    qualifications: '',
    purpose: '',
    approach: '',
    outcome: '',
    timeline: '',
    budget: '',
    callToAction: '',
    voting:[]
  });
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleProposalTypeChange = (
    e: React.ChangeEvent<HTMLSelectElement>
  ) => {
    const selectedProposalType = e.target.value;
    setProposalType(selectedProposalType);

    // Find the selected proposal type from the proposalTypes array
    const selectedProposal = proposalTypes.find(
      type => type.name === selectedProposalType
    );

    if (selectedProposal) {
      // Update formData with purpose, approach, and outcome from selected proposal
      setFormData({
        ...formData,
        purpose: selectedProposal.purpose,
        approach: selectedProposal.approach,
        outcome: selectedProposal.outcome,
      });
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: value,
    });
  };
  const submit = () => {
    setIsSubmitting(true)
    const metadata = {
      name: formData.approach,
      about: JSON.stringify(formData),
      picture: picture,
    };
    onSubmit(metadata);
  };
  return (
    <>
      <div style={{ textAlign: 'center' }}>
        <div>
          <div style={{ marginBottom: '20px' }}>
            <img
              className="user_pic"
              src={picture ? picture : '/img/proposal.png'}
            />
          </div>
          {uploading ? (
            <>
              <CircularProgress size={20} sx={{ mr: '8px' }} /> Uploading Image
              ...
            </>
          ) : (
            <Button
              variant="contained"
              onClick={e =>
                document.getElementById('upload_profile_pic')?.click()
              }
            >
              + Upload
            </Button>
          )}
          <br />
          <input
            style={{ visibility: 'hidden' }}
            onChange={e => handleFileUpload(e)}
            type="file"
            accept="image/x-png,image/gif,image/jpeg"
            id="upload_profile_pic"
          />
        </div>

        <div className="text-left">
          <div style={{ textAlign: 'left' }}>
            <label>Proposal Type:</label>
            <select
              className="form-control in_bg_tr"
              value={proposalType}
              onChange={handleProposalTypeChange}
            >
              <option value="">Select a proposal type</option>
              {proposalTypes.map((type, i) => (
                <option key={i} value={type.name}>
                  {type.name}
                </option>
              ))}
            </select>
          </div>
          {proposalType && (
            <>
              <div>
                <label>Purpose:</label>
                <textarea
                  name="purpose"
                  placeholder="Purpose"
                  className="no_border form-control in_bg_tr"
                  value={formData.purpose}
                  onChange={handleInputChange}
                />
              </div>
              <div>
                <label>Approach:</label>
                <textarea
                  className="no_border form-control in_bg_tr"
                  name="approach"
                  value={formData.approach}
                  onChange={handleInputChange}
                />
              </div>
              <div>
                <label>Outcome:</label>
                <textarea
                  className="no_border form-control in_bg_tr"
                  name="outcome"
                  value={formData.outcome}
                  onChange={handleInputChange}
                />
              </div>
            </>
          )}
          <div>
            <label>Problem:</label>
            <textarea
              className="form-control in_bg_tr"
              name="problem"
              value={formData.problem}
              onChange={handleInputChange}
            />
          </div>
          {proposalType && formData.problem ? (
            <button
              type="submit"
              className="btn btn_success mt-3"
              disabled={isSubmitting}
              onClick={e => submit()}
            >
              {isSubmitting ? 'Submitting...' : 'Submit'}
            </button>
          ) : (
            <button
              type="submit"
              className="btn btn_success mt-3"
              onClick={e => toast.error('Form incomplete, Fill it Up !')}
            >
              Submit
            </button>
          )}
        </div>
      </div>
    </>
  );
};

export default MetadataForm;