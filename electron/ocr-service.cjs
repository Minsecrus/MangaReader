// electron/ocr-service.cjs
const { spawn } = require('child_process')
const path = require('path')

class OcrService {
    constructor() {
        this.process = null
        this.isReady = false
        this.pendingRequests = new Map()
        this.requestId = 0
        this.responseBuffer = ''
    }

    start() {
        // 开发环境: 使用 venv 中的 Python
        // 生产环境: 使用打包的 Python 可执行文件
        const isDev = !require('electron').app.isPackaged

        let pythonPath
        let scriptPath

        if (isDev) {
            // 开发环境: 使用 venv 中的 Python
            const venvPython = path.join(__dirname, '../ocr-service/venv/Scripts/python.exe')
            pythonPath = venvPython
            scriptPath = path.join(__dirname, '../ocr-service/ocr_service.py')
        } else {
            // 生产环境: 使用打包的可执行文件
            pythonPath = path.join(process.resourcesPath, 'ocr-service/ocr-service.exe')
            scriptPath = null // exe 不需要脚本路径
        }

        console.log('🚀 Starting OCR service...')
        console.log('Environment:', isDev ? 'Development' : 'Production')
        console.log('Python:', pythonPath)
        console.log('Script:', scriptPath)

        const args = scriptPath ? ['-u', scriptPath] : []

        this.process = spawn(pythonPath, args, {
            stdio: ['pipe', 'pipe', 'pipe'],
            env: { ...process.env, PYTHONUNBUFFERED: '1', PYTHONIOENCODING: 'utf-8' }
        })

        // 设置流编码为 UTF-8
        this.process.stdin.setDefaultEncoding('utf-8')
        this.process.stdout.setEncoding('utf-8')
        this.process.stderr.setEncoding('utf-8')

        // 监听 stderr (日志输出)
        this.process.stderr.on('data', (data) => {
            console.log('[OCR Service]', data.toString().trim())
        })

        // 监听 stdout (JSON 响应)
        this.process.stdout.on('data', (data) => {
            this.responseBuffer += data

            // 按行处理响应
            const lines = this.responseBuffer.split('\n')
            this.responseBuffer = lines.pop() || '' // 保留不完整的行

            lines.forEach(line => {
                line = line.trim()
                if (!line) return

                try {
                    const response = JSON.parse(line)
                    this._handleResponse(response)
                } catch (e) {
                    console.error('Failed to parse OCR response:', line, e)
                }
            })
        })

        // 进程错误处理
        this.process.on('error', (error) => {
            console.error('❌ OCR service error:', error)
            this.isReady = false
        })

        this.process.on('exit', (code) => {
            console.log(`OCR service exited with code ${code}`)
            this.isReady = false

            // 拒绝所有待处理的请求
            this.pendingRequests.forEach(({ reject }) => {
                reject(new Error('OCR service stopped'))
            })
            this.pendingRequests.clear()
        })
    }

    _handleResponse(response) {
        // 处理启动信号
        if (response.status === 'ready') {
            this.isReady = true
            console.log('✅ OCR Service Ready!')
            return
        }

        if (response.status === 'error') {
            console.error('❌ OCR Service Failed:', response.message)
            return
        }

        // 处理普通响应
        const { id, success, text, error, message } = response

        // ping 命令的响应
        if (message === 'pong') {
            console.log('✅ OCR service is alive')
            return
        }

        // 查找对应的请求
        if (id !== undefined && this.pendingRequests.has(id)) {
            const { resolve, reject } = this.pendingRequests.get(id)
            this.pendingRequests.delete(id)

            if (success) {
                resolve(text)
            } else {
                reject(new Error(error || 'OCR recognition failed'))
            }
        }
    }

    async recognize(imageBase64) {
        return new Promise((resolve, reject) => {
            if (!this.isReady) {
                reject(new Error('OCR service not ready'))
                return
            }

            // 生成请求 ID
            const id = this.requestId++

            // 保存回调
            this.pendingRequests.set(id, { resolve, reject })

            // 构造请求
            const request = {
                id,
                command: 'recognize',
                image: imageBase64
            }

            // 发送请求
            try {
                this.process.stdin.write(JSON.stringify(request) + '\n')
            } catch (error) {
                this.pendingRequests.delete(id)
                reject(error)
                return
            }

            // 超时处理 (60秒，因为首次识别可能需要加载模型)
            setTimeout(() => {
                if (this.pendingRequests.has(id)) {
                    this.pendingRequests.delete(id)
                    reject(new Error('OCR request timeout'))
                }
            }, 60000)
        })
    }

    async ping() {
        return new Promise((resolve, reject) => {
            if (!this.isReady) {
                reject(new Error('OCR service not ready'))
                return
            }

            const request = { command: 'ping' }

            try {
                this.process.stdin.write(JSON.stringify(request) + '\n')
                resolve(true)
            } catch (error) {
                reject(error)
            }
        })
    }

    stop() {
        if (this.process) {
            try {
                const request = { command: 'exit' }
                this.process.stdin.write(JSON.stringify(request) + '\n')
            } catch (e) {
                // 忽略错误
            }

            setTimeout(() => {
                if (this.process) {
                    this.process.kill()
                    this.process = null
                }
            }, 1000)
        }
    }
}

module.exports = { OcrService }
