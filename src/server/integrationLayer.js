const axios = require('axios');

async function setupRelayForAdmin(publicKey) {
  try {
    const response = await axios.post('http://localhost:8069/setup_relay', { publicKey });
    return response.data;
  } catch (error) {
    console.error('Error setting up relay:', error);
    throw error;
  }
}

module.exports = { setupRelayForAdmin };
