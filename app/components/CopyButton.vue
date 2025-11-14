<!-- app/components/CopyButton.vue -->
<script setup lang="ts">
const buttonText = ref('复制')
let timeoutId: NodeJS.Timeout | null = null
// 接收一个父级传递过来的text来实现点击按钮复制
interface Prop {
    textToCopy: string
}
const { textToCopy } = defineProps<Prop>()

const copyText = async () => {
    if (timeoutId) {
        clearTimeout(timeoutId)
    }
    try {
        await window.navigator.clipboard.writeText(textToCopy)
        buttonText.value = '已复制'
    } catch (err) {
        buttonText.value = '复制失败'
        console.error('复制失败:', err)
    } finally {
        timeoutId = setTimeout(() => {
            buttonText.value = '复制'
        }, 1500)
    }
}
</script>

<template>
    <button class="text-xs px-2 py-1 rounded cursor-pointer transition-all hover:opacity-80 bg-manga-400 text-white"
        @click="copyText">
        {{ buttonText }}
    </button>
</template>
