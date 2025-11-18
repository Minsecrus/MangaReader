<!-- app/pages/index.vue -->
<script setup lang="ts">
// 原文显示板块 使用 v-model 双向绑定
const originalText = ref('今日はいい天気ですね。漫画を読みながら日本語を勉強します。')

const isOcrMode = ref(false) // ocr模式 鼠标十字crosshair
const isOcrRecognizing = ref(false) // 正在调用模型识别

const handleOcr = () => {
    // 激活 OCR 模式，显示框选 overlay
    isOcrMode.value = true
}

// ocr识别完成 处理ocrCaptureImage
const handleOcrCapture = async (selectionData: { left: number, top: number, width: number, height: number }) => {
    isOcrRecognizing.value = true // 图片传递给模型 模型加载

    console.log('OCR 框选区域:', selectionData)

    // TODO: 将选区数据和当前图片发送给主进程进行 OCR 识别
    // window.electronAPI.send('ocr:recognize', { selectionData, imageUrl })

    // 模拟识别
    setTimeout(() => {
        isOcrRecognizing.value = false
        originalText.value = '识别的文本会显示在这里'
    }, 2000)
}

const handleOcrCancel = () => {
    // 用户主动按下esc推出ocr模式
    isOcrMode.value = false
}
</script>

<template>
    <div class="min-h-screen bg-manga-50 dark:bg-manga-700">
        <header class="px-6 py-4 border-b border-manga-200 dark:border-manga-600 bg-manga-100 dark:bg-manga-800">
            <Nav />
        </header>

        <main class="max-w-screen-2xl mx-auto p-6">
            <div class="grid grid-cols-1 lg:grid-cols-5 gap-6 h-[calc(100vh-120px)]">
                <div class="lg:col-span-3 relative">
                    <ImageUpload />
                    <!-- OCR 框选 overlay -->
                    <OcrOverlay v-if="isOcrMode" @capture-complete="handleOcrCapture" @cancel="handleOcrCancel" />
                </div>

                <div class="lg:col-span-2 space-y-4">
                    <OcrButton @ocr-btn-click="handleOcr" :is-recognizing="isOcrRecognizing" :is-in-ocr="isOcrMode" />
                    <OriginalText :is-recognizing="isOcrRecognizing" v-model:local-text="originalText" />
                    <!-- 这里indexvue起到一个父组件传递originalText的作用 v-model 传递给originalText再传递给Translationvue -->
                    <TokenizedWords :origin-text="originalText" />
                    <Translation :original-text="originalText" />
                    <HintCard text="提示：点击分词结果中的单词可查看详情" />
                </div>
            </div>
        </main>
    </div>
</template>
