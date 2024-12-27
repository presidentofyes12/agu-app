import moment from 'moment';
import axios from 'axios';
import Web3 from 'web3';
import { toast } from 'react-toastify';
import {
  RPC_URL,
  UPLOAD_API_KEY,
  contractABI,
  contractAddress,
} from './constant';

const web3 = new Web3(RPC_URL);

export const fileUpload = (event, setFile, setLoading) => {
  const formData = new FormData();
  formData.append('image', event.target.files[0]);
  setLoading(true);

  axios
    .post(`https://api.imgbb.com/1/upload?key=${UPLOAD_API_KEY}`, formData)
    .then(response => {
      if (response.data) {
        setFile(response.data.data.url);
      }
    })
    .catch(error => {
      toast.error('Error on Processing Image .');
      console.error('Upload failed:', error);
    })
    .finally(() => {
      setLoading(false);
    });
};

export const formatTime = timestamp => {
  const currentTime = moment();
  const postTime = moment.unix(timestamp);

  const diffMinutes = currentTime.diff(postTime, 'minutes');
  const diffHours = currentTime.diff(postTime, 'hours');
  const diffDays = currentTime.diff(postTime, 'days');
  const diffWeeks = currentTime.diff(postTime, 'weeks');
  const diffMonths = currentTime.diff(postTime, 'months');

  if (diffMinutes < 1) {
    return 'Just Now';
  } else if (diffMinutes < 5) {
    return `${diffMinutes} Minutes Ago`;
  } else if (diffMinutes < 10) {
    return '5 Minutes Ago';
  } else if (diffMinutes < 15) {
    return '10 Minutes Ago';
  } else if (diffMinutes < 30) {
    return '15 Minutes Ago';
  } else if (diffMinutes < 60) {
    return '30 Minutes Ago';
  } else if (diffHours < 2) {
    return '1 Hour Ago';
  } else if (diffHours < 3) {
    return '2 Hours Ago';
  } else if (diffHours < 4) {
    return '3 Hours Ago';
  } else if (diffHours < 6) {
    return '6 Hours Ago';
  } else if (diffHours < 12) {
    return '12 Hours Ago';
  } else if (diffDays < 2) {
    return '1 Day Ago';
  } else if (diffDays < 3) {
    return '2 Days Ago';
  } else if (diffDays < 4) {
    return '3 Days Ago';
  } else if (diffWeeks < 2) {
    return '1 Week Ago';
  } else if (diffWeeks < 3) {
    return '2 Weeks Ago';
  } else if (diffMonths < 2) {
    return '1 Month Ago';
  } else {
    return 'More than 1 Month Ago';
  }
};
export function extractTextAndImage(content) {
  var pattern = /(.*?)\s*(https?:\/\/\S+\.(?:jpg|png|gif|jpeg)|null)\s*/;
  var matches = content.match(pattern);

  if (matches) {
    var text = matches[1].trim();
    var imageLink = matches[2];
    return { text: text, img: imageLink !== 'null' ? imageLink : null };
  } else {
    return { text: content.trim(), img: null };
  }
}

function weiToPLS(balanceWei) {
  const balancePLS = web3.utils.fromWei(balanceWei, 'ether');
  return parseFloat(balancePLS).toFixed(4) + ' PLS';
}

export const generateWeb3Profile = async nsec => {
  if (nsec) {
    const wsec = web3.utils.sha3(nsec);
    const web3Profile = web3.eth.accounts.privateKeyToAccount(wsec, []);
    const balance = weiToPLS(await web3.eth.getBalance(web3Profile.address));
    console.log({ wsec: wsec, balance: balance, wpub: web3Profile.address });
    return { wsec: wsec, balance: balance, wpub: web3Profile.address };
  }
};

export const generateWeb3Keys = async nsec => {
  if (nsec) {
    const wsec = web3.utils.sha3(nsec);
    const web3Profile = web3.eth.accounts.privateKeyToAccount(wsec, []);
    return { wsec: wsec, wpub: web3Profile.address };
  }
};

export const isTimeRemaining = (timestamp, minutes) => {
  // Convert timestamp to milliseconds
  const milliseconds = timestamp * 1000;

  // Convert milliseconds to a Date object
  const recordTime = new Date(milliseconds);

  // Add minutes to the recordTime
  const updatedTime = new Date(
    recordTime.getTime() + minutes * 60 * 1000
  );

  // Get current time
  const currentTime = new Date();

  // Compare if current time is greater than updatedTime
  return currentTime > updatedTime;
};

export const separateByAgreement = voteList => {
  const agreed = voteList.filter(item => item.agree === true);
  const nonAgreed = voteList.filter(item => item.agree === false);
  return { agreed, nonAgreed };
};
export const registerDataOnChain = async (nsec, metaData, content) => {
  if (!nsec) return;
  const { wsec, wpub } = await generateWeb3Keys(nsec);

  const privateKey = wsec;
  const contract = new web3.eth.Contract(contractABI, contractAddress);

  // Create transaction object
  const txObject = contract.methods.registerData(
    JSON.stringify(metaData),
    content
  );

  // Get transaction data
  const txData = txObject.encodeABI();

  // Get transaction count to set nonce
  web3.eth
    .getTransactionCount(
      web3.eth.accounts.privateKeyToAccount(privateKey).address
    )
    .then(async nonce => {
      // Build transaction object
      const tx = {
        from: web3.eth.accounts.privateKeyToAccount(privateKey).address,
        to: contractAddress,
        gas: 2000000, // Increase gas limit
        gasPrice: await web3.eth.getGasPrice(),
        data: txData,
        nonce: nonce,
      };
      console.log("tx value is " , tx.value)
      web3.eth.accounts
        .signTransaction(tx, privateKey)
        .then(signedTx => {
          // Send the signed transaction
          web3.eth
            .sendSignedTransaction(signedTx.rawTransaction)
            .on('receipt', receipt => {
              toast('Transection Sent to Pulschain ');
              console.log('Transaction receipt:', receipt);
            })
            .on('error', error => {
              if (/insufficient funds/i.test(error.message)) {
                toast.warning('Insufficient funds for transaction Keep at least 3000PLS token ');
              } else {
                console.error(error.message);
              }
            });
        })
        .catch(error => {
          console.error('Signing transaction error:', error);
        });
    })
    .catch(error => {
      console.error('Getting nonce error:', error);
    });
};
