import React, { useEffect } from 'react';
import { useAtom } from 'jotai';
import { ethers } from 'ethers';
import { providerAtom, accountAtom, chainIdAtom, isConnectedAtom } from '../state/web3State';
import { WEB3_CONFIG } from '../hooks/web3Config';

export const Web3Provider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [, setProvider] = useAtom(providerAtom);
  const [, setAccount] = useAtom(accountAtom);
  const [, setChainId] = useAtom(chainIdAtom);
  const [, setIsConnected] = useAtom(isConnectedAtom);

  useEffect(() => {
    const initProvider = async () => {
      if (typeof window.ethereum !== 'undefined') {
        const provider = new ethers.providers.Web3Provider(window.ethereum);
        setProvider(provider);

        try {
          const accounts = await provider.listAccounts();
          if (accounts.length > 0) {
            setAccount(accounts[0]);
            setIsConnected(true);
          }

          const network = await provider.getNetwork();
          setChainId(network.chainId);
        } catch (error) {
          console.error('Error initializing Web3:', error);
        }
      }
    };

    initProvider();

    if (window.ethereum) {
      window.ethereum.on('accountsChanged', (accounts: string[]) => {
        if (accounts.length > 0) {
          setAccount(accounts[0]);
          setIsConnected(true);
        } else {
          setAccount(null);
          setIsConnected(false);
        }
      });

      window.ethereum.on('chainChanged', (chainId: string) => {
        setChainId(parseInt(chainId));
      });
    }

    return () => {
      if (window.ethereum) {
        window.ethereum.removeAllListeners();
      }
    };
  }, []);

  return <>{children}</>;
};
