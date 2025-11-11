<!-- app/pages/index.vue -->
<script setup lang="ts">
// dark light mode 切换 同时检测用户浏览器的明暗模式设置
const isDark = ref(false)
const toggleDark = () => {
    isDark.value = !isDark.value
    document.documentElement.classList.toggle('dark')
}
onMounted(() => {
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches
    if (prefersDark) {
        isDark.value = true
        // document.documentElement 选取html 根元素 符合v4最佳实践
        document.documentElement.classList.add('dark')
    }
})

// 原文显示板块 使用 v-model 双向绑定
const originalText = ref('今日はいい天気ですね。漫画を読みながら日本語を勉強します。')

const handleImageUpload = () => console.log('打开文件选择器')
const handleScreenshot = () => console.log('开始截图')
const handleSettings = () => console.log('打开设置')
const handleVocabulary = () => console.log('打开生词本')

</script>

<template>
    <div class="min-h-screen bg-manga-50 dark:bg-manga-700">
        <header class="px-6 py-4 border-b border-manga-200 dark:border-manga-600 bg-manga-100 dark:bg-manga-800">
            <div class="flex items-center justify-between max-w-screen-2xl mx-auto">
                <div class="flex items-center gap-6">
                    <h1 class="text-2xl font-bold text-manga-900 dark:text-manga-100">📚 MangaReader</h1>
                </div>
                <div class="flex items-center gap-3">
                    <Button variant="secondary" size="sm" @click="handleVocabulary">📖 生词本</Button>
                    <Button variant="secondary" size="sm" @click="handleSettings">⚙️ 设置</Button>
                    <Button size="sm" @click="toggleDark">
                        <!-- 模式切换按钮 -->
                        {{ isDark ? '☀️' : '🌙' }}
                    </Button>
                </div>
            </div>
        </header>

        <main class="max-w-screen-2xl mx-auto p-6">
            <div class="grid grid-cols-1 lg:grid-cols-5 gap-6 h-[calc(100vh-120px)]">
                <div class="lg:col-span-3">
                    <div
                        class="p-4 transition-all duration-200 shadow-base border border-manga-200 dark:border-manga-500 rounded-primary hover:shadow-card hover:-translate-y-0.5 h-full flex items-center justify-center bg-manga-50 dark:bg-manga-700">
                        <div class="text-center">
                            <div class="text-6xl mb-4">🖼️</div>
                            <p class="text-lg mb-2 text-manga-900 dark:text-manga-100">图片预览区域</p>
                            <p class="text-sm mb-6 text-manga-600 dark:text-manga-400">拖拽图片到此处</p>
                            <div class="flex gap-3 justify-center">
                                <Button @click="handleImageUpload">📁 选择图片</Button>
                                <Button variant="secondary" @click="handleScreenshot">✂️ 截图</Button>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="lg:col-span-2 space-y-4">
                    <OriginalText v-model:local-text="originalText" />
                    <!-- 这里indexvue起到一个父组件传递originalText的作用 v-model 传递给originalText再传递给Translationvue -->
                    <TokenizedWords :origin-text="originalText" />
                    <Translation :original-text="originalText" />
                    <HintCard text="提示：点击分词结果中的单词可查看详情" />
                </div>
            </div>
        </main>
    </div>
</template>
