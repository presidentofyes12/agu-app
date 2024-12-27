import React from 'react';

interface DownloadSeedWordsProps {
  text: string;
  title?: string;
}

const DownloadSeedWords: React.FC<DownloadSeedWordsProps> = ({ text, title = 'Download Seed Words' }) => {
  const handleDownload = () => {
    if (!text || text.trim() === '') {
      console.error('Seed words are empty or not available');
      alert('Seed words are not available for download. Please try creating the account again.');
      return;
    }

    try {
      const element = document.createElement('a');
      const file = new Blob([text], { type: 'text/plain' });
      element.href = URL.createObjectURL(file);
      element.download = 'nostrSeedWords.txt';
      document.body.appendChild(element);
      element.click();
      document.body.removeChild(element);
      window.localStorage.setItem("downloaded", "true");
    } catch (error) {
      console.error('Error downloading seed words:', error);
      alert('An error occurred while downloading the seed words. Please try again.');
    }
  };

  return (
    <button className='btn btn_success' onClick={handleDownload}>
      {title}
    </button>
  );
};

export default DownloadSeedWords;