<!-- components/ImageUpload.vue -->
<script setup lang="ts">
// 当前显示的图片 URL（通过 URL.createObjectURL 创建）
const currentImage = ref<string | null>(null)

// 模板引用：拖拽区域和图片容器
const dropArea = useTemplateRef<HTMLDivElement>('dropArea')
const imageContainer = useTemplateRef<HTMLDivElement>('imageContainer')

// 拖拽状态标识（用于视觉反馈）
const isDragging = ref(false)

// 图片容器的宽高
const containerSize = ref({ width: 0, height: 0 })

watch(currentImage, () => {
    console.log(111)

    nextTick(() => {
        if (currentImage.value && imageContainer.value) {
            if (imageContainer.value) {
                const rect = imageContainer.value.getBoundingClientRect()
                containerSize.value = {
                    width: rect.width,
                    height: rect.height
                }
            }
        }
    })
})

const handleDragOver = (event: Event) => {
    // 阻止默认行为（避免浏览器打开文件）和事件冒泡
    event.preventDefault()
    event.stopPropagation()
}

const handleFileSelect = (event: Event) => {
    const input = event.target as HTMLInputElement
    const file = input.files?.[0] // 获取第一个文件

    // 验证文件类型是否为图片
    if (file && file.type.startsWith('image/')) {
        // 创建临时 URL 用于预览（不需要上传到服务器）
        // URL.createObjectURL 会在内存中创建一个临时 blob:// URL
        currentImage.value = URL.createObjectURL(file)
    }

    // 清空 input.value，允许用户重复选择同一文件
    // 如果不清空，选择相同文件不会触发 change 事件
    input.value = ''
}

const handleDragEnter = (event: DragEvent) => {

    isDragging.value = true
}

const handleDragLeave = (event: DragEvent) => {
    const relatedTarget = event.relatedTarget as HTMLElement

    if (dropArea.value && !dropArea.value.contains(relatedTarget)) {
        // 模板引用的类型守卫
        isDragging.value = false
    }

}

const handleDrop = (event: DragEvent) => {
    console.log('留下了文件')
    event.preventDefault() // 阻止浏览器默认打开文件
    isDragging.value = false

    // 从 dataTransfer 中获取拖拽的文件 
    const file = event.dataTransfer?.files?.[0]

    // 验证文件类型
    if (file && file.type.startsWith('image/')) {
        // 创建预览 URL（与点击选择相同）
        currentImage.value = URL.createObjectURL(file)
    }
}

const handleScreenshot = () => { console.log(`handleScreenshot`) }
</script>

<template>
    <div ref="dropArea" @dragover="handleDragOver" @dragenter="handleDragEnter" @dragleave="handleDragLeave"
        @drop="handleDrop"
        class="p-4 transition-all duration-200 shadow-base border rounded-primary hover:shadow-card hover:-translate-y-0.5 h-full flex items-center justify-center bg-manga-50 dark:bg-manga-700"
        :class="isDragging ? 'border-primary border-2' : 'border-manga-200 dark:border-manga-500'">

        <!-- 有图片时显示 -->
        <div v-if="currentImage" ref="imageContainer" class="h-full w-full flex items-center justify-center ">
            <img :src="currentImage" alt="预览图片" class="object-contain size-auto" :style="{
                maxWidth: containerSize.width + 'px',
                maxHeight: containerSize.height + 'px'
            }" />
            <!-- 由于 tailwind 的 JIT 模式 使用:class 并不能生效 故这里使用内联css -->
        </div>

        <!-- 空状态（无图片时显示） -->
        <div v-else class="text-center">
            <div class="text-6xl mb-4">{{ isDragging ? '' : '📥' }}</div>
            <p class="text-lg mb-2 text-manga-900 dark:text-manga-100">
                {{ isDragging ? '松开鼠标上传' : '图片预览区域' }}
            </p>
            <p class="text-sm mb-6 text-manga-600 dark:text-manga-400">拖拽图片到此处</p>

            <div class="flex gap-3 justify-center">
                <label class="inline-block cursor-pointer">
                    <div
                        class="text-base transition-all duration-200 text-white cursor-pointer hover:opacity-90 hover:-translate-y-px hover:shadow-base px-4 py-2 bg-primary rounded-primary">
                        📁 选择图片
                    </div>
                    <!-- accept="image/*": 只接受图片文件 label标签不包裹button防止无法触发 -->
                    <input type="file" accept="image/*" @change="handleFileSelect" class="hidden">
                </label>

                <Button variant="secondary" @click="handleScreenshot">✂️ 截图</Button>
            </div>
        </div>
    </div>
</template>
