// /types/electron.d.ts
export interface IElectronAPI {
    send: (channel: string, data?: any) => void
    on: (channel: string, func: (...args: any[]) => void) => void
    recognizeText: (imageBase64: string) => Promise<{ success: boolean; text?: string; error?: string }>
}

declare global {
    interface Window {
        electronAPI: IElectronAPI
    }
}
