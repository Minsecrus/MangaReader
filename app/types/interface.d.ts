// types/electron.d.ts
export interface Token {
    word: string
    type: 'noun' | 'verb' | 'particle' | 'adjective' | 'other'
    reading?: string
    dictionary_form?: string
}

// 定义设置对象的接口
export interface AppSettings {
    enableTranslation: boolean
    enableTokenization: boolean
    translationApiKey: string
    theme: 'system' | 'light' | 'dark'
    ocrShortcut: string
    [key: string]: any
}

export interface IElectronAPI {
    // 基础通信
    send: (channel: string, data?: any) => void
    on: (channel: string, func: (...args: any[]) => void) => void

    // OCR 核心
    recognizeText: (imageBase64: string) => Promise<{
        success: boolean
        text?: string
        error?: string
    }>
    tokenize: (text: string) => Promise<{
        success: boolean
        tokens?: Token[]
        error?: string
    }>

    // 窗口控制
    minimizeWindow: () => void
    maximizeWindow: () => void
    closeWindow: () => void
    onWindowStateChange: (callback: (state: 'maximized' | 'normal') => void) => void

    // Settings (Config)
    getSettings: () => Promise<AppSettings>
    saveSetting: (key: string, value: any) => void
    openConfigFile: () => void

    // 其他
    openLink: (url: string) => Promise<void>

    // ✅ 新增：全局快捷键 API
    // 1. 设置快捷键 (返回 boolean 表示是否成功)
    setGlobalShortcut: (shortcut: string) => Promise<boolean>

    // 2. 监听快捷键触发
    // 参数是一个回调函数，返回值是一个“清理函数”(用于移除监听)
    onShortcutTriggered: (callback: () => void) => () => void

    checkModel: () => Promise<{ success: boolean; exists?: boolean; error?: string }>
    downloadModel: () => Promise<{ success: boolean; error?: string }>
    deleteModel: () => Promise<{ success: boolean; error?: string }>
    translate: (text: string) => Promise<{ success: boolean; translation?: string; error?: string }>
}

declare global {
    interface Window {
        electronAPI: IElectronAPI
    }
}
