const express = require('express');
const ftp = require('basic-ftp');
const cors = require('cors');
const { Readable, Writable } = require('stream');

const app = express();
app.use(cors());
app.use(express.json());

async function createFtpClient() {
  const ftpClient = new ftp.Client();
  ftpClient.ftp.verbose = true;
  try {
    await ftpClient.access({
      host: "127.0.0.1",
      user: "New User",
      password: "0810", // Replace with the actual password
      secure: false
    });
    console.log("Connected to FTP server");
    return ftpClient;
  } catch (err) {
    console.error("FTP connection error:", err);
    throw err;
  }
}

app.post('/upload', async (req, res) => {
  let ftpClient;
  try {
    ftpClient = await createFtpClient();
    const { content, fileId } = req.body;
    console.log(`Attempting to upload file: ${fileId}`);
    
    // List current directory contents
    const list = await ftpClient.list();
    console.log("Current directory contents:", list);

    // Ensure the FTPomg directory exists
    try {
      await ftpClient.ensureDir("/FTPomg");
    } catch (mkdirErr) {
      console.error("Error creating directory:", mkdirErr);
    }

    // Create a readable stream from the content
    const stream = new Readable();
    stream.push(content);
    stream.push(null);

    // Upload the file
    await ftpClient.uploadFrom(stream, `/FTPomg/${fileId}`);
    console.log(`File ${fileId} uploaded successfully`);
    res.json({ success: true, message: 'File uploaded successfully' });
  } catch (error) {
    console.error("Error uploading file:", error);
    res.status(500).json({ success: false, error: error.message });
  } finally {
    if (ftpClient) {
      ftpClient.close();
    }
  }
});

app.get('/download/:fileId', async (req, res) => {
  let ftpClient;
  try {
    ftpClient = await createFtpClient();
    const { fileId } = req.params;
    console.log(`Attempting to download file: ${fileId}`);

    // List current directory contents
    const list = await ftpClient.list('/FTPomg');
    console.log("FTPomg directory contents:", list);

    // Check if the file exists
    const fileInfo = list.find(file => file.name === fileId);
    if (!fileInfo) {
      throw new Error(`File ${fileId} not found in /FTPomg directory`);
    }

    // Create a writable stream to store the file content
    let content = '';
    const writeStream = new Writable({
      write(chunk, encoding, callback) {
        content += chunk.toString();
        callback();
      }
    });

    // Download the file
    await ftpClient.downloadTo(writeStream, `/FTPomg/${fileId}`);
    console.log(`File ${fileId} downloaded successfully`);

    // Send file metadata along with content
    res.json({
      success: true,
      fileInfo: {
        id: fileId,
        name: fileInfo.name,
        size: fileInfo.size,
        modifiedAt: fileInfo.modifiedAt,
      },
      content
    });
  } catch (error) {
    console.error("Error downloading file:", error);
    res.status(500).json({ success: false, error: error.message, stack: error.stack });
  } finally {
    if (ftpClient) {
      await ftpClient.close();
    }
  }
});

app.delete('/delete/:fileId', async (req, res) => {
  let ftpClient;
  try {
    ftpClient = await createFtpClient();
    const { fileId } = req.params;
    console.log(`Attempting to delete file: ${fileId}`);
    await ftpClient.remove(`/FTPomg/${fileId}`);
    console.log(`File ${fileId} deleted successfully`);
    res.json({ success: true, message: 'File deleted successfully' });
  } catch (error) {
    console.error("Error deleting file:", error);
    res.status(500).json({ success: false, error: error.message });
  } finally {
    if (ftpClient) {
      ftpClient.close();
    }
  }
});

const PORT = 3001;
app.listen(PORT, () => console.log(`Server running on port ${PORT}`));
