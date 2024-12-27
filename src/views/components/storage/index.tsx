// @ts-nocheck

import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Box, TextField, Button, List, ListItem, ListItemText, Typography, Select, MenuItem, FormControl, InputLabel, CircularProgress } from '@mui/material';
import { RouteComponentProps } from '@reach/router';
import { useAtom } from 'jotai';
import { directMessagesAtom, profilesAtom, ravenAtom } from 'atoms';
import { DirectContact } from 'types';
import { nip19 } from 'nostr-tools';
import { v4 as uuidv4 } from 'uuid';
import AppWrapper from 'views/components/app-wrapper';
import AppMenu from 'views/components/app-menu';

interface StorageProps extends RouteComponentProps {}

interface Proposal {
  id: string;
  header: string;
  content: string;
  owner: string;
  modifiedAt?: Date;
  size?: number;
}

const Storage: React.FC<StorageProps> = (props) => {
  const [proposals, setProposals] = useState<Proposal[]>([]);
  const [newProposal, setNewProposal] = useState('');
  const [fileContent, setFileContent] = useState('');
  const [fileName, setFileName] = useState('');
  const [selectedContact, setSelectedContact] = useState<DirectContact | null>(null);
  const [fileIdToShare, setFileIdToShare] = useState('');
  const [fileIdToView, setFileIdToView] = useState('');
  const [directMessages] = useAtom(directMessagesAtom);
  const [profiles] = useAtom(profilesAtom);
  const [raven] = useAtom(ravenAtom);
  const [isUploading, setIsUploading] = useState(false);
  const [isDownloading, setIsDownloading] = useState(false);

  useEffect(() => {
    const savedProposals = JSON.parse(localStorage.getItem('proposals') || '[]') as Proposal[];
    setProposals(savedProposals);
  }, []);

  const generateFileId = (fileName: string): string => {
    const transactionId = uuidv4();
    const extension = fileName.split('.').pop() || '';
    const timestamp = Date.now();
    return `${transactionId}_${timestamp}.${extension}`;
  };

  const saveProposal = async () => {
    setIsUploading(true);
    try {
      const newId = generateFileId('manual_entry.txt');
      await axios.post('http://localhost:3001/upload', { content: newProposal, fileId: newId });
      const updatedProposals = [...proposals, { id: newId, header: 'Manual Entry', content: newProposal, owner: 'self' }];
      setProposals(updatedProposals);
      localStorage.setItem('proposals', JSON.stringify(updatedProposals));
      setNewProposal('');
    } catch (err) {
      console.error("Error saving proposal:", err);
      alert("Failed to save proposal. Please try again.");
    } finally {
      setIsUploading(false);
    }
  };

  const deleteProposal = async (id: string) => {
    try {
      await axios.delete(`http://localhost:3001/delete/${id}`);
      const updatedProposals = proposals.filter(proposal => proposal.id !== id);
      setProposals(updatedProposals);
      localStorage.setItem('proposals', JSON.stringify(updatedProposals));
    } catch (err) {
      console.error("Error deleting proposal:", err);
      alert("Failed to delete proposal. Please try again.");
    }
  };

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file && file.type === 'text/plain') {
      setFileName(file.name);
      const reader = new FileReader();
      reader.onload = (e) => {
        const result = e.target?.result;
        if (typeof result === 'string') {
          setFileContent(result);
        }
      };
      reader.readAsText(file);
    } else {
      alert('Please upload a .txt file');
    }
  };

