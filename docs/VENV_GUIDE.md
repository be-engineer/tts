# 虚拟环境使用指南

## 📖 概述

本项目提供了三种方式来管理Python虚拟环境和运行脚本,所有方式都会自动检测、创建和激活虚拟环境。

## 🚀 使用方法

### 方法一: 使用Shell脚本 (Linux/Mac - 推荐)

```bash
# 赋予执行权限(首次使用)
chmod +x run.sh

# 运行默认脚本(aliyun_tts_sdk.py)
./run.sh

# 运行指定脚本
./run.sh aliyun_tts_sdk.py
./run.sh example.py
./run.sh test_venv.py
```

**特点:**
- ✅ 彩色输出,易于阅读
- ✅ 自动激活/退出虚拟环境
- ✅ 显示详细的执行状态
- ✅ 支持传递命令行参数

---

### 方法二: 使用Python脚本 (跨平台)

```bash
# 运行默认脚本
python run_with_venv.py

# 运行指定脚本
python run_with_venv.py aliyun_tts_sdk.py
python run_with_venv.py example.py
python run_with_venv.py test_venv.py
```

**特点:**
- ✅ 跨平台(Linux/Mac/Windows)
- ✅ 纯Python实现,无需额外依赖
- ✅ 自动处理虚拟环境生命周期

---

### 方法三: 使用批处理脚本 (Windows)

```batch
REM 运行默认脚本
run.bat

REM 运行指定脚本
run.bat aliyun_tts_sdk.py
run.bat example.py
run.bat test_venv.py
```

**特点:**
- ✅ Windows原生支持
- ✅ 自动激活/退出虚拟环境
- ✅ 与Linux版本功能一致

---

### 方法四: 手动管理虚拟环境

如果你更喜欢手动控制,可以按照以下步骤:

#### 1. 创建虚拟环境

```bash
python3 -m venv venv
```

#### 2. 激活虚拟环境

**Linux/Mac:**
```bash
source venv/bin/activate
```

**Windows:**
```batch
venv\Scripts\activate
```

#### 3. 安装依赖

```bash
pip install -r requirements.txt
```

#### 4. 运行脚本

```bash
python aliyun_tts_sdk.py
python example.py
```

#### 5. 退出虚拟环境

```bash
deactivate
```

---

## 🔍 验证虚拟环境

运行测试脚本来验证虚拟环境是否正常工作:

```bash
# 使用自动管理脚本
./run.sh test_venv.py

# 或手动运行
source venv/bin/activate
python test_venv.py
deactivate
```

测试脚本会显示:
- Python可执行文件路径
- Python版本信息
- 是否在虚拟环境中运行
- 依赖包安装状态

---

## 📂 项目结构

```
tts/
├── venv/                  # 虚拟环境目录(自动生成,已加入.gitignore)
├── run.sh                 # Linux/Mac运行脚本
├── run.bat                # Windows运行脚本
├── run_with_venv.py       # Python跨平台运行脚本
├── test_venv.py           # 虚拟环境测试脚本
├── aliyun_tts_sdk.py      # 主TTS脚本(推荐使用)
├── aliyun_tts.py          # 基础框架版本
├── example.py             # 使用示例
├── requirements.txt       # 依赖包列表
├── README.md              # 项目说明文档
└── .gitignore             # Git忽略配置
```

---

## ⚙️ 工作原理

### 自动管理流程

1. **检测虚拟环境**: 检查`venv/bin/python`(Linux/Mac)或`venv\Scripts\python.exe`(Windows)是否存在

2. **创建虚拟环境**: 如果不存在,使用`python -m venv venv`创建

3. **激活虚拟环境**: 
   - Shell脚本: `source venv/bin/activate`
   - Python脚本: 直接使用虚拟环境的Python解释器
   - Windows批处理: `call venv\Scripts\activate.bat`

4. **安装依赖**: 运行`pip install -r requirements.txt`

5. **运行脚本**: 在虚拟环境中执行指定的Python脚本

6. **退出虚拟环境**: 脚本执行完成后自动退出

---

## 💡 最佳实践

### 1. 首次使用

```bash
# 直接运行,会自动完成所有设置
./run.sh test_venv.py
```

### 2. 日常开发

```bash
# 使用自动管理脚本运行
./run.sh aliyun_tts_sdk.py
```

### 3. 调试模式

如果需要保持虚拟环境激活状态进行调试:

```bash
# 手动激活
source venv/bin/activate

# 查看当前环境
which python
pip list

# 运行脚本
python aliyun_tts_sdk.py

# 完成后退出
deactivate
```

### 4. 更新依赖

```bash
# 编辑requirements.txt后
./run.sh test_venv.py  # 会自动安装新依赖
```

---

## ❓ 常见问题

### Q1: 虚拟环境创建失败?

**A:** 确保已安装Python 3.6+:
```bash
python3 --version
```

### Q2: 依赖安装失败?

**A:** 尝试使用国内镜像源:
```bash
source venv/bin/activate
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### Q3: 如何删除虚拟环境重新创建?

**A:** 
```bash
# 删除虚拟环境
rm -rf venv

# 重新运行,会自动创建
./run.sh test_venv.py
```

### Q4: 如何在IDE中使用虚拟环境?

**A:** 
- **VSCode**: 选择解释器 -> `./venv/bin/python`
- **PyCharm**: Settings -> Project -> Python Interpreter -> Add -> Existing Environment -> 选择`./venv/bin/python`

### Q5: 虚拟环境占用多少空间?

**A:** 通常100-300MB,取决于安装的依赖包数量。

---

## 🔒 安全提示

1. **不要提交虚拟环境到Git**: `venv/`目录已在`.gitignore`中配置
2. **不要硬编码密钥**: 使用环境变量或`.env`文件
3. **定期更新依赖**: 运行`pip install --upgrade -r requirements.txt`

---

## 📚 相关文档

- [Python虚拟环境官方文档](https://docs.python.org/3/library/venv.html)
- [pip使用指南](https://pip.pypa.io/en/stable/)
- [阿里云TTS文档](https://help.aliyun.com/document_detail/84430.html)
