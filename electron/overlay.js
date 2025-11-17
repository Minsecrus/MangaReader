// electron/overlay.js

const $source = document.querySelector('.source')
let sourceContext = null
console.log(222)
window.electronAPI.on('window:capture-source', (base64) => {
    console.log(111)
    $source.style.backgroundImage = `url(${base64})`

    const image = new Image()
    image.src = base64
    image.onload = () => {
        const canvas = document.createElement("canvas")
        canvas.width = image.width
        canvas.height = image.height
        const context = canvas.getContext('2d')
        context.drawImage(image, 0, 0)
        sourceContext = context
        console.log(sourceContext)
    }
})

const $preview = document.querySelector('.preview')
const $size = document.querySelector('.size')
const $tool = document.querySelector('.tool')
const selection = {
    flag: false,
    x: 0,
    y: 0
}

document.addEventListener('mousedown', (event) => {
    const { x, y } = event
    selection.flag = true
    selection.x = x
    selection.y = y
})

document.addEventListener('mousemove', (event) => {
    if (!selection.flag || !sourceContext) {
        return
    }
    const { x, y } = event
    const left = Math.min(x, selection.x)
    const top = Math.min(y, selection.y)
    const width = Math.abs(x - selection.x)
    const height = Math.abs(y - selection.y)
    $preview.style.left = `${left}px`
    $preview.style.top = `${top}px`
    $preview.style.width = `${width}px`
    $preview.style.height = `${height}px`

    $preview.width = width
    $preview.height = height
    const context = $preview.getContext('2d')
    const imageData = sourceContext.getImageData(left, top, width, height)
    context.putImageData(imageData, 0, 0)

    $preview.style.display = 'block'

    $size.innerHTML = `${width}px x ${height}px`
    $size.style.left = `${left}px`
    $size.style.top = `${top}px`

    $size.style.display = 'block'

    $tool.style.left = `${left + width}px`
    $tool.style.top = `${top + height}px`
    $tool.style.display = 'block'
})
document.addEventListener('mouseup', () => {
    selection.flag = false
})
