<!-- components/SettingsModal.vue -->
<script setup lang="ts">
// 接收一个布尔值控制显示隐藏
defineProps<{
    show: boolean
}>()
const emit = defineEmits<{
    close: []
}>()

const themeOptions: ThemeOption[] = ['light', 'dark', 'system']

const handleClose = () => {
    console.log(111)
    emit('close')
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
                                <input type="checkbox" class="cursor-pointer">
                            </label>

                            <label class="flex items-center justify-between cursor-pointer">
                                <span class="text-manga-900 dark:text-manga-200">
                                    启用翻译
                                </span>
                                <input type="checkbox" class="cursor-pointer">
                            </label>
                        </div>

                        <div class="space-y-3">
                            <h3 class="text-sm font-medium text-manga-500 uppercase">🎨 外观</h3>
                            <div class="flex gap-4 bg-manga-50 dark:bg-manga-900 p-2 rounded-lg">
                                <button v-for="mode in themeOptions" :key="mode"
                                    class="bg-white dark:bg-manga-700 shadow text-blue-600 dark:text-blue-400 font-bold flex-1 py-2 rounded-md text-sm cursor-pointer">
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
                                <Button size="sm" variant="secondary">
                                    📂 打开文件夹
                                </Button>
                            </div>
                        </div>
                    </div>

                    <!-- 底部按钮 -->
                    <div class="mt-8 flex justify-end">
                        <Button @click="handleClose">完成</Button>
                    </div>
                </div>
            </Transition>
        </div>
    </Teleport>
</template>
