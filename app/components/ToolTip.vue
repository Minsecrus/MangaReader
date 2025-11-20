<!-- ToolTip.vue -->
<script setup lang="ts">
interface Props {
    text: string
    duration: number
}
defineProps<Props>()
</script>

<template>
    <!-- 不再需要内部 Transition，由 TransitionGroup 统一管理 -->
    <div class="bg-black/80 text-white px-5 py-3 rounded-lg text-sm 
        backdrop-blur-sm shadow-lg pointer-events-none select-none
        w-max max-w-sm text-center">
        {{ text }}
    </div>
</template>
