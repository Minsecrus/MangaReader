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
    }
})
