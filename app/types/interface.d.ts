// /types/electron.d.ts
export interface IElectronAPI {
    send: (channel: string, data?: any) => void
    on: (channel: string, func: (...args: any[]) => void) => void
    recognizeText: (imageBase64: string) => Promise<{ success: boolean; text?: string; error?: string }>
    // 窗口控制
    minimizeWindow: () => void
    maximizeWindow: () => void
    closeWindow: () => void
    onWindowStateChange: (callback) => void
}

declare global {
    interface Window {
        electronAPI: IElectronAPI
    }
}
