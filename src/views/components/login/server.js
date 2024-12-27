const express = require('express');
const { exec } = require('child_process');
const cors = require('cors');
const fs = require('fs').promises;
const path = require('path');
const os = require('os');

const app = express();
app.use(cors());
app.use(express.json());

const TEMP_DIR = path.join(os.tmpdir(), 'nostr_relay_build');
const RELAY_DIR = path.join(__dirname, 'nostr-rs-relay');

app.post('/api/setup-relay', async (req, res) => {
  const { port, nostrKey } = req.body;

  if (!port || !nostrKey) {
    return res.status(400).json({ success: false, error: 'Port and Nostr private key are required' });
  }

  try {
    const setupResult = await setupRelay(port);
    await setupNoscl(nostrKey, port);
    res.json({ success: true, message: 'Nostr relay setup completed successfully', setupDetails: setupResult });
  } catch (error) {
    console.error('Setup failed:', error);
    res.status(500).json({ success: false, error: error.message, setupDetails: error.setupDetails });
  }
});

async function setupRelay(port) {
  console.log('Setting up nostr-rs-relay...');

  try {
    // Create a temporary directory with a short path
    await fs.mkdir(TEMP_DIR, { recursive: true });
    console.log(`Created temporary directory: ${TEMP_DIR}`);

    // Copy the relay files to the temporary directory
    await copyDir(RELAY_DIR, TEMP_DIR);
    console.log(`Copied relay files to: ${TEMP_DIR}`);

    const commands = [
      'cargo build --release',
      `cargo run --release --bin nostr-rs-relay -- --port ${port} --db-dir data`
    ];

    for (const command of commands) {
      await executeCommand(command, TEMP_DIR);
    }

    // Copy the built binary back to the original directory
    const binaryPath = path.join(TEMP_DIR, 'target', 'release', 'nostr-rs-relay');
    const destPath = path.join(RELAY_DIR, 'nostr-rs-relay');
    await fs.copyFile(binaryPath, destPath);
    console.log(`Copied binary from ${binaryPath} to ${destPath}`);

    return { buildDir: TEMP_DIR, binaryPath: destPath };
  } catch (error) {
    console.error('Error in setupRelay:', error);
    throw error;
  }
}

async function copyDir(src, dest) {
  try {
    await fs.mkdir(dest, { recursive: true });
    let entries = await fs.readdir(src, { withFileTypes: true });

    for (let entry of entries) {
      let srcPath = path.join(src, entry.name);
      let destPath = path.join(dest, entry.name);

      if (entry.isDirectory()) {
        if (entry.name !== '.git') {
          await copyDir(srcPath, destPath);
        } else {
          console.log(`Skipping .git directory: ${srcPath}`);
        }
      } else {
        try {
          await fs.copyFile(srcPath, destPath);
          console.log(`Copied file: ${srcPath} -> ${destPath}`);
        } catch (error) {
          console.error(`Error copying file ${srcPath}:`, error);
        }
      }
    }
  } catch (error) {
    console.error(`Error copying directory from ${src} to ${dest}:`, error);
    throw error;
  }
}

function setupNoscl(nostrKey, port) {
  const commands = [
    `noscl setprivate ${nostrKey}`,
    `noscl relay add ws://localhost:${port}`
  ];

  return Promise.all(commands.map(cmd => executeCommand(cmd)));
}

function executeCommand(command, cwd = null) {
  return new Promise((resolve, reject) => {
    exec(command, { cwd }, (error, stdout, stderr) => {
      console.log(`Executing command: ${command}`);
      console.log(`stdout: ${stdout}`);
      console.log(`stderr: ${stderr}`);
      if (error) {
        console.error(`Error executing command: ${command}`);
        reject(error);
      } else {
        resolve(stdout);
      }
    });
  });
}

const PORT = process.env.PORT || 5000;
app.listen(PORT, () => console.log(`Server running on port ${PORT}`));
