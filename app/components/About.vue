<!-- compos/About.vue -->
<script setup lang="ts">
const config = {
    github: 'https://github.com/MalloyManga/MangaReader',
    portfolioWebsite: 'https://malloymanga.github.io/',
    website: '#',
    appVersion: 'v0.1.0',
    currentYear: 2025,
}

const openLink = (url: string) => {
    // 调用 Electron 的 shell 打开浏览器
    window.electronAPI.openLink(url)
}
</script>

<template>
    <div class="pt-6 mt-2 border-t border-manga-100 dark:border-manga-700">
        <h3 class="text-sm font-medium text-manga-500 dark:text-manga-400 uppercase mb-3 px-1">
            👨‍💻 关于 & 开发者
        </h3>

        <div
            class="bg-manga-50 dark:bg-manga-900/50 p-4 rounded-xl border border-transparent hover:border-manga-200 dark:hover:border-manga-600 hover:bg-manga-100 dark:hover:bg-manga-800 transition-all duration-200 group">

            <div class="flex items-start justify-between">
                <div class="flex gap-3">
                    <div
                        class="w-10 h-10 rounded-lg bg-linear-to-br from-primary to-blue-400 flex items-center justify-center text-lg text-white shadow-sm shrink-0">
                        📖
                        <!-- Image -->
                    </div>

                    <div class="flex flex-col">
                        <div class="flex items-baseline gap-2">
                            <span class="font-bold text-manga-900 dark:text-white text-sm">Manga Reader</span>
                            <span
                                class="text-[10px] font-mono text-manga-400 bg-white dark:bg-manga-800 px-1.5 py-0.5 rounded border border-manga-100 dark:border-manga-700">
                                {{ config.appVersion }}
                            </span>
                        </div>

                        <div class="text-xs text-manga-500 dark:text-manga-400 mt-0.5">
                            Developed by
                            <span @click="openLink(config.portfolioWebsite)"
                                class="font-semibold text-manga-700 dark:text-manga-200 underline cursor-pointer">
                                Malloy
                            </span>
                        </div>
                    </div>
                </div>

                <div class="flex gap-2">
                    <!-- 软件官网暂时没有 考虑到一些问题 暂时不做打算 -->
                    <!-- <button @click="openLink(config.website)"
                        class="p-2 rounded-lg text-manga-400 hover:text-primary hover:bg-white dark:hover:bg-manga-700 transition-all cursor-pointer">
                        <IconWebsite />
                    </button> -->
                    <button @click="openLink(config.github)"
                        class="p-2 rounded-lg text-manga-400 hover:text-manga-900 dark:hover:text-white hover:bg-white dark:hover:bg-manga-700 transition-all cursor-pointer">
                        <IconGithub />
                    </button>
                </div>
            </div>

            <div
                class="mt-3 pt-3 border-t border-manga-200/50 dark:border-manga-700/50 flex flex-col sm:flex-row justify-between items-start sm:items-center gap-1">
                <p class="text-[10px] text-manga-400">
                    Copyright © {{ config.currentYear }} Malloy.
                </p>
                <p class="text-[10px] text-manga-400">
                    MIT License · Open Source
                </p>
            </div>

        </div>
    </div>
</template>
