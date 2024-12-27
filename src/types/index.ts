export type Platform = 'web' | 'ios' | 'android';

export type SyntheticPrivKey = 'nip07' | 'none';
export type PrivKey = string | SyntheticPrivKey;

export type RavenState = { ready: boolean, dmsDone: boolean, syncDone: boolean };

export type Keys = {
    pub: string;
    priv: string;
} | {
    pub: string;
    priv: SyntheticPrivKey;
} | null;

export type Metadata = {
    name: string,
    about: string,
    picture: string
}

export type DirectContact = { pub: string, npub: string };

export type Profile = { id: string, creator: string, created: number, nip05: string } & Metadata;

export type Channel = { id: string, creator: string, created: number } & Metadata;

export type ChannelUpdate = { channelId: string } & Channel;

export type EventDeletion = { eventId: string, why: string };

export type PublicMessage = { id: string, root: string, content: string, creator: string, created: number, children?: PublicMessage[], reactions?: Reaction[], mentions: string[], proposalID: string, tags?: [string, string][]; };

export type DirectMessage = { id: string, root?: string, content: string, peer: string, creator: string, created: number, children?: DirectMessage[], reactions?: Reaction[], mentions: string[], decrypted: boolean, proposalID: string, tags?: [string, string][]; };

export type Message = PublicMessage | DirectMessage;

export type ChannelMessageHide = { id: string, reason: string };

export type ChannelUserMute = { pubkey: string, reason: string };

export type RelayDict = Record<string, { read: boolean; write: boolean }>;

export type MuteList = { pubkeys: string[], encrypted: string };

export type Reaction = { id: string, message: string, peer: string, content: string, creator: string, created: number };

export type ReactionCombined = { symbol: string, authors: string[], count: number, userReaction: Reaction | undefined };

export type ReadMarkMap = Record<string, number>;

export type Committee = { id: string, name: string, members: string[] };

// NIP-15 Specific Types
export type Merchant = {
  id: string;
  name: string;
  pubkey: string;
  contact: string;
  stalls: Stall[];
};

export type Marketplace = {
  id: string;
  name: string;
  description: string;
  stalls: Stall[];
};



export interface Stall {
  id: string;
  merchant_id: string;
  name: string;
  description: string;
  currency: string;
  shipping: ShippingZone[];
}

export interface Proposal extends Channel {
  readyForMarket?: boolean;
  productDetails?: {
    price: number;
    quantity: number;
    category: string;
  };
}

export interface Product {
  id: string;
  stall_id: string;
  name: string;
  description: string;
  images: string[];
  currency: string;
  price: number;
  quantity: number;
  specs: [string, string][];
  shipping: any[]; // You might want to define a more specific type for shipping
  proposalId?: string;
}

export interface ShippingZone {
  id: string;
  name: string;
  cost: number;
  regions: string[];
}

export interface ProductShipping {
  id: string;
  cost: number;
}

export interface Order {
  id: string;
  customerId: string;
  items: OrderItem[];
  shippingId: string;
  status: OrderStatus;
  createdAt: number;
}

export interface OrderItem {
  productId: string;
  quantity: number;
}

export type OrderStatus = 'pending' | 'paid' | 'shipped' | 'delivered' | 'cancelled';

export interface PaymentRequest {
  orderId: string;
  amount: number;
  currency: string;
  options: PaymentOption[];
}

export interface PaymentOption {
  type: 'lightning' | 'onchain' | 'lnurl';
  address: string;
}