// electron/preload.js
// import { contextBridge, ipcRenderer } from 'electron'
const { contextBridge, ipcRenderer } = require('electron')

contextBridge.exposeInMainWorld('electronAPI', {

    // 支持发送消息(带或不带数据)
    send: (channel, data) => {
        ipcRenderer.send(channel, data) // 渲染进程向主进程发送异步消息不等待响应
    },

    on: (channel, func) => {
        ipcRenderer.on(channel, (event, ...args) => func(...args))
    }
})
