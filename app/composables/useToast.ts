// composables/useToast.ts
interface ToastMessage {
    id: number
    text: string
    duration: number
}

const toasts = ref<ToastMessage[]>([])
let toastId = 0

export const useToast = () => {
    const showToast = (text: string, duration = 1500) => {
        const id = toastId++
        // 新的 toast 插入到数组开头（最上方）
        toasts.value.unshift({ id, text, duration })

        setTimeout(() => {
            // 直接删除，Vue 的 TransitionGroup 会自动处理离开动画
            toasts.value = toasts.value.filter(t => t.id !== id)
        }, duration)
    }

    return {
        toasts: readonly(toasts),
        showToast
    }
}