const saveFileContent = async () => {
  setIsUploading(true);
  try {
    const newId = generateFileId(fileName);
    const response = await axios.post('http://localhost:3001/upload', { 
      content: fileContent,  // Ensure this is a string
      fileId: newId 
    });
    console.log("Server response:", response.data);
    if (response.data.success) {
      const updatedProposals = [...proposals, { id: newId, header: fileName, content: fileContent, owner: 'self' }];
      setProposals(updatedProposals);
      localStorage.setItem('proposals', JSON.stringify(updatedProposals));
      setFileContent('');
      setFileName('');
    } else {
      throw new Error(response.data.error || "Unknown error occurred");
    }
  } catch (err) {
    console.error("Error saving file content:", err);
    alert(`Failed to save file content. ${err.response?.data?.error || err.message}`);
  } finally {
    setIsUploading(false);
  }
};

  const shareFile = async () => {
    if (selectedContact && fileIdToShare) {
      try {
        await raven?.sendDirectMessage(selectedContact.pub, `Shared file: ${fileIdToShare}`);
        console.log(`Sharing file ${fileIdToShare} with contact ${selectedContact.npub}`);
        alert("File shared successfully!");
      } catch (err) {
        console.error("Error sharing file:", err);
        alert("Failed to share file. Please try again.");
      }
    }
  };

  const viewSharedFile = async () => {
    setIsDownloading(true);
    const maxRetries = 3;
    let retries = 0;

    const attemptDownload = async () => {
      try {
        const response = await axios.get(`http://localhost:3001/download/${fileIdToView}`);
        console.log("Server response:", response.data);
        if (response.data.success) {
          const { fileInfo, content } = response.data;
          
          // Save the file as a shared file
          const newSharedFile: Proposal = {
            id: fileInfo.id,
            header: fileInfo.name,
            content: content,
            owner: 'shared', // or you could set this to the actual owner if available
            modifiedAt: new Date(fileInfo.modifiedAt),
            size: fileInfo.size
          };

          setProposals(prevProposals => [...prevProposals, newSharedFile]);
          
          // Update localStorage
          const updatedProposals = [...proposals, newSharedFile];
          localStorage.setItem('proposals', JSON.stringify(updatedProposals));

          alert(`File "${fileInfo.name}" has been saved as a shared file.`);
        } else {
          throw new Error(response.data.error || "Unknown error occurred");
        }
      } catch (err) {
        console.error("Error viewing shared file:", err);
        if (retries < maxRetries) {
          retries++;
          console.log(`Retrying download (attempt ${retries})`);
          await new Promise(resolve => setTimeout(resolve, 1000)); // Wait 1 second before retrying
          return attemptDownload();
        }
        let errorMessage = "Failed to view shared file. ";
        if (err.response && err.response.data) {
          errorMessage += err.response.data.error || "";
          console.error("Detailed error:", err.response.data);
        } else {
          errorMessage += err.message;
        }
        alert(errorMessage);
      }
    };

    await attemptDownload();
    setIsDownloading(false);
  };

  const uniqueContacts = Array.from(new Set(directMessages.map(dm => dm.peer)))
    .map(peer => ({
      pub: peer,
      npub: nip19.npubEncode(peer)
    }));

  console.log(proposals.filter(proposal => proposal.id));

  return (
    <AppWrapper>
    <AppMenu />
    <Box sx={{ width: '100%', maxWidth: 600, mx: 'auto', mt: 4 }}>
      <Typography variant="h4" gutterBottom>Storage</Typography>
      
      <TextField
        label="New Proposal"
        value={newProposal}
        onChange={(e) => setNewProposal(e.target.value)}
        fullWidth
        margin="normal"
      />
      <Button 
        variant="contained" 
        onClick={saveProposal}
        disabled={isUploading}
      >
        {isUploading ? <CircularProgress size={24} /> : 'Save Proposal'}
      </Button>

      <Box sx={{ mt: 2 }}>
        <input
          type="file"
          accept=".txt"
          onChange={handleFileUpload}
        />
        <Button
          variant="contained"
          onClick={saveFileContent}
          disabled={!fileContent || isUploading}
          sx={{ mt: 1 }}
        >
          {isUploading ? <CircularProgress size={24} /> : 'Save File Content'}
        </Button>
      </Box>

      <Box sx={{ mt: 2 }}>
        <Typography variant="h6">Share File</Typography>
        <FormControl fullWidth sx={{ mt: 1 }}>
          <InputLabel>Select Contact</InputLabel>
          <Select
            value={selectedContact?.pub || ''}
            onChange={(e) => {
              const contact = uniqueContacts.find(c => c.pub === e.target.value);
              setSelectedContact(contact || null);
            }}
          >
            {uniqueContacts.map((contact) => (
              <MenuItem key={contact.pub} value={contact.pub}>
                {profiles.find(p => p.creator === contact.pub)?.name || contact.npub}
              </MenuItem>
            ))}
          </Select>
        </FormControl>
        <TextField
          label="File ID to Share"
          value={fileIdToShare}
          onChange={(e) => setFileIdToShare(e.target.value)}
          fullWidth
          margin="normal"
        />
        <Button variant="contained" onClick={shareFile}>Share File</Button>
      </Box>

      <Box sx={{ mt: 2 }}>
        <Typography variant="h6">View Shared File</Typography>
        <TextField
          label="File ID to View"
          value={fileIdToView}
          onChange={(e) => setFileIdToView(e.target.value)}
          fullWidth
          margin="normal"
        />
        <Button 
          variant="contained" 
          onClick={viewSharedFile}
          disabled={isDownloading}
        >
          {isDownloading ? <CircularProgress size={24} /> : 'View Shared File'}
        </Button>
      </Box>

      <Typography variant="h6" sx={{ mt: 2 }}>Your Files</Typography>
      <List>
        {proposals.filter(p => p.owner === 'self').map(proposal => (
          <ListItem key={proposal.id}>
            <ListItemText
              primary={proposal.header}
              secondary={`ID: ${proposal.id}`}
            />
            <Button onClick={() => deleteProposal(proposal.id)}>Delete</Button>
          </ListItem>
        ))}
      </List>

    <Typography variant="h6" sx={{ mt: 2 }}>Shared Files</Typography>
    <List>
      {proposals.filter(p => p.owner === 'shared').map(proposal => (
        <ListItem key={proposal.id}>
          <ListItemText
            primary={proposal.header}
            secondary={`ID: ${proposal.id}, Size: ${proposal.size} bytes, Modified: ${proposal.modifiedAt?.toLocaleString()}`}
          />
          <Button onClick={() => alert(proposal.content)}>View Content</Button>
        </ListItem>
      ))}
    </List>
    </Box>
  </AppWrapper>
  );
};

export default Storage;
