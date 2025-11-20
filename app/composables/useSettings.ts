// composables/useSettings.ts
export type ThemeOption = 'system' | 'light' | 'dark'

export const useSettings = () => {
    // 这里存放具体的设置数据
    const settings = useState('app-settings', () => ({
        enableOcr: true,
        enableTranslation: false,
        enableTokenization: true,
        translationApiKey: '',
        theme: 'system' as ThemeOption, // 默认为跟随系统
        screenshotShortcut: 'Ctrl+Shift+S'
    }))

    const applyTheme = () => {
        if (!import.meta.client) return

        const html = document.documentElement
        const isDarkSystem = window.matchMedia('(prefers-color-scheme: dark)').matches

        let shouldBeDark = false

        if (settings.value.theme === 'system') {
            shouldBeDark = isDarkSystem
        } else {
            shouldBeDark = settings.value.theme === 'dark'
        }

        if (shouldBeDark) {
            html.classList.add('dark')
        } else {
            html.classList.remove('dark')
        }
    }

    watch(() => settings.value.theme, () => {
        applyTheme()
        // 这里记得调用 saveSetting 保存到 electron-store
    })
    if (import.meta.client) {
        const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)')
        mediaQuery.addEventListener('change', () => {
            if (settings.value.theme === 'system') {
                applyTheme()
            }
        })
    }

    // 打开模型文件夹 (调用 Electron)
    const openModelFolder = () => {
        if (import.meta.client) {
            window.electronAPI?.send('open-model-folder')
        }
    }

    // 保存设置 (持久化到 localStorage 或 electron-store)
    const saveSettings = () => {
        // 这里写保存逻辑，比如存入 localStorage
        localStorage.setItem('manga-reader-settings', JSON.stringify(settings.value))
        console.log('设置已保存')
    }

    // 初始化读取
    const initSettings = () => {
        if (import.meta.client) {
            const saved = localStorage.getItem('manga-reader-settings')
            if (saved) {
                Object.assign(settings.value, JSON.parse(saved))
            }
        }
    }

    return {
        settings,
        applyTheme,
        openModelFolder,
        saveSettings,
        initSettings
    }
}
