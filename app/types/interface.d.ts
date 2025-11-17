// /types/electron.d.ts
export interface IElectronAPI {
    send: (channel) => void
    on: (channel, func) => void
}

declare global {
    interface Window {
        electronAPI: IElectronAPI
    }
}
