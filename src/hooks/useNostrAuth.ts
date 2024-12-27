import { useState } from 'react';
import { generatePrivateKey, getPublicKey, signEvent, verifySignature } from 'nostr-tools';

export const useNostrAuth = () => {
  const [privateKey, setPrivateKey] = useState<string | null>(null);
  const [publicKey, setPublicKey] = useState<string | null>(null);

  const generateKeys = () => {
    const privKey = generatePrivateKey();
    const pubKey = getPublicKey(privKey);
    setPrivateKey(privKey);
    setPublicKey(pubKey);
    return { privateKey: privKey, publicKey: pubKey };
  };

  const sign = (message: string) => {
    if (!privateKey) throw new Error('Private key not set');
    if (!publicKey) throw new Error('Public key not set');
    return signEvent({ pubkey: publicKey, content: message, created_at: Math.floor(Date.now() / 1000), kind: 1, tags: [] }, privateKey);
  };

  const verify = (message: string, signature: string, pubKey: string) => {
    const eventData = {
      id: '', // This will be computed by verifySignature
      pubkey: pubKey,
      content: message,
      created_at: Math.floor(Date.now() / 1000),
      kind: 1,
      tags: [],
      sig: signature
    };
    return verifySignature(eventData);
  };

  return { generateKeys, sign, verify, publicKey };
};
