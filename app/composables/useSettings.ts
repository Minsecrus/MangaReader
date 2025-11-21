// composables/useSettings.ts
export type ThemeOption = 'system' | 'light' | 'dark'

export const useSettings = () => {
    // 这里存放具体的设置数据
    const settings = useState('app-settings', () => ({
        enableTranslation: false, // 启用翻译
        enableTokenization: true, // 启用分词
        translationApiKey: '', // 翻译APIkey
        theme: 'system' as ThemeOption, // 默认为跟随系统
        ocrShortcut: ''
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

    if (import.meta.client) {
        watch(settings, (newVal) => {
            // 1. 应用主题
            applyTheme()

            // 2. 保存到 electron-store
            // 我们遍历每一个 key 进行保存，确保数据同步
            // (electron-store 是本地文件操作，性能开销可以忽略不计)
            for (const [key, value] of Object.entries(newVal)) {
                window.electronAPI.saveSetting(key, value)
            }
        }, { deep: true }) // 深度监听
    }

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

    // ✅ 初始化：从 Electron 读取配置
    const initSettings = async () => {
        if (import.meta.client) {
            try {
                const storedSettings = await window.electronAPI.getSettings()
                // 合并配置：用 store 里的覆盖默认值
                Object.assign(settings.value, storedSettings)
                // 初始化完成后立即应用一次主题
                applyTheme()
                console.log('⚙️ Settings loaded from Electron Store')
            } catch (e) {
                console.error('Failed to load settings:', e)
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
