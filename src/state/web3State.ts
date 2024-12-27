import { atom } from 'jotai';
import { ethers } from 'ethers';

export const providerAtom = atom<ethers.providers.Web3Provider | null>(null);
export const signerAtom = atom<ethers.Signer | null>(null);
export const accountAtom = atom<string | null>(null);
export const chainIdAtom = atom<number | null>(null);
export const isConnectedAtom = atom<boolean>(false);

// Derived atoms for contract state
export const balanceAtom = atom<string>('0');
export const familyInfoAtom = atom<{
  familyId: number;
  familySize: number;
  relationships: number[];
} | null>(null);
