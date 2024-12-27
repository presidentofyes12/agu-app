import React, { useMemo } from 'react';
import Box from '@mui/material/Box';
import { useTheme } from '@mui/material/styles';
import QRCode from 'qrcode.react';
import { nip19 } from 'nostr-tools';

interface AvatarProps {
  src?: string;
  seed: string;
  size: number;
  rounded?: boolean;
}

const Avatar: React.FC<AvatarProps> = ({ src, seed, size, rounded }) => {
  const theme = useTheme();

  const avatar = useMemo(() => {
    if (src && src.startsWith('https://')) {
      return src;
    }
    return null;
  }, [src]);

  return (
    <Box
      sx={{
        background: theme.palette.divider,
        borderRadius: rounded ? '50%' : theme.shape.borderRadius,
        width: `${size}px`,
        height: `${size}px`,
        objectFit: 'cover',
      }}
    >
      {avatar ? (
        <img
          src={avatar}
          style={{
            width: '100%',
            height: '100%',
            borderRadius: rounded ? '50%' : theme.shape.borderRadius,
            objectFit: 'cover',
          }}
          alt="Avatar"
        />
      ) : (
        <QRCode
          value={nip19.npubEncode(seed)}
          size={size}
          includeMargin={false}
          renderAs="svg"
          style={{
            width: '100%',
            height: '100%',
            borderRadius: rounded ? '50%' : theme.shape.borderRadius,
          }}
        />
      )}
    </Box>
  );
};

export default Avatar;