// main.js
const { app, BrowserWindow, ipcMain, desktopCapturer, screen, globalShortcut } = require('electron')
const path = require('path')

// 判断是否为开发环境 (由 Electron Forge 自动设置)
const isDev = !app.isPackaged

let mainWindow // 将 mainWindow 提升到全局，以便我们可以从 ipcMain 访问它

let captureWindow = null

function createMainWindow() {
    // 创建浏览器窗口
    mainWindow = new BrowserWindow({
        width: 1200,
        height: 800,
        webPreferences: {
            contextIsolation: true,
            preload: path.join(__dirname, 'preload.js')
        },
    })

    if (isDev) {
        // 开发环境下，加载 Nuxt 的开发服务器 URL
        // 我们明确告诉它加载 Nuxt 默认的 3000 端口
        mainWindow.loadURL('http://localhost:3000')
        // 打开开发者工具
        mainWindow.webContents.openDevTools()
    } else {
        // 生产环境下，加载 Nuxt 构建后的静态文件
        // Nuxt 4 的 SSG 输出目录是 .output/public
        mainWindow.loadFile(path.join(__dirname, '../.output/public/index.html'))
    }

    // Handle window closed event properly
    mainWindow.on('closed', () => {
        mainWindow = null
    })
}

async function createCaptureWindow() {
    const { bounds: { width, height }, scaleFactor } = screen.getPrimaryDisplay() // 考虑到缩放比例 以及 宽高
    const sources = await desktopCapturer.getSources({
        types: ['screen'],
        thumbnailSize: { width: width * scaleFactor, height: height * scaleFactor } // 获取到屏幕尺寸 宽高乘缩放比率
    })
    // 屏幕会有多个 获取到第一个 [0]
    const base64 = sources[0].thumbnail.toDataURL() // base64传递到html里渲染

    captureWindow = new BrowserWindow({
        webPreferences: {
            nodeIntegration: true,
            preload: path.join(__dirname, 'preload.js')
        },
        fullscreen: true, // 全屏
        transparent: true, // 透明
        frame: false, // 无框架
        skipTaskbar: true, // 底部任务栏不创建图标
        autoHideMenuBar: true, // 自动隐藏菜单
        movable: false, // 禁止拖拽
        resizable: false, // 禁止改变大小
        enableLargerThanScreen: true, // 允许窗口大于屏幕
        hasShadow: false, // 无阴影
        show: false, // 默认不显示
    })
    captureWindow.loadFile(path.join(__dirname, 'overlay.html'))
    captureWindow.on('show', () => {
        // 传递 base64 和 scaleFactor
        captureWindow.webContents.send('window:capture-source', { base64, scaleFactor })

        globalShortcut.register('Esc', () => {
            captureWindow.close()
        })
    })
    captureWindow.on('close', () => {
        mainWindow.show()
        globalShortcut.unregister('Esc')
    })
    captureWindow.show() // 监听上面的show事件

}

ipcMain.on('window:capture-open', () => {
    // 截图的时间隐藏主窗口 同时 截图完毕或者退出的时间再重新显示
    mainWindow.hide()
    // 先隐藏主窗口,等待一小段时间确保窗口完全隐藏后再创建截图窗口
    // 这样可以避免在截图时捕获到半透明的主窗口
    setTimeout(() => {
        createCaptureWindow()
    }, 100) // 等待 100ms 确保主窗口完全隐藏
})

// 接收截图完成事件
ipcMain.on('window:capture-complete', (event, screenshotData) => {
    // 将截图数据发送给主窗口
    if (mainWindow && !mainWindow.isDestroyed()) {
        mainWindow.webContents.send('screenshot:captured', screenshotData)
    }
    // 关闭截图窗口
    if (captureWindow && !captureWindow.isDestroyed()) {
        captureWindow.close()
    }
})


ipcMain.on('window:capture-close', () => {
    if (captureWindow) {
        captureWindow.close()
        captureWindow = null
    }
    mainWindow.show()
})

app.whenReady().then(createMainWindow)

app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') {
        app.quit()
    }
})

app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
        createMainWindow()
    }
})