const { generatePrivateKey, getPublicKey, signEvent, verifySignature } = require('nostr-tools');
const crypto = require('crypto');

function generateChallenge() {
  return crypto.randomBytes(32).toString('hex');
}

function generateToken(publicKey) {
  const timestamp = Date.now();
  const data = `${publicKey}:${timestamp}`;
  const hash = crypto.createHash('sha256').update(data).digest('hex');
  return `${publicKey}:${timestamp}:${hash}`;
}

function verifyToken(token) {
  const [publicKey, timestamp, hash] = token.split(':');
  const data = `${publicKey}:${timestamp}`;
  const computedHash = crypto.createHash('sha256').update(data).digest('hex');
  return computedHash === hash && (Date.now() - parseInt(timestamp)) < 3600000;
}

async function verifyNostrSignature(publicKey, signature, challenge) {
  const event = {
    pubkey: publicKey,
    created_at: Math.floor(Date.now() / 1000),
    kind: 22242,
    tags: [],
    content: challenge
  };
  return verifySignature(event, signature, publicKey);
}

module.exports = { generateChallenge, generateToken, verifyToken, verifyNostrSignature };
