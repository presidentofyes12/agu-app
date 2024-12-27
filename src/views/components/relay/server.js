const express = require('express');
const { exec, execSync } = require('child_process');
const cors = require('cors');
const fs = require('fs');
const path = require('path');
const axios = require('axios');
const unzipper = require('unzipper');
const net = require('net');

const app = express();
app.use(cors());
app.use(express.json());

const REPO_URL = 'https://github.com/scsibug/nostr-rs-relay/archive/refs/heads/master.zip';
const RELAY_DIR = path.join(__dirname, 'nostr-rs-relay');

function findAvailablePort(startPort = 9000) {
  return new Promise((resolve, reject) => {
    const server = net.createServer();
    server.listen(startPort, () => {
      const { port } = server.address();
      server.close(() => {
        resolve(port);
      });
    });
    server.on('error', (err) => {
      if (err.code === 'EADDRINUSE') {
        findAvailablePort(startPort + 1).then(resolve, reject);
      } else {
        reject(err);
      }
    });
  });
}

function ensureNosclInstalled() {
  return new Promise((resolve, reject) => {
    console.log('PATH before:', process.env.PATH);
    exec('which noscl', (error, stdout, stderr) => {
      if (error) {
        console.log('noscl not found. Attempting to install...');
        try {
          execSync('go install github.com/fiatjaf/noscl@latest');
          const goPath = execSync('go env GOPATH', { encoding: 'utf8' }).trim();
          const newPath = `${process.env.PATH}:${goPath}/bin`;
          process.env.PATH = newPath;
          console.log('noscl installed successfully.');
          console.log('PATH after:', process.env.PATH);
          resolve();
        } catch (installError) {
          console.error('Failed to install noscl:', installError);
          reject(installError);
        }
      } else {
        console.log('noscl is already installed.');
        resolve();
      }
    });
  });
}

app.post('/api/setup-relay', async (req, res) => {
  const { nostrKey } = req.body;

  if (!nostrKey) {
    return res.status(400).json({ success: false, error: 'Nostr private key is required' });
  }

  try {
    const port = await findAvailablePort(8080);
    
    await clear(port);
    
    // Step 1: Download and extract nostr-rs-relay
    await downloadAndExtractRelay();

    // Step 2: Build and set up the relay
    await buildAndSetupRelay(port);

    // Step 3: Set up noscl
    let noslSetupSuccess = false;
    try {
      await setupNoscl(nostrKey, port);
      noslSetupSuccess = true;
    } catch (noslError) {
      console.warn('Failed to set up noscl, but continuing with relay setup:', noslError);
    }

    // Check if config.toml exists
    if (!fs.existsSync(path.join(RELAY_DIR, 'config.toml'))) {
      throw new Error('config.toml not found in the relay directory');
    }

    res.json({ 
      success: true, 
      message: 'Nostr relay setup completed successfully', 
      port,
      noslSetupSuccess,
      noslInstallInstructions: noslSetupSuccess ? null : 'To use noscl, please install Go and run: go install github.com/fiatjaf/noscl@latest'
    });
  } catch (error) {
    console.error('Setup failed:', error);
    res.status(500).json({ success: false, error: error.toString() });
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
        fs.renameSync(path.join(__dirname, 'nostr-rs-relay-master'), RELAY_DIR);
        resolve();
      })
      .on('error', reject);
  });

  console.log('nostr-rs-relay downloaded and extracted');
}

function buildAndSetupRelay(port) {
  return new Promise((resolve, reject) => {
    const commands = [
      'sudo podman stop nostr-relay || true',
      'sudo podman rm nostr-relay || true',
      'sudo podman system prune --all --force',
      'sudo podman build --pull -t localhost/nostr-rs-relay:v1 .',
      'mkdir -p data',
      'sudo chown 100:100 data',
      `sudo podman run -d -p ${port}:8080 --user=100:100 -v "$(pwd)/data:/usr/src/app/db:Z" -v "$(pwd)/config.toml:/usr/src/app/config.toml:ro,Z" --name nostr-relay localhost/nostr-rs-relay:v1`
    ];

    const executeCommands = (index) => {
      if (index >= commands.length) {
        resolve();
        return;
      }
    
      if (!fs.existsSync(path.join(RELAY_DIR, 'config.toml'))) {
        console.error('config.toml not found');
        return reject('config.toml not found');
      }

      console.log(`Executing command: ${commands[index]}`);
      exec(commands[index], { cwd: RELAY_DIR, shell: '/bin/bash' }, (error, stdout, stderr) => {
        if (error) {
          console.error(`Error executing command: ${commands[index]}`);
          console.error(`stderr: ${stderr}`);
          reject(`Error: ${error.message}`);
          return;
        }
        console.log(`stdout: ${stdout}`);
        executeCommands(index + 1);
      });
    };

    executeCommands(0);
  });
}

async function setupNoscl(nostrKey, port) {
  try {
    await ensureNosclInstalled();

    const commands = [
      `noscl setprivate ${nostrKey}`,
      `noscl relay add ws://localhost:${port}`
    ];

    for (const command of commands) {
      console.log(`Executing command: ${command}`);
      execSync(command, { stdio: 'inherit' });
    }
  } catch (error) {
    console.error('Error in setupNoscl:', error);
    throw error;
  }
}

function clear(port) {
  return new Promise((resolve, reject) => {
    const commands = [
      `sudo rm -rf nostr-rs-relay`,
      `mkdir nostr-rs-relay`
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
          reject(error);
          return;
        }
        console.log(stdout);
        executeCommands(index + 1);
      });
    };

    executeCommands(0);
  });
}

const SERVER_PORT = process.env.PORT || 5000;
app.listen(SERVER_PORT, () => console.log(`Server running on port ${SERVER_PORT}`));
