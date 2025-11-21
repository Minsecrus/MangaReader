// electron/ocr-service.cjs
const { spawn } = require('child_process')
const path = require('path')

class OcrService {
    constructor(modelPath) {
        this.modelPath = modelPath
        this.process = null
        this.isReady = false
        this.pendingRequests = new Map()
        this.requestId = 0
        this.responseBuffer = ''
    }

    start() {
        const isDev = !require('electron').app.isPackaged
        let pythonPath, scriptPath

        if (isDev) {
            // 注意：这里路径根据你的项目结构微调，确保能找到 python.exe
            pythonPath = path.join(__dirname, '../services/venv/Scripts/python.exe') 
            scriptPath = path.join(__dirname, '../services/ocr_service.py')
        } else {
            pythonPath = path.join(process.resourcesPath, 'services/ocr-service.exe')
            scriptPath = null
        }

        const args = []
        if (scriptPath) {
            args.push('-u', scriptPath)
        }

        // 传入模型路径参数
        if (this.modelPath) {
            args.push('--model-dir', this.modelPath)
        }

        console.log('🚀 Starting OCR service...')
        console.log('📂 Model Path:', this.modelPath)

        this.process = spawn(pythonPath, args, {
            stdio: ['pipe', 'pipe', 'pipe'],
            env: {
                ...process.env,
                PYTHONUNBUFFERED: '1',
                PYTHONIOENCODING: 'utf-8',
                // 可以在这里设置 HF 镜像，如果用户在国内
                HF_ENDPOINT: 'https://hf-mirror.com'
            }
        })

        this.process.stdin.setDefaultEncoding('utf-8')
        this.process.stdout.setEncoding('utf-8')
        this.process.stderr.setEncoding('utf-8')

        // 监听日志 (stderr)
        this.process.stderr.on('data', (data) => {
            const msg = data.toString().trim()
            console.log('[OCR Core]', msg)
            // 如果你想在前端显示下载进度，可以通过 ipcMain 发送这个 msg 到前端
        })

        // 监听数据 (stdout)
        this.process.stdout.on('data', (data) => {
            this.responseBuffer += data
            const lines = this.responseBuffer.split('\n')
            this.responseBuffer = lines.pop() || ''

            lines.forEach(line => {
                line = line.trim()
                if (!line) return
                try {
                    const response = JSON.parse(line)
                    this._handleResponse(response)
                } catch (e) {
                    // 忽略非 JSON 输出（虽然 stderr 应该捕获大部分日志，但以防万一）
                }
            })
        })

        this.process.on('error', (err) => console.error('OCR Process Error:', err))
        this.process.on('exit', (code) => {
            console.log(`OCR Process exited: ${code}`)
            this.isReady = false
            this.pendingRequests.forEach(r => r.reject(new Error('OCR Service Exited')))
            this.pendingRequests.clear()
        })
    }

    _handleResponse(response) {
        if (response.status === 'ready') {
            this.isReady = true
            console.log('✅ OCR Service is Ready to accept requests!')
            return
        }

        // 简单的错误处理
        if (response.status === 'error') {
            console.error('❌ OCR Init Error:', response.message)
            return
        }

        const { id, success, text, error } = response
        if (id !== undefined && this.pendingRequests.has(id)) {
            const { resolve, reject } = this.pendingRequests.get(id)
            this.pendingRequests.delete(id)
            if (success) resolve(text)
            else reject(new Error(error))
        }
    }

    async recognize(imageBase64) {
        return new Promise((resolve, reject) => {
            if (!this.isReady) {
                // 如果服务还没准备好（比如正在下载模型），直接拒绝或者等待
                // 这里为了简单，直接返回错误提示
                reject(new Error('OCR Service is initializing (downloading model?)... please wait.'))
                return
            }

            const id = this.requestId++
            this.pendingRequests.set(id, { resolve, reject })

            const request = { id, command: 'recognize', image: imageBase64 }

            try {
                this.process.stdin.write(JSON.stringify(request) + '\n')
            } catch (e) {
                this.pendingRequests.delete(id)
                reject(e)
                return
            }

            // --- 修改点：超时设置 ---
            // 因为 OCR 有时候在 CPU 上跑比较慢，或者第一次预热慢
            // 建议设置长一点，比如 2 分钟
            setTimeout(() => {
                if (this.pendingRequests.has(id)) {
                    this.pendingRequests.delete(id)
                    reject(new Error('OCR request timeout (120s)'))
                }
            }, 120000)
        })
    }

    stop() {
        if (this.process) this.process.kill()
    }
}

module.exports = { OcrService }