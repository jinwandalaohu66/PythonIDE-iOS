<p align="center">
  <img src="docs/icon.png" width="120" alt="PythonIDE Logo" />
</p>

<h1 align="center">PythonIDE</h1>
<h3 align="center">掌上的 Python & JavaScript 开发环境</h3>
<p align="center">
  <strong>让编程从电脑走到手机与平板</strong> · Write, Run, Debug on iOS
</p>

<p align="center">
  <a href="https://apps.apple.com/app/id6753987304">
    <img src="https://img.shields.io/badge/App%20Store-下载-black?style=for-the-badge&logo=apple" alt="Download on App Store" height="44" />
  </a>
  <a href="https://github.com/jinwandalaohu66/PythonIDE-Landing">
    <img src="https://img.shields.io/github/stars/jinwandalaohu66/PythonIDE-Landing?style=for-the-badge&logo=github" alt="GitHub Stars" height="44" />
  </a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/iOS-16.2+-blue?style=flat-square" alt="iOS 16.2+" />
  <img src="https://img.shields.io/badge/Python-3.13-3776AB?style=flat-square&logo=python" alt="Python 3.13" />
  <img src="https://img.shields.io/badge/JavaScript-ES6+-F7DF1E?style=flat-square&logo=javascript" alt="JavaScript" />
  <img src="https://img.shields.io/badge/Swift-5.9-FA7343?style=flat-square&logo=swift" alt="Swift" />
</p>

---

## ✨ 核心功能 / Core Features

### 🐍 多语言运行
| 功能 | 描述 |
|------|------|
| **Python 3.13** | 本地运行、完整标准库、交互式 I/O、async/await、多线程 |
| **JavaScript** | JavaScriptCore 执行 .js，alert/confirm/prompt、fetch、localStorage、剪贴板等桥接 |
| **HTML 预览** | WKWebView 加载 HTML+CSS+JS，相对路径、alert/console 桥接 |

### ✏️ 专业代码编辑器
| 功能 | 描述 |
|------|------|
| **语法高亮** | Python、JavaScript、HTML、CSS、JSON、Markdown、LOG 等 |
| **代码自动补全** | 智能提示、补全建议 |
| **自动缩进** | 按语言自动缩进、Tab 宽度可调 |
| **行号栏** | 显示行号、支持大文件 |
| **等宽字体** | 可调字体大小（10–30 号） |
| **查找 & 替换** | 全文搜索、高亮匹配、跳转行 |
| **快捷输入栏** | 按语言（Py/JS/HTML/CSS/JSON/MD）定制符号与 snippets，可自定义 |
| **实时保存** | 自动保存、手动保存 |
| **显示空白符** | 可选显示空格、制表符 |
| **捏合缩放** |  pinch 调节字体大小 |

### 📄 多格式编辑与预览
| 类型 | 支持 |
|------|------|
| **可运行** | `.py`（Python）、`.js`（JavaScript） |
| **可预览** | `.html`（网页）、`.css`（套用示例）、`.md`（Markdown 渲染）、`.csv`（表格） |
| **可编辑** | `.json`、`.txt`、`.log`、`.php` 等 |

### 📂 文件管理
| 功能 | 描述 |
|------|------|
| **多层级文件夹** | 无限层级、面包屑导航、点击路径跳转 |
| **文件操作** | 创建、重命名、复制、移动、删除 |
| **回收站** | 7 天保留、恢复、批量删除、倒计时提示 |
| **置顶** | 文件/文件夹置顶，左滑快速操作 |
| **搜索** | 按文件名搜索、高亮、历史记录 |
| **批量操作** | 多选、批量删除 |
| **导入** | 从系统文件应用导入 |
| **排序** | 拖拽排序、按更新时间 |

### 📺 控制台与输出
| 功能 | 描述 |
|------|------|
| **Rich 输出** | ANSI 彩色、图表可视化 |
| **分屏模式** | 编辑器与控制台同屏 |
| **输出设置** | 字体大小、输出速度（慢/正常/快）、行号、自动滚动 |
| **运行历史** | 查看并再次运行历史脚本 |

