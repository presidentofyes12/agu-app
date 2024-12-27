/*import { Event, Filter } from 'nostr-tools';
import { SimplePool } from 'nostr-tools';
import { getRelays } from 'local-storage';
import { Stall, Product } from './types';
import { RelayDict } from 'types';

let relays: RelayDict;
getRelays().then(r => {
  relays = r;
});

export async function fetchStalls(): Promise<Stall[]> {
  const filters: Filter[] = [{ kinds: [30017] }];
  const events = await fetchEvents(filters);
  return events.map(event => JSON.parse(event.content));
}

export async function fetchProducts(): Promise<Product[]> {
  const filters: Filter[] = [{ kinds: [30018] }];
  const events = await fetchEvents(filters);
  return events.map(event => JSON.parse(event.content));
}

async function fetchEvents(filters: Filter[], timeout: number = 0): Promise<Event[]> {
  const pool = new SimplePool();
  const events = await pool.list(relays, filters, timeout);
  return events;
}*/