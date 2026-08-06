# 项目结构说明

## 📁 目录结构

```
tts/
│
├── docs/                          # 📚 文档目录
│   ├── README.md                  # 完整使用说明
│   ├── VENV_GUIDE.md              # 虚拟环境使用指南
│   ├── OVERVIEW.md                # 项目总览
│   ├── NETWORK_TROUBLESHOOTING.md # 网络问题解决方案
│   └── STRUCTURE.md               # 本文件 - 项目结构说明
│
├── run.sh                         # 🚀 Linux/Mac运行脚本(推荐)
├── run.bat                        # 🚀 Windows运行脚本
├── run_with_venv.py               # 🚀 Python跨平台运行脚本
│
├── simple_test.py                 # ✅ 快速测试脚本(新手推荐)
├── install_nls_sdk.py             # 🔧 NLS SDK专用安装工具
├── test_venv.py                   # 🔍 虚拟环境详细测试
│
├── aliyun_tts_sdk.py              # ⭐ 主TTS脚本(推荐使用)
├── aliyun_tts.py                  # 📝 基础框架版本
├── example.py                     # 💡 使用示例代码
│
├── requirements.txt               # 📦 Python依赖列表
├── .gitignore                     # 🔒 Git忽略配置
└── README.md                      # 📖 项目简介(根目录)
```

## 📂 目录说明

### docs/ - 文档目录

存放所有Markdown文档,保持项目根目录整洁。

| 文件                       | 说明                    | 推荐阅读顺序   |
| -------------------------- | ----------------------- | -------------- |
| README.md                  | 完整的使用说明和API文档 | ⭐⭐⭐ 必读       |
| VENV_GUIDE.md              | 虚拟环境的详细使用指南  | ⭐⭐ 推荐        |
| OVERVIEW.md                | 项目功能和技术栈总览    | ⭐ 可选         |
| NETWORK_TROUBLESHOOTING.md | 网络问题诊断和解决      | 遇到问题时查看 |
| STRUCTURE.md               | 本文件 - 项目结构说明   | 了解项目组织   |

## 📄 核心脚本

### 运行管理类

| 脚本               | 平台      | 用途                             |
| ------------------ | --------- | -------------------------------- |
| `run.sh`           | Linux/Mac | Shell脚本,自动管理虚拟环境并运行 |
| `run.bat`          | Windows   | 批处理脚本,功能同run.sh          |
| `run_with_venv.py` | 跨平台    | Python脚本,功能同run.sh          |

**使用方法:**
```bash
./run.sh <脚本名>
# 例如:
./run.sh simple_test.py
./run.sh aliyun_tts_sdk.py
./run.sh example.py
```

### 测试和工具类

| 脚本                 | 用途               | 何时使用       |
| -------------------- | ------------------ | -------------- |
| `simple_test.py`     | 快速环境测试       | ⭐ 首次使用时   |
| `install_nls_sdk.py` | 安装NLS SDK        | 需要TTS功能时  |
| `test_venv.py`       | 详细的虚拟环境测试 | 调试环境问题时 |

### TTS功能类

| 脚本                | 说明              | 依赖        |
| ------------------- | ----------------- | ----------- |
| `aliyun_tts_sdk.py` | 完整的TTS实现     | 需要NLS SDK |
| `aliyun_tts.py`     | 基础框架,展示结构 | 无需SDK     |
| `example.py`        | 多种使用场景示例  | 需要NLS SDK |

## 📋 配置文件

| 文件               | 用途                |
| ------------------ | ------------------- |
| `requirements.txt` | Python依赖包列表    |
| `.gitignore`       | Git版本控制忽略规则 |

## 🎯 使用流程

### 新手入门

```bash
# 1. 快速测试环境
./run.sh simple_test.py

# 2. 根据提示安装NLS SDK
./run.sh install_nls_sdk.py

# 3. 配置密钥
export ALIYUN_TTS_APP_KEY='...'
export ALIYUN_ACCESS_KEY_ID='...'
export ALIYUN_ACCESS_KEY_SECRET='...'

# 4. 运行TTS
./run.sh aliyun_tts_sdk.py
```

### 日常开发

```bash
# 直接运行需要的脚本
./run.sh aliyun_tts_sdk.py    # 运行TTS
./run.sh example.py            # 查看示例
./run.sh test_venv.py          # 测试环境
```

## 🔍 文件分类

### 按功能分类

**🚀 启动入口**
- run.sh / run.bat / run_with_venv.py

**✅ 测试验证**
- simple_test.py
- test_venv.py

**🔧 安装工具**
- install_nls_sdk.py

**⭐ 核心功能**
- aliyun_tts_sdk.py (主要)
- aliyun_tts.py (备选)

**💡 学习示例**
- example.py

**📚 文档资料**
- docs/ 目录下所有.md文件

### 按依赖关系

**无依赖**
- simple_test.py - 只需基础Python
- aliyun_tts.py - 只需基础Python

**需要基础依赖**
- test_venv.py - 需要websocket等
- install_nls_sdk.py - 需要pip

**需要NLS SDK**
- aliyun_tts_sdk.py
- example.py

## 💡 最佳实践

### 文件命名规范

- `.py` - Python脚本
- `.sh` - Shell脚本(Linux/Mac)
- `.bat` - 批处理脚本(Windows)
- `.md` - Markdown文档
- `.txt` - 文本配置

### 文档组织原则

1. **根目录README.md**: 简洁的项目介绍和快速开始
2. **docs/目录**: 详细的文档和指南
3. **代码注释**: 每个脚本都有详细的docstring

### 虚拟环境

- 虚拟环境位于 `venv/` 目录
- 已添加到 `.gitignore`,不会提交到Git
- 通过运行脚本自动管理,无需手动激活

## 🔗 相关资源

- [阿里云智能语音交互](https://help.aliyun.com/document_detail/84430.html)
- [Python虚拟环境](https://docs.python.org/3/library/venv.html)
- [pip包管理器](https://pip.pypa.io/)

---

**提示**: 如有任何问题,请先查看 `docs/README.md` 获取完整使用说明。
