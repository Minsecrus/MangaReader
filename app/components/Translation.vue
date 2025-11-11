<!-- app/components/Translation.vue -->
<script setup lang="ts">
interface Prop {
    originalText: string
}
const { originalText } = defineProps<Prop>()
const isTranslationLoading = ref(false)
const translatedText = ref<string | null>(null)
const hasFirstTranslated = ref(false) // 是否已经进行过第一次翻译

const showTranslation = ref(false)

const handleRetranslate = async () => {
    translatedText.value = null // 清空之前的翻译结果
    await handleTranslate() // 调用翻译函数重新翻译
}

const handleTranslate = async () => {
    isTranslationLoading.value = true
    if (!translatedText.value) {
        hasFirstTranslated.value = true // 标记已经进行过第一次翻译
        // 只有第一次翻译时(translatedText不存在取反为true)才调用API 如果translatedText已经存在就不再调用 避免重复调用API
        // 调用翻译 API 使用 prop 传递过来的 originalText
        console.log(originalText) // 这里模拟调用API使用originalText
        // isTranslationLoading.value = false
        // 这里仍然要看API怎么用时再来处理isTranslationLoading问题

        // -----------
        setTimeout(() => {
            // 这里模拟翻译延迟 实际情况看API调用结果 假设1s后API返回结果
            translatedText.value = '今天天气真好呢。一边看漫画一边学习日语。' // 这里替换为实际API返回的翻译结果

            isTranslationLoading.value = false
        }, 1000)
        // -----------
    }
    else {
        // 如果translatedText已经存在 直接设置加载状态为false
        isTranslationLoading.value = false
    }
}

const toggleTranslation = async () => {
    await handleTranslate()
    showTranslation.value = !showTranslation.value
}
</script>

<template>
    <div class="card">
        <div class="flex items-center justify-between mb-3">
            <div class="text-xs font-semibold text-manga-600 dark:text-manga-400">
                🌐 翻译
            </div>
            <CopyButton v-if="showTranslation && translatedText" :textToCopy="translatedText" />
        </div>

        <!-- 翻译内容 -->
        <Transition name="fade">
            <!-- showTranslation为true就显示 之后若isTranslationLoading为true反之判断translatedText 存在的话就显示它 否则就显示'暂无翻译' -->
            <div v-if="showTranslation">
                <div v-if="isTranslationLoading" class="flex items-center gap-2 text-manga-600 dark:text-manga-400">
                    <div class="animate-spin h-4 w-4 border-2 rounded-full border-primary border-t-transparent"></div>
                    <span class="text-sm">翻译中...</span>
                </div>

                <p v-else-if="translatedText" class="text-sm leading-relaxed text-manga-900 dark:text-manga-100">
                    {{ translatedText }}
                </p>

                <p v-else class="text-sm text-manga-600 dark:text-manga-400">
                    暂无翻译
                </p>
            </div>
        </Transition>

        <!-- 操作按钮 -->
        <div class="mt-3 flex gap-2">
            <Button size="sm" @click="toggleTranslation" :disabled="isTranslationLoading">
                {{ showTranslation ? "隐藏" : "显示" }}翻译
            </Button>

            <Button v-if="hasFirstTranslated" variant="secondary" size="sm" @click="handleRetranslate">
                <!-- 如果 hasFirstTranslated 为 true已经进行了第一次翻译 就显示重新翻译按钮 点击就重新调用一次API -->
                重新翻译
            </Button>
        </div>
    </div>
</template>

<style scoped>
.fade-enter-active,
.fade-leave-active {
    transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
    opacity: 0;
}
</style>
