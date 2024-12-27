const exec = require('child_process').exec;

exec('react-app-rewired build', (error, stdout, stderr) => {
  if (error) {
    console.warn(`Build completed with errors:\n${stderr}`);
  } else {
    console.log(`Build successful:\n${stdout}`);
  }
});
