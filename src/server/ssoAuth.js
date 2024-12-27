const { getPublicKey } = require('nostr-tools');

function verifySSOCredentials(username, password) {
  try {
    const derivedPublicKey = getPublicKey(password);
    return derivedPublicKey === username;
  } catch (error) {
    console.error('Invalid Nostr credentials:', error);
    return false;
  }
}

module.exports = { verifySSOCredentials };
