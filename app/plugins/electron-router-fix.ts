export default defineNuxtPlugin((nuxtApp) => {
    const router = useRouter()

    // 在路由解析之前拦截
    router.beforeEach((to, from, next) => {
        // 检查是否是 Electron 的文件路径路由
        // 例如: /E:/VS%20code/.../index.html
        if (to.fullPath.includes('index.html') || to.fullPath.includes(':')) {
            console.log('🚨 [Plugin] Detected file path route, redirecting to /')
            return next('/')
        }
        next()
    })
})
