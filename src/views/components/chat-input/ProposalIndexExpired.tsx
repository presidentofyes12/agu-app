import React, { useEffect, useRef } from 'react';
import { EditorContent, JSONContent } from '@tiptap/react';
import Box from '@mui/material/Box';
import { useTheme } from '@mui/material/styles';
import { IoWarningOutline } from 'react-icons/io5';
import useMediaBreakPoint from 'hooks/use-media-break-point';
import useMakeEditor from 'views/components/chat-input/editor';
import {
  getEditorValue,
  removeEditorValue,
  storeEditorValue,
} from 'local-storage';
import { PLATFORM } from 'const';

const ProposalIndexExpired = (props: {
  separator: string;
  senderFn: (message: string, mentions: string[]) => Promise<any>;
}) => {
  const { senderFn, separator } = props;
  const theme = useTheme();
  const { isMd } = useMediaBreakPoint();
  const inputRef = useRef<HTMLDivElement | null>(null);
  const storageKey = `${separator}_msg`;

  const save = () => {
    const val = editor?.getHTML();
    if (!val) {
      removeEditorValue(storageKey);
      return;
    }
    storeEditorValue(storageKey, val);
  };

  const editor = useMakeEditor({
    content: getEditorValue(storageKey) || '',
    onUpdate: save,
  });

  useEffect(() => {
    editor?.commands.setContent(getEditorValue(storageKey) || '');
    if (PLATFORM === 'web') {
      editor?.commands.focus();
    }
  }, [storageKey]);
 

  return (
    <Box sx={{ p: 2, borderTop: '1px solid rgba(255, 255, 255, 0.12)' }}>
      <Box
        sx={{
          background: theme.palette.divider,
          borderRadius: theme.shape.borderRadius,
        }}
      >
        <Box sx={{ p: '10px 10px' }}>
          <p style={{ padding:'20px 10px' }}>
            <span style={{marginRight:'10px'}}>
              <IoWarningOutline />
            </span>
            Proposal Voting Period Expired !!
          </p>
        </Box>
      </Box>
    </Box>
  );
};

export default ProposalIndexExpired;
