<!-- components/SettingsModal.vue -->
<script setup lang="ts">
// 接收一个布尔值控制显示隐藏
defineProps<{
    show: boolean
}>()
const emit = defineEmits<{
    close: []
}>()

const { settings, saveSettings, openModelFolder } = useSettings()
const { showToast } = useToast()

const themeOptions: ThemeOption[] = ['light', 'dark', 'system']

// --- 快捷键录制逻辑 ---
const isRecording = ref(false) // 是否正在录制
const shortcutInputRef = useTemplateRef<HTMLInputElement>('shortcutInputRef')

// 开始录制
const startRecording = () => {
    isRecording.value = true
    // 提示用户
    showToast('请按下快捷键组合，按 Enter 确认，Esc 取消，Backspace 删除', 3000)

    // 清空当前显示，准备录入 (或者你可以选择保留旧的作为默认，这里选择清空以此体现“重新录制”)
    // settings.value.ocrShortcut = '' 
}

// 结束录制 (失焦或确认)
const stopRecording = () => {
    isRecording.value = false
    shortcutInputRef.value?.blur()
}

// 监听按键事件
const handleKeyDown = (e: KeyboardEvent) => {
    if (!isRecording.value) return

    e.preventDefault() // 阻止浏览器默认行为 (比如按 Ctrl+S 不会弹出保存网页)
    e.stopPropagation()

    // 1. 处理取消 (Esc)
    if (e.key === 'Escape') {
        stopRecording()
        showToast('已取消录制', 1000)
        return
    }

    // 2. 处理确认 (Enter)
    if (e.key === 'Enter') {
        if (settings.value.ocrShortcut) {
            console.log('✅ 快捷键设置成功:', settings.value.ocrShortcut)
            showToast(`快捷键已设置为: ${settings.value.ocrShortcut}`, 1500)
        }
        stopRecording()
        return
    }

    // 3. 处理退格 (Backspace) - 清除当前快捷键
    if (e.key === 'Backspace') {
        settings.value.ocrShortcut = ''
        return
    }

    // 4. 构建快捷键字符串
    const keys = []

    // 判断修饰键
    if (e.ctrlKey) keys.push('Ctrl')
    if (e.metaKey) keys.push('Cmd') // Mac Command 键
    if (e.altKey) keys.push('Alt')
    if (e.shiftKey) keys.push('Shift')

    // 获取主按键
    // 排除掉修饰键本身 (例如用户只按了 Ctrl，我们不希望显示 "Ctrl + Control")
    const specialKeys = ['Control', 'Meta', 'Alt', 'Shift']
    if (!specialKeys.includes(e.key)) {
        // 将按键转为大写，比如 'a' -> 'A', 'ArrowUp' -> 'ArrowUp'
        let keyName = e.key.toUpperCase()
        if (keyName === ' ') keyName = 'Space' // 空格特殊处理
        keys.push(keyName)
    }

    // 只有当有按键时才更新 (避免只按 Ctrl 显示空)
    if (keys.length > 0) {
        // 将数组用 " + " 连接，例如 "Ctrl + Shift + A"
        settings.value.ocrShortcut = keys.join(' + ')
    }
}

const handleClose = () => {
    emit('close')
}

const handleSave = () => {
    saveSettings()
    emit('close')
    showToast('设置已保存 👌', 1500)
}
</script>

