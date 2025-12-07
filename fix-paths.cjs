const fs = require('fs');
const path = require('path');

const indexPath = path.join(__dirname, '.output/public/index.html');

try {
    let content = fs.readFileSync(indexPath, 'utf8');

    // 1. 替换 CSS 和 JS 的引用路径
    // href="/assets/..." -> href="./assets/..."
    // src="/assets/..."  -> src="./assets/..."
    content = content.replace(/href="\/assets\//g, 'href="./assets/');
    content = content.replace(/src="\/assets\//g, 'src="./assets/');

    // 2. 替换 Nuxt 内部配置的 baseURL
    // baseURL:"/" -> baseURL:"./"
    content = content.replace(/baseURL:"\/"/g, 'baseURL:"./"');

    fs.writeFileSync(indexPath, content, 'utf8');
    console.log('✅ Successfully fixed relative paths in index.html');
} catch (err) {
    console.error('❌ Error fixing paths:', err);
    process.exit(1);
}
