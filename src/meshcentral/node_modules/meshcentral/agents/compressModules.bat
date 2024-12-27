@ECHO OFF
MD modules_meshcmd_min
MD modules_meshcore_min

"..\..\WebSiteCompiler\bin\Debug\WebSiteCompiler.exe" meshcore.js
"..\..\WebSiteCompiler\bin\Debug\WebSiteCompiler.exe" meshcmd.js

%LOCALAPPDATA%\..\Roaming\nvm\v14.16.0\node ..\translate\translate.js minifydir C:\Users\Default.DESKTOP-9CGK2DI\Desktop\AmtWebApp\meshcentral\agents\modules_meshcore C:\Users\Default.DESKTOP-9CGK2DI\Desktop\AmtWebApp\meshcentral\agents\modules_meshcore_min
%LOCALAPPDATA%\..\Roaming\nvm\v14.16.0\node ..\translate\translate.js minifydir C:\Users\Default.DESKTOP-9CGK2DI\Desktop\AmtWebApp\meshcentral\agents\modules_meshcmd C:\Users\Default.DESKTOP-9CGK2DI\Desktop\AmtWebApp\meshcentral\agents\modules_meshcmd_min
