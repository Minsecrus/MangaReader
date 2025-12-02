<!-- components/GlobalLoader.vue -->
<script setup lang="ts">
const { showToast } = useToast()
const isVisible = ref(true)
const isFading = ref(false) // 控制消失动画
const loadingText = ref('Initializing...')
const downloadPercent = ref(0) // 下载进度

const emit = defineEmits<{
    ready: []
}>()

// 监听后端状态
onMounted(async () => {
    window.electronAPI.on('backend-status', (data) => {
        console.log('Loader received signal:', data)
        if (data.status === 'ready') {
            finishLoading()
        }
    })
    window.electronAPI.onInitStatus((message: string) => {
        loadingText.value = message
    })

    // 监听初始化下载进度
    window.electronAPI.onInitProgress((data: { percent: number, message: string }) => {
        loadingText.value = `${data.message} (${data.percent}%)`
        downloadPercent.value = data.percent
    })

    const isReady = await window.electronAPI.checkBackendReady()
    if (isReady) {
        loadingText.value = "Welcome Back!"
        finishLoading()
    }
    // 超时强制显示 防止后端挂了
    setTimeout(() => {
        if (isVisible.value) {
            console.warn('Loader: Timeout triggered (Backend slow or failed)')
            finishLoading()
        }
    }, 300000)
})

const finishLoading = () => {
    isFading.value = true
    // 等待 fade-out 动画结束 (500ms)
    setTimeout(() => {
        isVisible.value = false
        emit('ready')
        showToast('资源加载完毕 🚀', 2000)
    }, 500)
}
</script>

<template>
    <!-- 全屏遮罩 -->
    <!-- 使用 Teleport 确保它永远在最上层 -->
    <Teleport to="body">
        <Transition enter-active-class="transition duration-300"
            leave-active-class="transition duration-500 ease-in-out" leave-to-class="opacity-0 blur-sm scale-105">
            <div v-if="isVisible"
                class="fixed inset-0 z-9999 flex flex-col items-center justify-center bg-manga-50 dark:bg-manga-800 transition-colors"
                :class="{ 'pointer-events-none': isFading }">
                <!-- 动画容器 -->
                <div class="loader-container mb-8">
                    <!-- 跳跃的 あ -->
                    <div class="jumping-char text-4xl font-black text-primary dark:text-blue-400 select-none">
                        あ
                    </div>
                </div>

                <!-- 文字提示 -->
                <div class="text-center space-y-2 w-full max-w-md px-4">
                    <h2 class="text-xl font-bold text-manga-900 dark:text-white tracking-widest animate-pulse">
                        MANGA READER
                    </h2>
                    <p class="text-sm text-manga-500 dark:text-manga-400 font-mono truncate">
                        {{ loadingText }}
                    </p>

                    <!-- 进度条 (仅在下载时显示) -->
                    <div v-if="downloadPercent > 0 && downloadPercent < 100"
                        class="w-full h-1.5 bg-manga-200 dark:bg-manga-700 rounded-full overflow-hidden mt-2">
                        <div class="h-full bg-primary transition-all duration-300 ease-out"
                            :style="{ width: `${downloadPercent}%` }"></div>
                    </div>
                </div>
            </div>
        </Transition>
    </Teleport>
</template>

<style scoped>
.loader-container {
    position: relative;
    width: 120px;
    height: 90px;
}

/* 1. 跳跃的 あ (对应原来的 loader:before) */
.jumping-char {
    position: absolute;
    bottom: 30px;
    left: 45px;
    /* 微调居中 */
    width: 40px;
    height: 40px;
    display: flex;
    align-items: center;
    justify-content: center;

    /* 动画：跳跃 + 形变 */
    animation: jump-bounce 0.5s ease-in-out infinite alternate;
}

/* 2. 滚动的台阶 (对应原来的 loader:after) */
/* 使用伪元素画出台阶阴影 */
.loader-container::after {
    content: "";
    position: absolute;
    right: 0;
    top: 0;
    height: 7px;
    width: 45px;
    border-radius: 4px;
    /* 初始状态的阴影 */
    box-shadow: 0 5px 0 #cbd5e1, -35px 50px 0 #cbd5e1, -70px 95px 0 #cbd5e1;
    animation: step-scroll 1s ease-in-out infinite;
}

/* 深色模式适配 */
:global(.dark) .loader-container::after {
    box-shadow: 0 5px 0 #475569, -35px 50px 0 #475569, -70px 95px 0 #475569;
    animation: step-scroll-dark 1s ease-in-out infinite;
}

/* --- 关键帧定义 --- */

@keyframes jump-bounce {
    0% {
        transform: scale(1, 0.7);
        /* 落地压扁 */
        bottom: 30px;
    }

    40% {
        transform: scale(0.8, 1.2);
        /* 起跳拉长 */
    }

    60% {
        transform: scale(1, 1);
    }

    100% {
        bottom: 120px;
        /* 跳到的最高点 */
        transform: scale(1, 1);
    }
}

/* 浅色模式台阶动画 */
@keyframes step-scroll {
    0% {
        box-shadow: 0 10px 0 rgba(0, 0, 0, 0), 0 10px 0 #cbd5e1, -35px 50px 0 #cbd5e1, -70px 90px 0 #cbd5e1;
    }

    100% {
        box-shadow: 0 10px 0 #cbd5e1, -35px 50px 0 #cbd5e1, -70px 90px 0 #cbd5e1, -70px 90px 0 rgba(0, 0, 0, 0);
    }
}

/* 深色模式台阶动画 (颜色不同) */
@keyframes step-scroll-dark {
    0% {
        box-shadow: 0 10px 0 rgba(0, 0, 0, 0), 0 10px 0 #475569, -35px 50px 0 #475569, -70px 90px 0 #475569;
    }

    100% {
        box-shadow: 0 10px 0 #475569, -35px 50px 0 #475569, -70px 90px 0 #475569, -70px 90px 0 rgba(0, 0, 0, 0);
    }
}
</style>
