<!-- components/ToastContainer.vue -->
<script setup lang="ts">
const { toasts } = useToast()
</script>

<template>
    <Teleport to="body">
        <!-- 外层容器：负责定位到屏幕顶部中间，但不参与 Flex 排列 -->
        <div class="fixed top-4 left-0 right-0 z-9999 pointer-events-none flex justify-center">

            <!-- 
                 TransitionGroup: 
                 1. tag="div": 作为一个真实的容器存在
                 2. relative: 为了让内部 absolute 的离开元素以它为基准定位
                 3. flex-col: 垂直排列
                 4. w-full items-center: 确保宽度正常
            -->
            <TransitionGroup name="list" tag="div" class="relative flex flex-col items-center w-full">
                <!-- 注意：这里我们给 ToolTip 加了一个 wrapper 或者直接加样式 -->
                <div v-for="toast in toasts" :key="toast.id" class="transition-all duration-500 ease-in-out mb-3">
                    <ToolTip :text="toast.text" :duration="toast.duration" />
                </div>
            </TransitionGroup>
        </div>
    </Teleport>
</template>

<style scoped>
/* 
   Vue TransitionGroup 动画核心魔法 
   必须同时定义 enter, leave, move
*/

/* 1. 进入动画：从上方滑入，淡入 */
.list-enter-from {
    opacity: 0;
    transform: translateY(-30px);
}

/* 2. 离开动画：原地淡出，稍微缩小 */
.list-leave-to {
    opacity: 0;
    transform: scale(0.8);
}

/* 3. 离开时的布局处理 (最关键的一步！) */
.list-leave-active {
    /* 
       必须 absolute 才能脱离文档流，让下方的元素往上补位。
       但是 absolute 会导致它失去 flex 居中，所以要手动居中。
    */
    position: absolute;

    /* 技巧：在一个 flex-col items-center 的容器里，
       absolute 元素往往会跑偏，或者是宽度塌陷。
       这里我们不控制 left/right，因为外层 div 包裹了它。
       关键是 z-index 设低，别挡住别人。
    */
    z-index: -1;
}

/* 4. 移动动画：其他元素被挤下去/补位时的动画 */
/* Vue 会自动给受影响的元素加上这个类 */
.list-move {
    transition: all 0.5s cubic-bezier(0.55, 0, 0.1, 1);
}
</style>