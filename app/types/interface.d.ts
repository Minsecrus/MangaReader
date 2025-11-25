// /types/electron.d.ts

// 定义 Token 类型
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
    [key: string]: any // 允许索引访问
}

export interface IElectronAPI {
    send: (channel: string, data?: any) => void
    on: (channel: string, func: (...args: any[]) => void) => void
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

    // ✅ 新增：Settings 接口
    getSettings: () => Promise<AppSettings>
    saveSetting: (key: string, value: any) => void
    openConfigFile: () => void

    // About页面打开链接
    openLink: (url: string) => Promise<void>
}

declare global {
    interface Window {
        electronAPI: IElectronAPI
    }
}
