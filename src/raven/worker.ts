import * as Comlink from 'comlink';
import { Event, Filter, SimplePool, Sub } from 'nostr-tools';

const permanentProposals = [
  {
    name: 'Mostr',
    about: '{"problem":"Lack of connection between Fediverse and Nostr","solution":"","targetAudience":"","qualifications":"","purpose":"A platform feature enabling dynamic and flexible presentation of content.","approach":"A platform feature enabling dynamic and flexible presentation of content.","outcome":"A platform feature enabling dynamic and flexible presentation of content.","timeline":"","budget":"","callToAction":"","voting":[],"proposalID":""}',
    picture: '',
  },
  {
    name: 'Ephemeral Relays',
    about: '{"problem":"Need for temporary communication channels","solution":"","targetAudience":"","qualifications":"","purpose":"Temporary communication channels that expire after a set duration.","approach":"Temporary communication channels that expire after a set duration.","outcome":"Temporary communication channels that expire after a set duration.","timeline":"","budget":"","callToAction":"","voting":[],"proposalID":""}',
    picture: '',
  },
  {
    name: 'Public and private AI profiles for version control',
    about: '{"problem":"Lack of version control for AI profiles","solution":"","targetAudience":"","qualifications":"","purpose":"Profiles that manage and track changes in AI models and datasets.","approach":"Profiles that manage and track changes in AI models and datasets.","outcome":"Profiles that manage and track changes in AI models and datasets.","timeline":"","budget":"","callToAction":"","voting":[],"proposalID":""}',
    picture: '',
  },
  {
    name: 'Marketplace',
    about: '{"problem":"Need for a decentralized marketplace","solution":"","targetAudience":"","qualifications":"","purpose":"A decentralized marketplace for trading goods and services.","approach":"A decentralized marketplace for trading goods and services.","outcome":"A decentralized marketplace for trading goods and services.","timeline":"","budget":"","callToAction":"","voting":[],"proposalID":""}',
    picture: '',
  },
  {
    name: 'Smart contract',
    about: '{"problem":"Need for automated and self-executing contracts","solution":"","targetAudience":"","qualifications":"","purpose":"Automated and self-executing contracts with predefined rules.","approach":"Automated and self-executing contracts with predefined rules.","outcome":"Automated and self-executing contracts with predefined rules.","timeline":"","budget":"","callToAction":"","voting":[],"proposalID":""}',
    picture: '',
  },
  {
    name: 'NewLaw/Everyone is right/Force for peace',
    about: '{"problem":"Need for a fair governance system","solution":"","targetAudience":"","qualifications":"","purpose":"A governance system promoting universal fairness and conflict resolution.","approach":"A governance system promoting universal fairness and conflict resolution.","outcome":"A governance system promoting universal fairness and conflict resolution.","timeline":"","budget":"","callToAction":"","voting":[],"proposalID":""}',
    picture: '',
  },
  {
    name: 'Withdrawal Rights/Disclaimer/ Privacy standards',
    about: '{"problem":"Need for user rights and privacy policies","solution":"","targetAudience":"","qualifications":"","purpose":"User rights and privacy policies ensuring data protection and transparency.","approach":"User rights and privacy policies ensuring data protection and transparency.","outcome":"User rights and privacy policies ensuring data protection and transparency.","timeline":"","budget":"","callToAction":"","voting":[],"proposalID":""}',
    picture: '',
  },
  {
    name: 'Embedded application',
    about: '{"problem":"Need for seamless application integration","solution":"","targetAudience":"","qualifications":"","purpose":"Integration of applications directly within the platform for seamless user experience.","approach":"Integration of applications directly within the platform for seamless user experience.","outcome":"Integration of applications directly within the platform for seamless user experience.","timeline":"","budget":"","callToAction":"","voting":[],"proposalID":""}',
    picture: '',
  },
  {
    name: 'Multi ID system',
    about: '{"problem":"Need for secure management of multiple identities","solution":"","targetAudience":"","qualifications":"","purpose":"A system allowing users to manage multiple identities securely.","approach":"A system allowing users to manage multiple identities securely.","outcome":"A system allowing users to manage multiple identities securely.","timeline":"","budget":"","callToAction":"","voting":[],"proposalID":""}',
    picture: '',
  },
  {
    name: "If you don't rate, you can't be rated.",
    about: '{"problem":"Lack of user participation in ratings","solution":"","targetAudience":"","qualifications":"","purpose":"A feedback system encouraging user participation in ratings.","approach":"A feedback system encouraging user participation in ratings.","outcome":"A feedback system encouraging user participation in ratings.","timeline":"","budget":"","callToAction":"","voting":[],"proposalID":""}',
    picture: '',
  },
  {
    name: 'Privacy, scalability, security, transparency, decentralization, and identification.',
    about: '{"problem":"Need for core platform principles","solution":"","targetAudience":"","qualifications":"","purpose":"Core principles guiding platform development and operations.","approach":"Core principles guiding platform development and operations.","outcome":"Core principles guiding platform development and operations.","timeline":"","budget":"","callToAction":"","voting":[],"proposalID":""}',
    picture: '',
  },
  {
    name: 'Autotranslate',
    about: '{"problem":"Need for multilingual support","solution":"","targetAudience":"","qualifications":"","purpose":"Automatic translation feature for multilingual support.","approach":"Automatic translation feature for multilingual support.","outcome":"Automatic translation feature for multilingual support.","timeline":"","budget":"","callToAction":"","voting":[],"proposalID":""}',
    picture: '',
  },
];

