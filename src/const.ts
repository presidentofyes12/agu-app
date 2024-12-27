import {Capacitor} from '@capacitor/core';
import {PaletteMode} from '@mui/material';
import {Channel, Platform, RelayDict} from 'types';

export const DEFAULT_RELAYS: RelayDict = {
    'wss://relay1.nostrchat.io': {read: true, write: true},
    'wss://relay2.nostrchat.io': {read: true, write: true},
    'wss://relay.damus.io': {read: true, write: true},
    'wss://relay.snort.social': {read: true, write: false},
    'wss://nos.lol': {read: true, write: true},
    'http://192.168.1.205:5000/': {read: true, write: false},
};

export const MESSAGE_PER_PAGE = 30;
export const ACCEPTABLE_LESS_PAGE_MESSAGES = 5;
export const SCROLL_DETECT_THRESHOLD = 5;

export const GLOBAL_CHAT: Channel = {
    id: 'f412192fdc846952c75058e911d37a7392aa7fd2e727330f4344badc92fb8a22',
    name: 'Home Page', 
    about: 'Whatever you want it to be, just be nice',
    picture: '',
    creator: 'aea59833635dd0868bc7cf923926e51df936405d8e6a753b78038981c75c4a74',
    created: 1678198928
};

export const PLATFORM = Capacitor.getPlatform() as Platform;

export const DEFAULT_THEME: PaletteMode = 'dark';

// Marketplace event kinds
export const MARKETPLACE_EVENT_KINDS = {
  STALL_CREATE: 30017,
  PRODUCT_CREATE: 30018,
  ORDER_CREATE: 30019,
  PAYMENT_REQUEST: 30020,
  ORDER_STATUS_UPDATE: 30021,
};

// Marketplace-related constants
export const MARKETPLACE_CONSTANTS = {
  MAX_PRODUCTS_PER_STALL: 100,
  MAX_IMAGES_PER_PRODUCT: 5,
  MAX_SPECS_PER_PRODUCT: 10,
};