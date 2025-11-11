<!-- app/components/TokenizedWords.vue -->
<script setup lang="ts">
interface Token {
    word: string
    type?: 'noun' | 'verb' | 'particle' | 'adjective' | 'other'
}

interface Props {
    originText: string
}

const { originText } = defineProps<Props>()

// 分词结果状态
const tokens = ref<Token[]>([])
const isTokenizing = ref(false)
let debounceTimer: ReturnType<typeof setTimeout> | null = null

// 分词 API 调用函数
const tokenizeText = async (text: string) => {
    if (!text.trim()) {
        tokens.value = []
        return
    }

    isTokenizing.value = true

    try {
        // 这里调用实际的分词 API
        console.log('开始分词:', text)

        // 模拟 API 调用延迟
        await new Promise(resolve => setTimeout(resolve, 500))

        // 模拟 API 返回结果
        tokens.value = [
            { word: '今日', type: 'noun' },
            { word: 'は', type: 'particle' },
            { word: 'いい', type: 'adjective' },
            { word: '天気', type: 'noun' },
            { word: 'です', type: 'verb' },
            { word: 'ね', type: 'particle' },
        ]
    } catch (error) {
        console.error('分词失败:', error)
        tokens.value = []
    } finally {
        isTokenizing.value = false
    }
}

// 监听 originText 变化，使用防抖策略
watch(() => originText, (newText) => {
    // 清除之前的定时器
    if (debounceTimer) {
        clearTimeout(debounceTimer)
    }

    // 如果文本为空，立即清空分词结果
    if (!newText.trim()) {
        tokens.value = []
        isTokenizing.value = false
        return
    }

    // 显示加载状态
    isTokenizing.value = true

    // 这里未来让用户自己进行设置修改
    debounceTimer = setTimeout(() => {
        tokenizeText(newText)
    }, 600)
}, { immediate: true })

// 组件卸载时清理定时器
onUnmounted(() => {
    if (debounceTimer) {
        clearTimeout(debounceTimer)
    }
})

</script>

<template>
    <div class="card">
        <div class="text-xs font-semibold mb-3 text-manga-600 dark:text-manga-400">
            🔤 分词结果
        </div>

        <!-- 加载状态 -->
        <div v-if="isTokenizing" class="flex items-center gap-2 text-manga-600 dark:text-manga-400">
            <div class="animate-spin h-4 w-4 border-2 rounded-full border-primary border-t-transparent"></div>
            <span class="text-sm">分词中...</span>
        </div>

        <!-- 分词结果 -->
        <div v-else-if="tokens.length > 0" class="flex gap-2 flex-wrap">
            <TokenButton v-for="(token, index) in tokens" :key="index" :word="token.word" :type="token.type" />
        </div>

        <!-- 空状态 没有在等待API同时tokens.length长度小于等于0 -->
        <div v-else class="text-sm text-manga-600 dark:text-manga-400">
            分词结果将显示在这里...
        </div>

        <!-- 图例 -->
        <!-- <div class="mt-3 pt-3 border-t border-manga-200 dark:border-manga-600 flex gap-3 flex-wrap text-xs">
			<div class="flex items-center gap-1">
				<div class="w-3 h-3 rounded bg-manga-400"></div>
				<span class="text-manga-600 dark:text-manga-400">名词</span>
			</div>
			<div class="flex items-center gap-1">
				<div class="w-3 h-3 rounded bg-primary"></div>
				<span class="text-manga-600 dark:text-manga-400">动词</span>
			</div>
			<div class="flex items-center gap-1">
				<div class="w-3 h-3 rounded bg-manga-500"></div>
				<span class="text-manga-600 dark:text-manga-400">助词</span>
			</div>
			<div class="flex items-center gap-1">
				<div class="w-3 h-3 rounded bg-secondary"></div>
				<span class="text-manga-600 dark:text-manga-400">形容词</span>
			</div>
		</div> -->
    </div>
</template>
