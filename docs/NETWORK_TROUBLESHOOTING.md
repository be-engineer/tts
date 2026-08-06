# 网络问题解决方案

## 🌐 问题说明

在使用阿里云TTS项目时,可能会遇到以下网络问题:

1. **SSL连接错误**: `SSLError(SSLEOFError(8, '[SSL: UNEXPECTED_EOF_WHILE_READING]'))`
2. **连接超时**: pip安装包时长时间无响应
3. **403错误**: 镜像源返回Forbidden错误
4. **下载速度慢**: 从官方PyPI下载速度很慢

## ✅ 自动解决方案

本项目已经内置了**多镜像源自动切换**功能:

### 工作原理

脚本会依次尝试以下镜像源:
1. 清华镜像源 (https://pypi.tuna.tsinghua.edu.cn/simple)
2. 阿里镜像源 (https://mirrors.aliyun.com/pypi/simple)
3. 中科大镜像源 (https://pypi.mirrors.ustc.edu.cn/simple)
4. 官方PyPI (https://pypi.org/simple)

如果某个镜像源失败或超时,会自动切换到下一个。

### 使用方法

直接运行即可,无需额外配置:

```bash
./run.sh test_venv.py
# 或
python run_with_venv.py test_venv.py
```

脚本会自动选择可用的镜像源。

---

## 🔧 手动解决方案

如果自动方案仍然失败,可以尝试以下方法:

### 方法一: 手动激活虚拟环境并安装

```bash
# 1. 激活虚拟环境
source venv/bin/activate

# 2. 使用特定镜像源安装
pip install -r requirements.txt \
    -i https://pypi.tuna.tsinghua.edu.cn/simple \
    --trusted-host pypi.tuna.tsinghua.edu.cn

# 3. 或者使用阿里镜像源
pip install -r requirements.txt \
    -i https://mirrors.aliyun.com/pypi/simple \
    --trusted-host mirrors.aliyun.com

# 4. 完成后退出
deactivate
```

### 方法二: 配置永久镜像源

创建或编辑 `~/.pip/pip.conf`:

```ini
[global]
index-url = https://pypi.tuna.tsinghua.edu.cn/simple
trusted-host = pypi.tuna.tsinghua.edu.cn

[install]
timeout = 60
```

然后正常安装:
```bash
source venv/bin/activate
pip install -r requirements.txt
deactivate
```

### 方法三: 使用代理

如果你有代理服务器:

```bash
# 设置HTTP代理
export http_proxy=http://proxy-server:port
export https_proxy=http://proxy-server:port

# 然后运行
./run.sh test_venv.py
```

### 方法四: 离线安装

如果完全无法联网:

1. 在有网络的机器上下载依赖:
```bash
pip download -r requirements.txt -d ./packages
```

2. 将packages目录复制到目标机器

3. 离线安装:
```bash
source venv/bin/activate
pip install --no-index --find-links=./packages -r requirements.txt
deactivate
```

---

## 📦 关于alibabacloud-nls-python-sdk

这个包可能不在所有镜像源中,我们采用从GitHub直接安装的方式:

```txt
git+https://github.com/aliyun/alibabacloud-nls-python-sdk.git
```

如果GitHub也无法访问,可以:

### 方案A: 手动克隆安装

```bash
# 1. 克隆仓库
git clone https://github.com/aliyun/alibabacloud-nls-python-sdk.git

# 2. 进入目录
cd alibabacloud-nls-python-sdk

# 3. 安装依赖
pip install -r requirements.txt

# 4. 安装SDK
pip install .

# 5. 返回项目目录
cd ..
```

### 方案B: 使用其他NLS SDK

如果上述方法都不可行,可以考虑使用REST API方式,不需要SDK:

参考 `aliyun_tts.py` 中的基础框架,自行实现HTTP请求。

---

## 🔍 诊断网络问题

运行以下命令检查网络状态:

```bash
# 测试能否访问清华镜像源
curl -I https://pypi.tuna.tsinghua.edu.cn/simple/

# 测试能否访问阿里镜像源
curl -I https://mirrors.aliyun.com/pypi/simple/

# 测试能否访问GitHub
curl -I https://github.com/

# 测试DNS解析
nslookup pypi.tuna.tsinghua.edu.cn
```

---

## 💡 常见问题

### Q1: 所有镜像源都超时怎么办?

**A:** 检查防火墙设置,确保允许HTTPS流量。或尝试使用手机热点。

### Q2: SSL证书错误?

**A:** 更新certifi包:
```bash
pip install --upgrade certifi
```

### Q3: 权限错误?

**A:** 确保虚拟环境已正确激活:
```bash
which python  # 应该显示 venv/bin/python
```

### Q4: 包版本冲突?

**A:** 清除pip缓存后重试:
```bash
pip cache purge
pip install -r requirements.txt
```

---

## 📞 需要帮助?

如果以上方法都无法解决:

1. 查看完整错误信息
2. 检查网络连接
3. 尝试不同的网络环境
4. 查阅相关文档:
   - [pip官方文档](https://pip.pypa.io/)
   - [清华镜像源帮助](https://mirrors.tuna.tsinghua.edu.cn/help/pypi/)
   - [阿里镜像源帮助](https://developer.aliyun.com/mirror/)

---

**提示**: 大多数网络问题可以通过切换镜像源或使用代理解决。本项目已内置多镜像源自动切换功能,通常无需手动干预。
