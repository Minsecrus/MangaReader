// main.cjs
const { app, BrowserWindow, ipcMain, desktopCapturer, screen, globalShortcut, shell } = require('electron')
const path = require('path')
const fs = require('fs')
const { BackendService } = require('./backend-service.cjs')

// 判断是否为开发环境 (由 Electron Forge 自动设置)
const isDev = !app.isPackaged

let mainWindow // 将 mainWindow 提升到全局，以便我们可以从 ipcMain 访问它

let captureWindow = null
let backendService = null // OCR 服务实例

// 全局 store 变量
let store

function getModelsPath() {
    // 开发环境：项目根目录/models
    // 生产环境：安装目录/resources/models
    return isDev
        ? path.join(__dirname, '../models')
        : path.join(process.resourcesPath, 'models')
}

// ✅ 初始化 Electron Store (处理 ESM 导入)
async function initStore() {
    const { default: Store } = await import('electron-store')

    store = new Store({
        name: 'config', // 文件名为 config.json
        defaults: {     // 默认配置，防止首次运行为空
            enableTranslation: false,
            enableTokenization: true,
            translationApiKey: '',
            theme: 'system',
            ocrShortcut: ''
        }
    })
    return store
}

function createMainWindow() {
    // 创建浏览器窗口
    mainWindow = new BrowserWindow({
        width: 1200,
        height: 800,
        frame: false, // 禁用默认边框
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

    // ✅ 新增：监听窗口最大化/还原事件，并发送给前端
    mainWindow.on('maximize', () => {
        mainWindow.webContents.send('window:state-change', 'maximized')
    })

    mainWindow.on('unmaximize', () => {
        mainWindow.webContents.send('window:state-change', 'normal')
    })

    // 窗口准备好时，也可以发送一次当前状态（可选，防止初始状态不对）
    mainWindow.once('ready-to-show', () => {
        if (mainWindow.isMaximized()) {
            mainWindow.webContents.send('window:state-change', 'maximized')
        }
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

// --- IPC Handlers ---

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

// ✅ 新增：打开模型文件夹
ipcMain.on('open-model-folder', () => {
    const modelsRoot = getModelsPath()
    // 打开 models 根目录，让用户看到 ocr/translation 等子文件夹
    if (!fs.existsSync(modelsRoot)) {
        fs.mkdirSync(modelsRoot, { recursive: true })
    }
    shell.openPath(modelsRoot)
})

// OCR 识别请求
ipcMain.handle('ocr:recognize', async (event, imageBase64) => {
    try {
        console.log('Received OCR request, image size:', imageBase64.length)

        if (!backendService || !backendService.isReady) {
            return {
                success: false,
                error: 'OCR service not ready. Please wait...'
            }
        }

        const text = await backendService.recognize(imageBase64)

        return {
            success: true,
            text: text
        }
    } catch (error) {
        console.error('OCR recognition error:', error)
        return {
            success: false,
            error: error.message
        }
    }
})

// 分词请求
ipcMain.handle('ocr:tokenize', async (event, text) => {
    try {
        if (!backendService) return { success: false, error: "Service not ready" }
        // 调用 Service
        const result = await backendService.tokenize(text)
        console.log('Tokenize result:', result)
        if (!result) {
            throw new Error('Service returned empty result')
        }

        // Service 返回的是 { tokens: [...] }
        return { success: true, tokens: result.tokens }
    } catch (e) {
        return { success: false, error: e.message }
    }
})

// 窗口控制 IPC 监听器 监听渲染进程发送的事件
ipcMain.on('window:minimize', () => {
    if (mainWindow) {
        mainWindow.minimize()
    }
})

ipcMain.on('window:maximize', () => {
    if (mainWindow) {
        if (mainWindow.isMaximized()) {
            mainWindow.unmaximize()
        } else {
            mainWindow.maximize()
        }
    }
})

ipcMain.on('window:close', () => {
    if (mainWindow) {
        mainWindow.close()
    }
})

app.whenReady().then(async () => {
    try {
        // 1. 先等待 store 初始化完成
        await initStore()
        console.log('✅ Electron Store initialized')

        // 2. 注册 Settings 相关的 IPC
        // 获取所有设置
        ipcMain.handle('settings:get', () => {
            return store.store // .store 返回整个配置对象
        })

        // 保存单个设置 (key, value)
        ipcMain.on('settings:set', (event, key, value) => {
            store.set(key, value)
        })

        // 打开配置文件 (给用户看)
        ipcMain.on('settings:open-config', () => {
            store.openInEditor()
        })

        const modelsRoot = getModelsPath()
        const ocrModelPath = path.join(modelsRoot, 'ocr')
        if (!fs.existsSync(ocrModelPath)) {
            fs.mkdirSync(ocrModelPath, { recursive: true })
        }

        // 启动 OCR 服务
        backendService = new BackendService(ocrModelPath)
        backendService.start()

        // 监听打开外部链接的请求
        ipcMain.handle('shell:open', async (event, url) => {
            // 安全起见，只允许打开 http/https 协议
            if (url.startsWith('http://') || url.startsWith('https://')) {
                await shell.openExternal(url)
            }
        })

        // 创建主窗口
        createMainWindow()
    }
    catch (e) {
        console.log('启动时错误', e)
    }
})

app.on('window-all-closed', () => {
    // 停止 OCR 服务
    if (ocrService) {
        ocrService.stop()
    }

    if (process.platform !== 'darwin') {
        app.quit()
    }
})

app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
        createMainWindow()
    }
})
