// src/hooks/useModularDAO.ts
import { useAtom } from 'jotai';
import { ethers } from 'ethers';
import {
  providerAtom,
  signerAtom,
  accountAtom,
  chainIdAtom,
  isConnectedAtom,
  balanceAtom,
  familyInfoAtom
} from '../state/web3State';

export function useModularDAO() {
  const [provider, setProvider] = useAtom(providerAtom);
  const [, setSigner] = useAtom(signerAtom);
  const [account, setAccount] = useAtom(accountAtom);
  const [, setChainId] = useAtom(chainIdAtom);
  const [, setIsConnected] = useAtom(isConnectedAtom);
  const [, setBalance] = useAtom(balanceAtom);
  const [familyInfo, setFamilyInfo] = useAtom(familyInfoAtom);

  const connectWallet = async () => {
    if (!window.ethereum) {
      throw new Error('No Ethereum wallet found. Please install MetaMask.');
    }

    try {
      // Request account access
      const accounts = await window.ethereum.request({
        method: 'eth_requestAccounts'
      });

      if (accounts.length > 0) {
        const newProvider = new ethers.providers.Web3Provider(window.ethereum);
        const newSigner = newProvider.getSigner();
        const chainId = await window.ethereum.request({
          method: 'eth_chainId'
        });

        setProvider(newProvider);
        setSigner(newSigner);
        setAccount(accounts[0]);
        setChainId(parseInt(chainId, 16));
        setIsConnected(true);

        // Fetch initial balance
        const balance = await newProvider.getBalance(accounts[0]);
        setBalance(ethers.utils.formatEther(balance));

        return accounts[0];
      }
    } catch (error) {
      console.error('Error connecting wallet:', error);
      throw error;
    }
  };

  const disconnectWallet = () => {
    setProvider(null);
    setSigner(null);
    setAccount(null);
    setChainId(null);
    setIsConnected(false);
    setBalance('0');
    setFamilyInfo(null);
  };

  const getProfileInfo = async () => {
    if (!provider || !account) {
      throw new Error('Wallet not connected');
    }

    try {
      // Implement your profile fetching logic here
      // This is a placeholder implementation - adjust according to your needs
      const profileData = {
        // Add your profile data structure here
      };
      return profileData;
    } catch (error) {
      console.error('Error fetching profile:', error);
      throw error;
    }
  };

  return {
    connectWallet,
    disconnectWallet,
    account,
    familyInfo,
    isConnected: !!account,
    provider,
    getProfileInfo // Add this to the returned object
  };
}
