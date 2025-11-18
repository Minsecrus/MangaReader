<!-- components/OcrOverlay.vue -->
<script setup lang="ts">
interface SelectionArea {
    startX: number
    startY: number
    endX: number
    endY: number
}

const emit = defineEmits<{
    captureComplete: [
        selectionData: {
            left: number
            top: number
            width: number
            height: number
        }
    ]
    cancel: []
}>()

const overlayRef = useTemplateRef<HTMLDivElement>('overlayRef')
const isSelecting = ref(false)
const selection = ref<SelectionArea>({
    startX: 0,
    startY: 0,
    endX: 0,
    endY: 0
})

const selectionStyle = computed(() => {
    // 计算属性 用于不断更新框选的样式
    const left = Math.min(selection.value.startX, selection.value.endX)
    const top = Math.min(selection.value.startY, selection.value.endY)
    const width = Math.abs(selection.value.endX - selection.value.startX)
    const height = Math.abs(selection.value.endY - selection.value.startY)

    return {
        left: `${left}px`,
        top: `${top}px`,
        width: `${width}px`,
        height: `${height}px`
    }
})

const handleMouseDown = (event: MouseEvent) => {
    // 鼠标按下时 把鼠标的位置赋值给start end
    isSelecting.value = true
    selection.value.startX = event.clientX
    selection.value.startY = event.clientY
    selection.value.endX = event.clientX
    selection.value.endY = event.clientY
}

const handleMouseMove = (event: MouseEvent) => {
    if (!isSelecting.value) return
    selection.value.endX = event.clientX
    selection.value.endY = event.clientY
}

const handleMouseUp = () => {
    if (!isSelecting.value) return
    isSelecting.value = false

    // 鼠标抬起的时间计算这个区域的坐标 以及 宽高
    const left = Math.min(selection.value.startX, selection.value.endX)
    const top = Math.min(selection.value.startY, selection.value.endY)
    const width = Math.abs(selection.value.endX - selection.value.startX)
    const height = Math.abs(selection.value.endY - selection.value.startY)

    // 传递选区坐标,由父组件处理截图
    emit('captureComplete', { left, top, width, height })

    console.log(isSelecting.value || (selection.value.endX !== selection.value.startX && selection.value.endY !== selection.value.startY))
}

const handleCancel = () => {
    emit('cancel')
}

// ESC 取消
onMounted(() => {
    // 注册一个 esc 的全局快捷键
    const handleEsc = (e: KeyboardEvent) => {
        if (e.key === 'Escape') {
            handleCancel()
        }
    }
    window.addEventListener('keydown', handleEsc)
    onUnmounted(() => {
        window.removeEventListener('keydown', handleEsc)
    })
})
</script>

<template>
    <div ref="overlayRef" class="fixed inset-0 z-50 cursor-crosshair" @mousedown="handleMouseDown"
        @mousemove="handleMouseMove" @mouseup="handleMouseUp">
        <!-- 选择框 进入了select模式 或者 鼠标框选出了一个方形区域 => true才显示  -->
        <div v-if="isSelecting || (selection.endX !== selection.startX && selection.endY !== selection.startY)"
            class="absolute border-2 border-primary bg-primary/10 pointer-events-none" :style="selectionStyle">
        </div>

        <!-- 提示文字 -->
        <ToolTip :show-time="1500">
            🖱️ 拖动鼠标框选识别区域 · 按 ESC 取消
        </ToolTip>
    </div>
</template>
