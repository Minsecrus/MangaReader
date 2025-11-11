<!-- app/components/HintCard.vue -->
<script setup lang="ts">
interface Prop {
    text: string
    icon?: string
}

const { text, icon = '💡' } = defineProps<Prop>()
</script>

<template>
    <div class="card">
        <p class="text-xs text-manga-600 dark:text-manga-400">
            {{ icon }} {{ text }}
        </p>
    </div>
</template>
