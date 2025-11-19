# 📚 MangaReader - 日漫生肉阅读助手


<p align="center">
专为日语学习者打造的本地化 OCR 工具，助你轻松啃下日文生肉漫画。
<br>
<br>
<a href="#-下载与安装">下载安装</a> •
<a href="#-功能特性">功能特性</a> •
<a href="#-使用指南">使用指南</a> •
<a href="#-开发者指南">开发者指南</a>
</p>

---

## ✨ 功能特性

- **📸 离线 OCR 识别**：基于 AI 模型，无需联网即可精准识别竖排日文漫画
- **✂️ 全局截图**：支持类似 QQ/微信 的截图方式，不仅限于漫画文件，可截取屏幕任意区域
- **🔍 智能分词**：自动将句子拆解为单词，标注假名读音 (Furigana)
- **🌐 多源翻译**：
    - **离线翻译**：支持加载本地翻译模型（需下载）
    - **在线 API**：支持配置 DeepL、Google、百度等 API Key 增强体验
- **🔒 隐私安全**：所有计算均在本地或直接连接官方 API，不会收集您的任何数据

## 📥 下载与安装

前往 Releases 页面 下载最新版本的安装包

- **Windows**: 下载 `.exe` 文件安装
- **Mac/Linux**: (暂不支持)

## 📖 使用指南

本软件支持 **混合模式**，根据您的网络环境和需求自动切换

### 1. 🟢 在线模式

*无需任何配置，开箱即用*
首次识别时，软件会自动从 HuggingFace 下载必要的 OCR 核心组件（约 400MB），请保持网络畅通 下载完成后即可永久离线使用 OCR 功能

### 2. 🟠 完全离线模式

*适合网络环境不佳或需要完全离线环境的用户*

1. 在 Release 页面下载 **「离线模型包 (Model Pack)」**
2. 打开软件设置 -> 点击「📂 打开模型文件夹」
3. 将解压后的模型文件放入对应目录中
4. 重启软件，状态栏显示“离线模型已加载”即配置成功

### 3. ⚙️ 高级设置

软件支持定制化，您可以在设置中：

- 填入 DeepL / Google API Key 以获得更精准的翻译
- 开启/关闭分词功能
- 自定义截图快捷键

---

## 🧑‍💻 开发者指南

如果你想参与贡献，请参考以下信息

### 🛠 技术栈

| 模块 | 技术选型 |
| --- | --- |
| **Core** | Electron + Vue 3 (Nuxt 4) |
| **UI** | Tailwind CSS |
| **OCR Service** | Python + PyTorch |
| **Model** | Manga-OCR (Transformers) |

### ⚡ 本地开发

- Node.js 18+
- Python 3.8+

### 📁 项目结构

```
MangaReader/
├── app/                # Nuxt 4 前端源码 (Vue组件, 页面)
├── electron/           # Electron 主进程 (Node.js)
├── ocr-service/        # Python OCR 服务端
│   ├── ocr_service.py  # 核心识别脚本
│   └── ocr-model/      # 本地模型存放处 (已忽略)
├── public/             # 静态资源
└── package.json
```

## 📄 开源协议

本项目采用 MIT License 开源
模型文件版权归原作者所有 ([manga-ocr](https://github.com/kha-white/manga-ocr) based on Kha-White work).
