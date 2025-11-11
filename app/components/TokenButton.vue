<!-- app/components/TokenButton.vue -->
<script setup lang="ts">
type TokenType = 'noun' | 'verb' | 'particle' | 'adjective' | 'other'
interface Prop {
    word: string
    type?: TokenType
}

const { word, type = 'other' } = defineProps<Prop>()

const getTokenClasses = (tokenType: TokenType) => {
    switch (tokenType) {
        case 'noun':
            return 'bg-manga-400 text-white'
        case 'verb':
            return 'bg-primary text-white'
        case 'particle':
            return 'bg-manga-500 text-white'
        case 'adjective':
            return 'bg-secondary text-white'
        default:
            return 'bg-manga-400 text-white'
    }
}

const handleClick = () => {
    // 这里未来可以添加一些其他的功能
    console.log(word)
}
</script>

<template>
    <button
        class="px-3 py-1.5 rounded text-sm font-medium transition-all hover:scale-105 cursor-pointer font-ja leading-[1.8]"
        :class="getTokenClasses(type)" @click="handleClick">
        {{ word }}
    </button>
</template>
