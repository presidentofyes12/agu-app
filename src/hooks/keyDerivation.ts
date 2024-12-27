// keyDerivation.ts
import { nip06 } from 'nostr-tools';
//import { generateSeedWords, privateKeyFromSeedWords } from 'nostr-tools';
import * as bip39 from 'bip39';

export const generateFirstGenKeys = () => {
  try {
    const mnemonic = nip06.generateSeedWords();
    const privateKey = nip06.privateKeyFromSeedWords(mnemonic);
    return { mnemonic, privateKey };
  } catch (error) {
    console.error("Error generating keys:", error);
    return { mnemonic: null, privateKey: null };
  }
};

export const deriveSecondGenKeys = (firstGenPrivateKey: string) => {
  const secondGenMnemonic = bip39.entropyToMnemonic(firstGenPrivateKey);
  const secondGenPrivateKey = nip06.privateKeyFromSeedWords(secondGenMnemonic);
  return { mnemonic: secondGenMnemonic, privateKey: secondGenPrivateKey };
};

export const generateCredentials = (secondGenPrivateKey: string) => {
  const username = bip39.entropyToMnemonic(secondGenPrivateKey).split(' ').slice(0, 3).join('-');
  const password = bip39.entropyToMnemonic(secondGenPrivateKey).split(' ').slice(3, 6).join('-');
  return { username, password };
};