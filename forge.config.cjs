const { FusesPlugin } = require('@electron-forge/plugin-fuses');
const { FuseV1Options, FuseVersion } = require('@electron/fuses');

module.exports = {
  packagerConfig: {
    icon: './public/MangaReaderLogo',
    asar: true,
    // 1. 将打包好的 Python 后端作为额外资源复制到 resources 目录
    extraResource: [
      './dist/backend',
    ],
    // 2. 忽略不需要打包的文件 (减小体积)
    ignore: [
      /^\/services/, // 忽略 Python 源码 (因为已经打包成 exe 了)
      /^\/README\.md$/, // 忽略 README
      /^\/public\/MangaReader_Header\.png$/, // 忽略 Banner 图片
      /^\/\.gitignore$/,
      /^\/forge\.config\.js$/,
      /^\/tsconfig\.json$/,
      /^\/nuxt\.config\.ts$/,
      /^\/models/, // 忽略 models 文件夹 (用户运行时下载)
      // 注意：不要忽略 .output (这是 Nuxt 构建后的前端)
    ]
  },
  rebuildConfig: {},
  makers: [
    {
      name: '@electron-forge/maker-squirrel',
      config: {
        name: 'MangaReader',
        authors: 'Malloy',
        description: 'A tool helps manga lover and Japanese learner read manga easily',
        setupIcon: './public/MangaReaderLogo.ico',
      },
    },
    {
      name: '@electron-forge/maker-zip',
      platforms: ['darwin', 'win32'], // 显式添加 win32
    },
  ],
  plugins: [
    {
      name: '@electron-forge/plugin-auto-unpack-natives',
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
