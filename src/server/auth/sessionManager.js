const redis = require('redis');
const client = redis.createClient({
  host: process.env.REDIS_HOST,
  port: process.env.REDIS_PORT
});

function storeSession(token, userData) {
  return new Promise((resolve, reject) => {
    client.setex(token, 3600, JSON.stringify(userData), (err) => {
      if (err) reject(err);
      else resolve();
    });
  });
}

function getSession(token) {
  return new Promise((resolve, reject) => {
    client.get(token, (err, reply) => {
      if (err) reject(err);
      else resolve(JSON.parse(reply));
    });
  });
}

module.exports = { storeSession, getSession };
