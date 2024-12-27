import Raven from 'raven/raven';
import {Event} from 'nostr-tools';
import {RelayDict} from 'types';

declare global {
    interface Window {
        raven?: Raven;
        // Existing Nostr declarations
        nostr?: {
            getPublicKey: () => Promise<string>;
            signEvent: (event: Event) => Promise<Event>;
            getRelays: () => Promise<RelayDict>;
            nip04: {
                encrypt: (pubkey: string, content: string) => Promise<string>;
                decrypt: (pubkey: string, content: string) => Promise<string>;
            };
        };
        requestPrivateKey: (data?: any) => Promise<string>;
        // Add Ethereum provider interface
        ethereum?: {
            request: (args: { method: string; params?: any[] }) => Promise<any>;
            on: (event: string, callback: (...args: any[]) => void) => void;
            removeAllListeners: () => void;
            isMetaMask?: boolean;
            selectedAddress?: string;
            chainId?: string;
            networkVersion?: string;
            // Add common provider methods
            enable: () => Promise<string[]>;
            sendAsync: (request: any) => Promise<any>;
            send: (request: any) => Promise<any>;
        };
    }
}
