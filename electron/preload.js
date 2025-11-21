// electron/preload.js
const { contextBridge, ipcRenderer } = require('electron')

contextBridge.exposeInMainWorld('electronAPI', {

    // 支持发送消息(带或不带数据)
    send: (channel, data) => {
        ipcRenderer.send(channel, data) // 渲染进程向主进程发送异步消息不等待响应
    },

    on: (channel, func) => {
        ipcRenderer.on(channel, (event, ...args) => func(...args))
    },

    // OCR 识别
    recognizeText: (imageBase64) => {
        return ipcRenderer.invoke('ocr:recognize', imageBase64)
    },

    // 窗口控制 声明给渲染进程
    minimizeWindow: () => ipcRenderer.send('window:minimize'),
    maximizeWindow: () => ipcRenderer.send('window:maximize'),
    closeWindow: () => ipcRenderer.send('window:close'),

    // ✅ 新增：监听窗口状态变化
    onWindowStateChange: (callback) => {
        ipcRenderer.on('window:state-change', (event, state) => callback(state))
    },

    // ✅ 新增：Settings API
    getSettings: () => ipcRenderer.invoke('settings:get'),
    saveSetting: (key, value) => ipcRenderer.send('settings:set', key, value),
    openConfigFile: () => ipcRenderer.send('settings:open-config')
})
