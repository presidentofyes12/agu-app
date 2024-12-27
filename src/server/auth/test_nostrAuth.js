const { generateChallenge, generateToken, verifyToken, verifyNostrSignature } = require('./nostrAuth');

// Test generateChallenge
console.log('Challenge:', generateChallenge());

// Test generateToken and verifyToken
const publicKey = 'npub1vearlxw5ukxp7260fe556kdrtzav29kzlesarewjyxx3fqmshagq6tqw76';
const token = generateToken(publicKey);
console.log('Token:', token);
console.log('Token valid:', verifyToken(token));

// Note: Testing verifyNostrSignature requires a valid Nostr signature, which we can't generate here
