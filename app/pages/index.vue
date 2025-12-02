<!-- app/pages/index.vue -->
<script setup lang="ts">
// 原文显示板块 使用 v-model 双向绑定
const originalText = ref('今日はいい天気ですね。漫画を読みながら日本語を勉強します。')
const showSettingsModal = ref(false) // settingModal显示
const isOcrMode = ref(false) // ocr模式 鼠标十字crosshair
const isOcrRecognizing = ref(false) // 正在调用模型识别
const { showToast } = useToast()

const handleOcr = () => {
    // 启动ocr时显示一个tooltip提示
    showToast('🖱️ 拖动鼠标框选识别区域 · 按 ESC 取消', 1500)

    // 激活 OCR 模式，显示框选 overlay
    isOcrMode.value = true
}

const { initSettings, settings } = useSettings()

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
            showToast(`OCR 识别失败: ${result.error}`)
        }

    } catch (error) {
        console.error('OCR 处理错误:', error)
        showToast(`OCR 处理错误: ${error}`, 5000)
    } finally {
        isOcrRecognizing.value = false
    }
}

const handleOcrCancel = () => {
    // 用户主动按下esc推出ocr模式
    isOcrMode.value = false
}

const handleAppReady = () => {
    console.log('App Ready! Triggering initial translation...')

    // 这里不需要手动调翻译 API，因为 originalText 的值本身就没变。
    // 但是，Translation 组件是 watch immediate 的。
    // 当 Loader 存在时，Translation 组件其实已经加载并在后台跑了一次翻译了。
    // 为了让用户有“加载好了”的感觉，我们可以在这里做点别的，或者什么都不做，
    // 因为 Translation 组件会在后台默默把那句日语翻译好，等 Loader 一消失，用户看到的就是翻译好的结果。

    // 如果你想强制刷新一下：
    const temp = originalText.value
    originalText.value = ''
    nextTick(() => originalText.value = temp)
}

onMounted(() => {
    initSettings()

    // 监听来自 Electron 的快捷键信号
    if (window.electronAPI) {
        // 当快捷键按下 -> 执行 handleOcr (和点击按钮效果一样)
        const cleanup = window.electronAPI.onShortcutTriggered(() => {
            console.log('Vue 收到快捷键信号，启动 OCR')
            // 只有当前不在 OCR 模式，且不在识别中才启动
            if (!isOcrMode.value && !isOcrRecognizing.value) {
                handleOcr()
            }
        })

        // 页面卸载时清理监听 (虽然 index.vue 通常不卸载，但这是好习惯)
        onUnmounted(() => {
            cleanup()
        })
    }
})
</script>

<template>
    <div class="min-h-screen bg-manga-50 dark:bg-manga-700">
        <GlobalLoader @ready="handleAppReady" />

        <!-- 全局 Toast 容器 -->
        <ToastContainer />

        <!-- 自定义标题栏 -->
        <TitleBar @open-settings="showSettingsModal = true" />
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
                    <TokenizedWords v-if="settings.enableTokenization" :origin-text="originalText" />
                    <Translation v-if="settings.enableTranslation" :original-text="originalText" />
                    <HintCard v-if="settings.enableTokenization" text="提示：点击分词结果中的单词可查看详情" />
                </div>
            </div>
        </main>

        <SettingsModal :show="showSettingsModal" @close="showSettingsModal = false" />
    </div>
</template>
