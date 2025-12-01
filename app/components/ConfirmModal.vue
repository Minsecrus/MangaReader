<!-- components/ConfirmModal.vue -->
<script setup lang="ts">
interface Props {
    show: boolean // 外部控制显示隐藏状态的布尔值
    title?: string // 标题
    content?: string // 内容
    confirmText?: string // 确认按钮的内容
    cancelText?: string // 取消按钮的内容
    isDanger?: boolean // 是否是危险操作（如果是，按钮变红）
    loading?: boolean  // 是否正在处理中
}

const {
    title = '确认操作',
    content = '你确定要执行此操作吗？',
    confirmText = '确定',
    cancelText = '取消',
    isDanger = false,
    loading = false
} = defineProps<Props>()

const emit = defineEmits<{
    confirm: []
    cancel: []
}>()
</script>

<template>
    <Teleport to="body">
        <Transition enter-active-class="transition duration-200 ease-out"
            leave-active-class="transition duration-150 ease-in" enter-from-class="opacity-0" leave-to-class="opacity-0"
            enter-to-class="opacity-100" leave-from-class="opacity-100">

            <!-- 遮罩层 -->
            <div v-if="show" class="fixed inset-0 z-60 flex items-center justify-center bg-black/50 backdrop-blur-sm"
                @click="emit('cancel')">

                <!-- 弹窗卡片 (阻止点击冒泡) -->
                <div class="w-full max-w-sm bg-white dark:bg-manga-800 rounded-xl shadow-2xl p-6 transform transition-all scale-100 border border-manga-200 dark:border-manga-700"
                    @click.stop>

                    <!-- 标题与图标 -->
                    <div class="flex items-start gap-4 mb-4">
                        <div class="shrink-0 flex items-center justify-center w-10 h-10 rounded-full"
                            :class="isDanger ? 'bg-red-100 text-red-600 dark:bg-red-900/30 dark:text-red-400' : 'bg-blue-100 text-blue-600'">
                            <IconWarn v-if="isDanger" class="size-6" />
                            <IconTip v-else class="w-6 h-6" />
                        </div>
                        <div>
                            <h3 class="text-lg font-bold text-manga-900 dark:text-white">
                                {{ title }}
                            </h3>
                            <p class="text-sm text-manga-500 dark:text-manga-400 mt-1">
                                {{ content }}
                            </p>
                        </div>
                    </div>

                    <!-- 按钮组 -->
                    <div class="flex justify-end gap-3 mt-6">
                        <button @click="emit('cancel')" :disabled="loading"
                            class="px-4 py-2 text-sm font-medium text-manga-600 dark:text-manga-300 bg-white dark:bg-manga-800 border border-manga-300 dark:border-manga-600 rounded-lg hover:bg-manga-50 dark:hover:bg-manga-700 focus:outline-none transition-colors cursor-pointer">
                            {{ cancelText }}
                        </button>

                        <button @click="emit('confirm')" :disabled="loading"
                            class="px-4 py-2 text-sm font-medium text-white rounded-lg shadow-sm focus:outline-none transition-all flex items-center gap-2 cursor-pointer"
                            :class="[
                                isDanger
                                    ? 'bg-red-600 hover:bg-red-700 dark:bg-red-600 dark:hover:bg-red-500'
                                    : 'bg-blue-600 hover:bg-blue-700',
                                loading ? 'opacity-70 cursor-not-allowed' : ''
                            ]">
                            <span v-if="loading"
                                class="animate-spin h-3 w-3 border-2 border-white border-t-transparent rounded-full"></span>
                            {{ confirmText }}
                        </button>
                    </div>
                </div>
            </div>
        </Transition>
    </Teleport>
</template>
