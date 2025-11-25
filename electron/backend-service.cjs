// electron/ocr-service.cjs
const { spawn } = require('child_process')
const path = require('path')

class BackendService {
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
            scriptPath = path.join(__dirname, '../services/backend_service.py')
        } else {
            pythonPath = path.join(process.resourcesPath, 'services/backend.exe')
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
            console.log('✅ OCR Service is Ready!')
            return
        }

        // 关键点 1：必须从 response 里解构出 tokens
        const { id, success, text, tokens, error } = response

        if (id !== undefined && this.pendingRequests.has(id)) {
            const { resolve, reject } = this.pendingRequests.get(id)
            this.pendingRequests.delete(id)

            if (success) {
                // 关键点 2：如果是分词请求，Python返回的是 tokens，text 是空的
                // 所以这里要判断：如果有 tokens，就返回对象；否则返回 text 字符串
                if (tokens) {
                    resolve({ tokens: tokens })
                } else {
                    resolve(text)
                }
            } else {
                reject(new Error(error))
            }
        }
    }

    // ✅ 新增：通用请求发送方法 (避免代码重复)
    _sendRequest(payload, timeout = 120000) {
        return new Promise((resolve, reject) => {
            if (!this.isReady) {
                reject(new Error('OCR Service is initializing... please wait.'))
                return
            }

            const id = this.requestId++
            this.pendingRequests.set(id, { resolve, reject })

            // 合并 ID 和 具体的请求数据
            const request = { ...payload, id }

            try {
                this.process.stdin.write(JSON.stringify(request) + '\n')
            } catch (e) {
                this.pendingRequests.delete(id)
                reject(e)
                return
            }

            // 超时处理
            setTimeout(() => {
                if (this.pendingRequests.has(id)) {
                    this.pendingRequests.delete(id)
                    reject(new Error(`Request timeout (${timeout}ms)`))
                }
            }, timeout)
        })
    }

    // 1. OCR 识别
    async recognize(imageBase64) {
        // 调用通用方法
        return this._sendRequest({ command: 'recognize', image: imageBase64 })
    }

    // 2. 分词
    async tokenize(text) {
        // 调用通用方法，分词比较快，超时设短一点也没关系 (比如 10秒)
        // 注意：这里传的是 text，不是 image
        // _handleResponse 会返回 { tokens: [...] }
        return this._sendRequest({ command: 'tokenize', text: text }, 30000)
    }

    stop() {
        if (this.process) this.process.kill()
    }
}

module.exports = { BackendService }