export class BgRaven {
  private seenOn: Record<string, string[]> = {};
  private subs: Record<string, Sub> = {};
  private relays: string[] = [];
  private pool = new SimplePool();
  private poolCreated = Date.now();

  public setup(relays: string[]) {
    this.relays = relays;
  }

  private getPool = (): SimplePool => {
    if (Date.now() - this.poolCreated > 120000) {
      // renew pool every two minutes
      this.pool.close(this.relays);

      this.pool = new SimplePool();
      this.poolCreated = Date.now();
    }

    return this.pool;
  };

  public fetch(filters: Filter[], quitMs: number = 0): Promise<Event[]> {
    return new Promise(resolve => {
      const pool = this.getPool();
      const sub = pool.sub(this.relays, filters);
      const events: Event[] = [];

      const quit = () => {
        sub.unsub();
        resolve(events);
      };

      let timer: any = quitMs > 0 ? setTimeout(quit, quitMs) : null;

      sub.on('event', (event: Event) => {
        const proposalName = JSON.parse(event.content).name;
        const isPermanentProposal = permanentProposals.some(
          proposal => proposal.name === proposalName
        );

        if (isPermanentProposal) {
          const duplicateProposals = events.filter(
            e => JSON.parse(e.content).name === proposalName
          );

          if (duplicateProposals.length === 0) {
            events.push(event);
            this.seenOn[event.id] = pool.seenOn(event.id);
          } else {
            // Delete excess proposals
            duplicateProposals.forEach(duplicateProposal => {
              const index = events.indexOf(duplicateProposal);
              if (index !== -1) {
                events.splice(index, 1);
                delete this.seenOn[duplicateProposal.id];
              }
            });
          }
        } else {
          events.push(event);
          this.seenOn[event.id] = pool.seenOn(event.id);
        }

        if (quitMs > 0) {
          clearTimeout(timer);
          timer = setTimeout(quit, quitMs);
        }
      });

      if (quitMs === 0) {
        sub.on('eose', () => {
          sub.unsub();
          resolve(events);
        });
      }
    });
  }

  public sub(
    filters: Filter[],
    onEvent: (e: Event) => void,
    unsub: boolean = true
  ) {
    const subId = Math.random().toString().slice(2);
    const pool = this.getPool();
    const sub = pool.sub(this.relays, filters, { id: subId });

    sub.on('event', event => {
      this.seenOn[event.id] = pool.seenOn(event.id);
      onEvent(event);
    });

    sub.on('eose', () => {
      if (unsub) {
        this.unsub(subId);
      }
    });

    this.subs[subId] = sub;
    return subId;
  }

  public unsub(subId: string) {
    if (this.subs[subId]) {
      this.subs[subId].unsub();
      delete this.subs[subId];
    }
  }

  public async where(eventId: string) {
    let try_ = 0;
    while (!this.seenOn[eventId]) {
      await this.fetch([{ ids: [eventId] }]);
      try_++;
      if (try_ === 3) {
        break;
      }
    }

    if (!this.seenOn[eventId]) {
      throw new Error('Could not find root event');
    }

    return this.findHealthyRelay(this.seenOn[eventId]);
  }

  private handleStallEvent(event: Event): void {
    // TODO: Implement stall event handling
  }

  private handleProductEvent(event: Event): void {
    // TODO: Implement product event handling
  }

  private handleOrderEvent(event: Event): void {
    // TODO: Implement order event handling
  }

  private handlePaymentRequestEvent(event: Event): void {
    // TODO: Implement payment request event handling
  }

  private handleOrderStatusUpdateEvent(event: Event): void {
    // TODO: Implement order status update event handling
  }

  private async findHealthyRelay(relays: string[]) {
    const pool = this.getPool();
    for (const relay of relays) {
      try {
        await pool.ensureRelay(relay);
        return relay;
      } catch (e) {}
    }

    throw new Error("Couldn't find a working relay");
  }
}

Comlink.expose(new BgRaven());