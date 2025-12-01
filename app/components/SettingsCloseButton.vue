<!-- compos/SettingsCloseButton.vue -->
<script setup lang="ts">
const emit = defineEmits<{
    settingsCloseBtnClick: []
}>()
</script>

<template>
    <button @click="emit('settingsCloseBtnClick')"
        class="p-1 rounded-full text-manga-400 hover:bg-manga-100 dark:hover:bg-manga-700 hover:text-manga-600 transition-colors cursor-pointer">
        <IconClose class="size-5" />
    </button>
</template>
