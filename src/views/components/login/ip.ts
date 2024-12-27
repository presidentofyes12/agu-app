// utils/ip.ts
export const getUserIP = async (): Promise<string> => {
  const response = await fetch('https://api.ipify.org?format=json');
  const data = await response.json();
  return data.ip;
};