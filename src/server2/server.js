const express = require('express');
const cors = require('cors');
const { exec } = require('child_process');
const fs = require('fs');
const path = require('path');
const axios = require('axios');
const unzipper = require('unzipper');
const WebSocket = require('ws');

const app = express();

// Enable CORS for all routes
app.use(cors());
app.use(express.json());

// ... rest of your server.js code ...

const REPO_URL = 'https://github.com/scsibug/nostr-rs-relay/archive/refs/heads/master.zip';
const RELAY_DIR = path.join(__dirname, 'nostr-rs-relay-master');

app.post('/api/setup-relay', async (req, res) => {
  const { port, nostrKey } = req.body;
  console.log('Received setup-relay request:', { port, nostrKey });

  if (!port || !nostrKey) {
    return res.status(400).json({ success: false, error: 'Port and Nostr private key are required' });
  }

  try {
    console.log('Starting relay setup process...');
    await downloadAndExtractRelay();
    console.log('Download and extraction complete');

await cleanupExistingRelay();
await buildAndSetupRelay(port);
console.log('Relay built and set up');

await checkRelayStatus(port);
console.log('Relay operational');

await setupNoscl(nostrKey, port);
    console.log('Noscl setup complete');

    res.json({ success: true, message: 'Nostr relay setup and test message published successfully' });
  } catch (error) {
    console.error('Setup failed:', error);
    let errorMessage = 'An unexpected error occurred';
    if (error.message.includes('buildAndSetupRelay')) {
      errorMessage = 'Failed to build or start the relay container';
    } else if (error.message.includes('checkRelayStatus')) {
      errorMessage = 'Relay started but is not responding correctly';
    } else if (error.message.includes('setupNoscl')) {
      errorMessage = 'Relay is running but failed to set up noscl';
    }
    res.status(500).json({ success: false, error: errorMessage });
  }
});

async function downloadAndExtractRelay() {
  console.log('Downloading nostr-rs-relay...');
  const response = await axios({
    method: 'get',
    url: REPO_URL,
    responseType: 'stream'
  });

  await new Promise((resolve, reject) => {
    response.data.pipe(unzipper.Extract({ path: __dirname }))
      .on('close', () => {
        console.log('nostr-rs-relay downloaded and extracted');
        resolve();
      })
      .on('error', reject);
  });

  console.log('nostr-rs-relay downloaded and extracted');

}


function buildAndSetupRelay(port) {
  return new Promise((resolve, reject) => {
    const commands = [
      'sudo podman build --pull -t nostr-rs-relay .',
      `sudo podman run -d -p ${port}:8080 --user=100:100 -v "${RELAY_DIR}/data:/usr/src/app/db:Z" -v "${RELAY_DIR}/config.toml:/usr/src/app/config.toml:ro,Z" --name nostr-relay nostr-rs-relay:latest`
    ];

    const executeCommands = (index) => {
      if (index >= commands.length) {
        resolve();
        return;
      }

      console.log(`Executing command: ${commands[index]}`);
      exec(commands[index], { cwd: RELAY_DIR }, (error, stdout, stderr) => {
        if (error) {
          console.error(`Error executing command: ${commands[index]}`);
          console.error(stderr);
          reject(error);
          return;
        }
        console.log(`Command output: ${stdout}`);
        executeCommands(index + 1);
      });
    };

    executeCommands(0);
  });
}

function setupNoscl(nostrKey, port) {
  return new Promise((resolve, reject) => {
    const commands = [
      `./noscl-master/noscl setprivate ${nostrKey}`,
      `./noscl-master/noscl relay add ws://172.17.0.1:${port}`,
      `./noscl-master/noscl relay`,
      `ping google.com -c 5`,  // Add a delay to allow the relay to start up
      `./noscl-master/noscl publish "Wow"`
    ];

    const executeCommands = (index) => {
      if (index >= commands.length) {
        resolve();
        return;
      }

      exec(commands[index], (error, stdout, stderr) => {
        if (error) {
          console.error(`Error executing command: ${commands[index]}`);
          console.error(stderr);
          // Don't reject here, continue with the next command
        }
        console.log(stdout);
        executeCommands(index + 1);
      });
    };

    executeCommands(0);
  });
}

function cleanupExistingRelay() {
  return new Promise((resolve, reject) => {
    exec('podman stop nostr-relay && podman rm nostr-relay', (error, stdout, stderr) => {
      if (error) {
        console.log('No existing relay to clean up');
      } else {
        console.log('Existing relay cleaned up');
      }
      resolve();
    });
  });
}

function checkRelayStatus(port) {
  return new Promise((resolve, reject) => {
    const maxAttempts = 10;
    let attempts = 0;

    const check = () => {
      const ws = new WebSocket(`ws://172.17.0.1:${port}`);

      ws.on('open', () => {
        console.log('WebSocket connection established');
        ws.close();
        resolve();
      });

      ws.on('error', (error) => {
        console.log(`WebSocket connection failed (attempt ${attempts + 1}/${maxAttempts}):`, error.message);
        if (++attempts < maxAttempts) {
          setTimeout(check, 2000);
        } else {
          reject(new Error('Relay failed to start after multiple attempts'));
        }
      });

      // Add a timeout in case the connection hangs
      setTimeout(() => {
        ws.close();
        if (++attempts < maxAttempts) {
          setTimeout(check, 2000);
        } else {
          reject(new Error('Relay connection timed out after multiple attempts'));
        }
      }, 5000);
    };

    check();
  });
}

const EXPRESS_PORT = process.env.EXPRESS_PORT || 5000;
app.listen(EXPRESS_PORT, () => console.log(`Express server running on port ${EXPRESS_PORT}`));
