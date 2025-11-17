<!-- OcrButton.vue -->
<script setup lang="ts">

const emit = defineEmits<{
    ocrBtnClick: []
}>()
</script>

<template>
    <button @click="emit('ocrBtnClick')"
        class="card text-manga-600 dark:text-manga-200 w-full h-12 flex items-center justify-center font-bold text-xl cursor-pointer relative overflow-hidden group border border-manga-300 dark:border-manga-500 transition-all duration-300 hover:bg-manga-200 dark:hover:bg-manga-600">
        <span class="relative z-10 transition-all duration-300 group-hover:text-transparent translate-x-3">OCR</span>
        <span
            class="absolute right-0 h-full w-10 bg-manga-300 dark:bg-manga-500 flex items-center justify-center transition-all duration-300 group-hover:w-full group-hover:translate-x-0 translate-x-0 group-active:bg-manga-400 dark:group-active:bg-manga-700">
            <IconOcr class="relative z-10" />
        </span>
    </button>
</template>
