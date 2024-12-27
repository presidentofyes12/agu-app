export interface Stall {
  id: string;
  name: string;
  description: string;
}

export interface Product {
  id: string;
  stall_id: string;
  name: string;
  description: string;
  price: number;
  currency: string;
}
