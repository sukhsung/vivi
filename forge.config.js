const { FusesPlugin } = require("@electron-forge/plugin-fuses");
const { FuseV1Options, FuseVersion } = require("@electron/fuses");

module.exports = {
  packagerConfig: {
    name: "vivi",
    executableName: "vivi", // File name of the actual binary
    asar: true,
    icon: "./src/assets/vivi-icon.png",
  },
  rebuildConfig: {
    // force: true,
  },
  makers: [
    {
      name: "@electron-forge/maker-squirrel",
      config: {
        name: "vivi",
        authors: "Suk Hyun Sung",
        shortcutName: "Vivi",
        setupIcon: "./src/assets/vivi-icon.ico", // optional
        iconUrl: "https://raw.githubusercontent.com/sukhsung/vivi/refs/heads/main/src/assets/vivi-icon.ico", // required if setupIcon is used
        noMsi: true,
        createDesktopShortcut: true,
        createStartMenuShortcut: true,
        shortcutFolderName: "Vivi",
      },
    },
    {
      name: "@electron-forge/maker-zip",
      platforms: ["darwin"],
    },
    {
      name: "@electron-forge/maker-dmg",
      platforms: ["darwin"],
    },
    {
      name: "@electron-forge/maker-deb",
      executableName: "vivi",
      config: {
        options: {
          name: "Vivi",
          maintainer: "https://shsung.com",
        },
      },
    },
    {
      name: "@electron-forge/maker-rpm",
      executableName: "vivi",
      config: {
        options: {
          name: "Vivi",
          maintainer: "https://shsung.com",
        },
      },
    },
  ],
  plugins: [
    {
      name: "@electron-forge/plugin-auto-unpack-natives",
      config: {},
    },
    // Fuses are used to enable/disable various Electron functionality
    // at package time, before code signing the application
    new FusesPlugin({
      version: FuseVersion.V1,
      [FuseV1Options.RunAsNode]: false,
      [FuseV1Options.EnableCookieEncryption]: true,
      [FuseV1Options.EnableNodeOptionsEnvironmentVariable]: false,
      [FuseV1Options.EnableNodeCliInspectArguments]: false,
      [FuseV1Options.EnableEmbeddedAsarIntegrityValidation]: true,
      [FuseV1Options.OnlyLoadAppFromAsar]: true,
    }),
  ],
};
