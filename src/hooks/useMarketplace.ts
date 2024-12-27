import { useEffect, useState } from 'react';
import { useAtom } from 'jotai';
import { Product, Proposal, Stall } from 'types';
import { stallsAtom, productsAtom, channelsAtom, ravenAtom } from 'atoms';

export function useMarketplace() {
  const [stalls, setStalls] = useAtom(stallsAtom);
  const [products, setProducts] = useAtom(productsAtom);
  const [channels] = useAtom(channelsAtom);
  const [proposals, setProposals] = useState<Proposal[]>([]);
  const [raven] = useAtom(ravenAtom);

  useEffect(() => {
    const fetchData = async () => {
      if (raven) {
        // Fetch stalls
        const fetchedStalls = await raven.fetchStalls();
        setStalls(fetchedStalls);

        // Fetch products
        const fetchedProducts = await raven.fetchProducts();
        setProducts(fetchedProducts);

        // Set proposals
        const fetchedProposals = channels.filter(channel => 'readyForMarket' in channel) as Proposal[];
        setProposals(fetchedProposals);
      }
    };

    fetchData();
  }, [raven, channels]);

  useEffect(() => {
    console.log('useMarketplace - Stalls:', stalls);
    console.log('useMarketplace - Products:', products);
    console.log('useMarketplace - Proposals:', proposals);
  }, [stalls, products, proposals]);

  return {
    stalls,
    products,
    proposals,
  };
}

export default useMarketplace;