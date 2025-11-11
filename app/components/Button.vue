<!-- app/components/Button.vue -->
<script setup lang="ts">
interface Prop {
    variant?: 'primary' | 'secondary'
    size?: 'sm' | 'md' | 'lg'
}
const { variant = 'primary', size = 'md' } = defineProps<Prop>()

const getButtonClass = () => {
    const variantClass = variant === 'primary'
        ? 'px-4 py-2 bg-primary rounded-primary'
        : 'px-3 py-1.5 bg-manga-400 rounded-secondary'

    const sizeClass = size === 'sm'
        ? 'text-sm'
        : size === 'lg'
            ? 'text-lg'
            : 'text-base'

    return `${variantClass} ${sizeClass}`
}
</script>

<template>
    <button
        class="rounded transition-all duration-200 text-white cursor-pointer disabled:cursor-not-allowed hover:opacity-90 hover:-translate-y-px hover:shadow-base"
        :class="getButtonClass()">
        <slot />
    </button>
</template>
