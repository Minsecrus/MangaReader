<!-- app/components/CopyButton.vue -->
<script setup lang="ts">
// 接收一个父级传递过来的text来实现点击按钮复制
interface Prop {
    textToCopy: string
}
const { textToCopy } = defineProps<Prop>()

const copyText = async () => {
    try {
        await window.navigator.clipboard.writeText(textToCopy)
    } catch (err) {
        console.error('复制失败:', err)
    }
}
</script>

<template>
    <button class="text-xs px-2 py-1 rounded cursor-pointer transition-all hover:opacity-80 bg-manga-400 text-white" @click="copyText">
        复制
    </button>
</template>
