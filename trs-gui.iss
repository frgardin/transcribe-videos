[Setup]
AppName=trs
AppVersion={#AppVersion}
AppPublisher=frgardin
AppPublisherURL=https://github.com/frgardin/transcribe-videos
AppSupportURL=https://github.com/frgardin/transcribe-videos/issues
AppUpdatesURL=https://github.com/frgardin/transcribe-videos/releases
DefaultDirName={autopf}\trs
DefaultGroupName=trs
AllowNoIcons=yes
OutputDir=dist
OutputBaseFilename=trs-gui-setup
Compression=lzma
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "dist\trs-gui.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\trs — Transcribe Videos"; Filename: "{app}\trs-gui.exe"
Name: "{group}\{cm:UninstallProgram,trs}"; Filename: "{uninstallexe}"
Name: "{commondesktop}\trs"; Filename: "{app}\trs-gui.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\trs-gui.exe"; Description: "{cm:LaunchProgram,trs}"; Flags: nowait postinstall skipifsilent
