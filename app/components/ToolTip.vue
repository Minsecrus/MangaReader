<!-- ToolTip.vue -->
<script setup lang="ts">
interface Props {
    showTime: number
}
const { showTime = 1500 } = defineProps<Props>()

const show = ref(false)

onMounted(() => {
    show.value = true
    setTimeout(() => {
        show.value = false
    }, showTime)
})
</script>

<template>
    <Transition name="text-fade">
        <div v-if="show"
            class="absolute top-4 left-1/2 -translate-x-1/2 bg-black/80 text-white px-4 py-2 rounded-lg text-sm backdrop-blur-sm shadow-lg pointer-events-none">
            <slot>ToolTip</slot>
        </div>
    </Transition>
</template>

<style scoped>
.text-fade-enter-active,
.text-fade-leave-active {
    transition: all 300ms ease-in-out;
}

.text-fade-enter-from,
.text-fade-leave-to {
    transform: translateY(-6px);
    opacity: 0;
}

.text-fade-enter-to,
.text-fade-leave-from {
    opacity: 1;
}
</style>