### 🛠️ 开发者工具箱（9 大工具）
| 工具 | 功能 |
|------|------|
| **编解码** | URL 编解码、Unicode、MD5、Base64 |
| **JSON** | 格式化、压缩、验证 |
| **API 调试** | HTTP 请求、响应预览 |
| **二维码** | 生成、识别、Data URL |
| **图片 URL** | URL 转图片、图片转 Data URL |
| **HTML 图片** | HTML 转图片、抓图、Data URL |
| **时间戳** | 毫秒/秒互转、日期格式化 |
| **进制转换** | 二、八、十、十六进制 |
| **正则表达式** | 匹配、测试、替换、分组预览 |

工具支持排序、搜索。

### 📚 第三方库
| 类别 | 示例 |
|------|------|
| **数据科学** | NumPy、Pandas、Matplotlib、SciPy、scikit-learn |
| **网络** | requests、aiohttp、urllib3、certifi |
| **加密** | PyCryptodome、cryptography |
| **其他** | Pillow、lxml、beautifulsoup4 等 150+ 预装 Wheel |

库管理：查看已安装、卸载、安装新库（.whl）。

### 🤖 AI 助手（需自配 API）
- 自然语言改代码
- 审查、注释、优化、修错
- 对话式聊天，支持多轮重试与采纳/放弃
- 支持 Py/JS/HTML/CSS/JSON/MD 等语言

### 📷 Photos 模块
- Python 调用相册与相机
- 配合 Pillow 做裁剪、压缩、处理

### 📂 媒体预览
- 图片、视频、PDF、文本、部分音频
- 应用内直接预览

### 🔒 隐私与体验
| 功能 | 描述 |
|------|------|
| **Face ID / Touch ID** | 应用锁定 |
| **4 套图标** | 默认、深色、渐变、极简，即时切换 |
| **外观** | 跟随系统 / 浅色 / 深色 |
| **灵动岛** | 脚本运行状态、计时、完成提醒 |
| **后台运行** | 长任务、本地通知、音频保活 |
| **触觉反馈** | 成功/失败/轻提示 |
| **URL Scheme** | `pythonide://`，支持从通知/Widget 跳转 |

---

## 📱 截图 / Screenshots

<p align="center">
  <img src="https://via.placeholder.com/280x600/1e3a5f/fff?text=Editor" width="280" alt="代码编辑器" />
  <img src="https://via.placeholder.com/280x600/1e3a5f/fff?text=Console" width="280" alt="控制台输出" />
  <img src="https://via.placeholder.com/280x600/1e3a5f/fff?text=Split+View" width="280" alt="分屏模式" />
</p>

---

## 📥 安装 / Install

| 方式 | 说明 |
|------|------|
| **App Store** | [点击下载](https://apps.apple.com/app/id6753987304) · 推荐 |
| **系统要求** | iOS 16.2+，iPhone / iPad |

---

## 💬 社区与反馈 / Community & Feedback

| 渠道 | 链接 |
|------|------|
| **✈️ Telegram** | [iOS 端 Py 编程 IDE](https://t.me/pythonzwb) |
| **💡 功能建议** | [GitHub Discussions](https://github.com/jinwandalaohu66/PythonIDE-Landing/discussions) |
| **🐛 问题反馈** | [Issues](https://github.com/jinwandalaohu66/PythonIDE-Landing/issues) |
| **📧 邮件** | 应用内「设置 → 反馈」 |
| **⭐ 支持** | 在 App Store 评分、在 GitHub 点 Star |

---

## ☕ 捐赠 / Donate

如果 PythonIDE 对你有帮助，欢迎请我喝杯咖啡，支持后续开发。

<p align="center">
  <img src="docs/donate-qr.jpeg" width="200" alt="赞赏码" />
</p>
<p align="center">
  <em>扫码赞赏 · Thank you for your support</em>
</p>

---

## 🙏 致谢 / Thanks

感谢所有使用和反馈 PythonIDE 的开发者。  
如果你觉得有用，欢迎 **Star** 和 **App Store 评分**，让更多人发现它。

<p align="center">
  <strong>PythonIDE</strong> —— 本地、纯粹、实用的移动端编程环境
</p>

---

<p align="center">
  <sub>
    <strong>Topics</strong> · ios · python · javascript · ide · mobile-development · swift · scripting · developer-tools
  </sub>
</p>