<template>
    <!-- 遮罩层: 只在 show 为 true 时显示 -->
    <!-- Teleport to body 确保它不会受父元素 overflow 影响，永远在最上层 -->
    <Teleport to="body">
        <div class="fixed inset-0 z-50 flex items-center justify-center" :class="{ 'pointer-events-none': !show }">
            <Transition enter-active-class="transition duration-200 ease-out"
                leave-active-class="transition duration-150 ease-in" enter-from-class="opacity-0"
                leave-to-class="opacity-0" enter-to-class="opacity-100" leave-from-class="opacity-100">
                <!-- 黑色半透明背景 -->
                <div v-if="show" class="absolute inset-0 bg-black/50 backdrop-blur-sm" @click="handleClose"></div>
            </Transition>
            <Transition enter-active-class="transition duration-300 ease-out delay-75"
                leave-active-class="transition duration-150 ease-in" enter-from-class="opacity-0 scale-95 translate-y-4"
                leave-to-class="opacity-0 scale-95 translate-y-4" enter-to-class="opacity-100 scale-100 translate-y-0"
                leave-from-class="opacity-100 scale-100 translate-y-0">

                <!-- 设置卡片主体 -->
                <div v-if="show"
                    class="relative w-full max-w-lg bg-white dark:bg-manga-800 rounded-xl shadow-2xl p-6 border border-manga-200 dark:border-manga-700 transform transition-all">

                    <!-- 标题栏 -->
                    <div class="flex justify-between items-center mb-6">
                        <h2 class="text-xl font-bold text-manga-900 dark:text-white">
                            ⚙️ 设置
                        </h2>
                        <button @click="handleClose"
                            class="text-manga-500 hover:text-manga-700 dark:text-manga-400 hover:dark:text-white cursor-pointer">
                            ✕
                        </button>
                    </div>

                    <!-- 内容区域 -->
                    <div class="space-y-6">
                        <!-- 模块开关 -->
                        <div class="space-y-3">
                            <h3 class="text-sm font-medium text-manga-500 dark:text-manga-400 uppercase">功能模块</h3>

                            <label class="flex items-center justify-between cursor-pointer">
                                <span class="text-manga-900 dark:text-manga-200">
                                    启用分词 (Tokenization)
                                </span>
                                <input type="checkbox" class="cursor-pointer" v-model="settings.enableTokenization">
                            </label>

                            <label class="flex items-center justify-between cursor-pointer">
                                <span class="text-manga-900 dark:text-manga-200">
                                    启用翻译
                                </span>
                                <input type="checkbox" class="cursor-pointer" v-model="settings.enableTranslation">
                            </label>
                        </div>

                        <!-- 快捷键设置 -->
                        <div class="space-y-3">
                            <h3 class="text-sm font-medium text-manga-500 dark:text-manga-400 uppercase">
                                ⌨️ 快捷键 (OCR)
                            </h3>
                            <div class="relative">
                                <input ref="shortcutInputRef" type="text" readonly
                                    :value="isRecording ? (settings.ocrShortcut || '请按下按键...') : (settings.ocrShortcut || '未设置')"
                                    @click="startRecording" @keydown="handleKeyDown" @blur="stopRecording"
                                    class="w-full px-3 py-2 rounded-lg text-sm font-mono text-center cursor-pointer transition-all border outline-none"
                                    :class="[
                                        isRecording
                                            ? 'bg-blue-50 dark:bg-blue-900/30 border-blue-500 text-blue-600 dark:text-blue-300 ring-2 ring-blue-200 dark:ring-blue-800'
                                            : 'bg-manga-50 dark:bg-manga-900 border-manga-200 dark:border-manga-700 text-manga-600 dark:text-manga-300 hover:border-manga-400'
                                    ]" />
                                <!-- 录制状态指示器 -->
                                <span v-if="isRecording" class="absolute right-3 top-2.5 flex h-3 w-3">
                                    <span
                                        class="animate-ping absolute inline-flex h-full w-full rounded-full bg-red-400 opacity-75"></span>
                                    <span class="relative inline-flex rounded-full h-3 w-3 bg-red-500"></span>
                                </span>
                            </div>
                            <p class="text-xs text-center text-manga-400">
                                {{ isRecording ? '按 Esc 取消，Enter 确认' : '点击上方框框开始录制' }}
                            </p>
                        </div>

                        <!-- 外观设置 -->
                        <div class="space-y-3">
                            <h3 class="text-sm font-medium text-manga-500 uppercase">🎨 外观</h3>
                            <div class="flex gap-4 bg-manga-50 dark:bg-manga-900 p-2 rounded-lg">
                                <button v-for="mode in themeOptions" :key="mode" @click="settings.theme = mode"
                                    class="cursor-pointer flex-1 py-2 rounded-md text-sm transition-all" :class="[
                                        settings.theme === mode
                                            ? 'bg-white dark:bg-manga-700 shadow text-blue-600 dark:text-blue-400 font-bold'
                                            : 'text-manga-500 hover:text-manga-700 dark:hover:text-manga-300']">
                                    {{ mode === 'light' ? '☀️ 浅色' : mode === 'dark' ? '🌙 深色' : '💻 跟随系统' }}
                                </button>
                            </div>
                        </div>

                        <!-- 模型管理 -->
                        <div class="pt-4 border-t border-manga-100 dark:border-manga-700">
                            <h3 class="text-sm font-medium text-manga-500 dark:text-manga-400 uppercase mb-3">模型管理
                            </h3>
                            <div class="bg-manga-50 dark:bg-manga-900 p-4 rounded-lg flex justify-between items-center">
                                <div class="text-sm text-manga-600 dark:text-manga-300">
                                    需要离线使用？请放置模型文件
                                </div>
                                <Button size="sm" variant="secondary" @btn-click="openModelFolder">
                                    📂 打开文件夹
                                </Button>
                            </div>
                        </div>
                    </div>

                    <!-- 底部按钮 -->
                    <div class="mt-8 flex justify-end">
                        <Button @btn-click="handleSave">完成</Button>
                    </div>
                </div>
            </Transition>
        </div>
    </Teleport>
</template>
