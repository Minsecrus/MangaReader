<!-- app/pages/index.vue -->
<script setup lang="ts">
// 原文显示板块 使用 v-model 双向绑定
const originalText = ref('今日はいい天気ですね。漫画を読みながら日本語を勉強します。')
const showSettingsModal = ref(false) // settingModal显示
const isOcrMode = ref(false) // ocr模式 鼠标十字crosshair
const isOcrRecognizing = ref(false) // 正在调用模型识别

const handleOcr = () => {
    // 激活 OCR 模式，显示框选 overlay
    isOcrMode.value = true
}

const { initSettings } = useSettings()

// ocr识别完成 处理ocrCaptureImage
const handleOcrCapture = async (selectionData: { left: number, top: number, width: number, height: number }) => {
    isOcrMode.value = false
    isOcrRecognizing.value = true

    try {
        console.log('OCR 框选区域:', selectionData)

        // 创建 canvas 截取选中区域
        const canvas = document.createElement('canvas')
        const { left, top, width, height } = selectionData

        canvas.width = width
        canvas.height = height
        const ctx = canvas.getContext('2d')!

        // 截取整个页面到 canvas
        // 查找 ImageUpload 组件内的图片元素
        const imgElement = document.querySelector('img[alt^="当前图片"]') as HTMLImageElement

        if (!imgElement) {
            throw new Error('未找到图片元素,请先上传图片')
        }

        if (!imgElement.complete || !imgElement.naturalWidth) {
            throw new Error('图片未加载完成')
        }

        // 获取图片元素的位置
        const imgRect = imgElement.getBoundingClientRect()

        // 计算相对于图片的坐标
        const relativeLeft = left - imgRect.left
        const relativeTop = top - imgRect.top

        // 创建临时 canvas 绘制原图
        const tempCanvas = document.createElement('canvas')
        tempCanvas.width = imgElement.naturalWidth
        tempCanvas.height = imgElement.naturalHeight
        const tempCtx = tempCanvas.getContext('2d')!
        tempCtx.drawImage(imgElement, 0, 0)

        // 计算缩放比例
        const scaleX = imgElement.naturalWidth / imgRect.width
        const scaleY = imgElement.naturalHeight / imgRect.height

        // 截取选中区域
        const imageData = tempCtx.getImageData(
            relativeLeft * scaleX,
            relativeTop * scaleY,
            width * scaleX,
            height * scaleY
        )

        // 绘制到目标 canvas
        canvas.width = width * scaleX
        canvas.height = height * scaleY
        ctx!.putImageData(imageData, 0, 0)

        // 转换为 base64
        const imageBase64 = canvas.toDataURL('image/png')

        console.log('发送 OCR 识别请求...')

        // 调用 OCR 识别
        const result = await window.electronAPI.recognizeText(imageBase64)

        if (result.success && result.text) {
            originalText.value = result.text
            console.log('✅ OCR 识别成功:', result.text)
        } else {
            console.error('❌ OCR 识别失败:', result.error)
            alert(`OCR 识别失败: ${result.error}`)
        }

    } catch (error) {
        console.error('OCR 处理错误:', error)
        alert(`OCR 处理错误: ${error}`)
    } finally {
        isOcrRecognizing.value = false
    }
}

const handleOcrCancel = () => {
    // 用户主动按下esc推出ocr模式
    isOcrMode.value = false
}

onMounted(() => {
    initSettings()
})
</script>

<template>
    <div class="min-h-screen bg-manga-50 dark:bg-manga-700">
        <header class="px-6 py-4 border-b border-manga-200 dark:border-manga-600 bg-manga-100 dark:bg-manga-800">
            <Nav @open-settings="showSettingsModal = true" />
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

        <SettingsModal :show="showSettingsModal" @close="showSettingsModal = false" />
    </div>
</template>
