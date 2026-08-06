# 使用官方PyPI说明

## 📝 配置说明

本项目已配置为使用**官方PyPI** (https://pypi.org) 安装依赖包。

### 优点
- ✅ 获取最新版本和更新
- ✅ 包完整性保证
- ✅ 全球CDN加速
- ✅ 无需担心镜像源同步延迟

### 缺点
- ⚠️ 在中国大陆访问可能较慢
- ⚠️ 可能需要代理或VPN
- ⚠️ 网络不稳定时可能超时

---

## 🔧 当前配置

### Shell脚本 (run.sh)
```bash
# 使用官方PyPI,超时60秒
pip install -r requirements.txt --timeout 60 --no-cache-dir
```

### Python脚本 (run_with_venv.py)
```python
subprocess.check_call([
    pip_path, 'install', '-r', requirements_file,
    '--timeout', '60',
    '--no-cache-dir'
], timeout=120)
```

### Windows批处理 (run.bat)
```batch
pip install -r requirements.txt --timeout 60 --no-cache-dir
```

---

## 🌐 如果需要切换回国内镜像源

### 方法一: 临时使用

```bash
# 清华镜像源
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 阿里镜像源
pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple

# 中科大镜像源
pip install -r requirements.txt -i https://pypi.mirrors.ustc.edu.cn/simple
```

### 方法二: 永久配置

创建或编辑 `~/.pip/pip.conf` (Linux/Mac) 或 `%APPDATA%\pip\pip.ini` (Windows):

```ini
[global]
index-url = https://pypi.tuna.tsinghua.edu.cn/simple
trusted-host = pypi.tuna.tsinghua.edu.cn
timeout = 60
```

### 方法三: 修改脚本

编辑 `run.sh`,将安装命令改为:

```bash
pip install -r "$SCRIPT_DIR/requirements.txt" \
    -i https://pypi.tuna.tsinghua.edu.cn/simple \
    --trusted-host pypi.tuna.tsinghua.edu.cn \
    --timeout 60
```

---

## 💡 网络优化建议

### 1. 使用代理

```bash
# 设置HTTP代理
export http_proxy=http://proxy-server:port
export https_proxy=http://proxy-server:port

# 然后运行
./run.sh aliyun_tts_sdk.py
```

### 2. 增加超时时间

如果网络较慢,可以增加超时时间:

```bash
pip install -r requirements.txt --timeout 120
```

### 3. 禁用缓存

```bash
pip install -r requirements.txt --no-cache-dir
```

这可以避免缓存损坏导致的问题。

### 4. 使用更快的DNS

```bash
# 使用Google DNS
echo "nameserver 8.8.8.8" | sudo tee /etc/resolv.conf

# 或使用Cloudflare DNS
echo "nameserver 1.1.1.1" | sudo tee /etc/resolv.conf
```

---

## 🚀 推荐安装流程

### 首次安装

```bash
# 1. 清理旧环境(如果有)
rm -rf venv

# 2. 使用官方PyPI安装
./run.sh simple_test.py

# 如果失败,尝试国内镜像源
source venv/bin/activate
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
deactivate
```

### 日常使用

```bash
# 直接运行即可
./run.sh aliyun_tts_sdk.py
```

---

## ❓ 常见问题

### Q1: 安装速度很慢?

**A:** 
- 检查网络连接
- 尝试使用代理
- 或切换到国内镜像源

### Q2: 连接超时?

**A:**
```bash
# 增加超时时间
pip install -r requirements.txt --timeout 180

# 或使用国内镜像源
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### Q3: SSL证书错误?

**A:**
```bash
# 更新certifi
pip install --upgrade certifi

# 或暂时禁用SSL验证(不推荐)
pip install -r requirements.txt --trusted-host pypi.org
```

### Q4: 包下载失败?

**A:**
```bash
# 清除缓存后重试
pip cache purge
pip install -r requirements.txt --no-cache-dir
```

---

## 📊 性能对比

| 源         | 速度             | 稳定性 | 版本新鲜度 |
| ---------- | ---------------- | ------ | ---------- |
| 官方PyPI   | ⭐⭐⭐ (需良好网络) | ⭐⭐⭐⭐⭐  | ⭐⭐⭐⭐⭐      |
| 清华镜像   | ⭐⭐⭐⭐⭐            | ⭐⭐⭐⭐   | ⭐⭐⭐⭐       |
| 阿里镜像   | ⭐⭐⭐⭐⭐            | ⭐⭐⭐⭐   | ⭐⭐⭐⭐       |
| 中科大镜像 | ⭐⭐⭐⭐             | ⭐⭐⭐    | ⭐⭐⭐        |

---

## 🔗 相关资源

- [PyPI官方网站](https://pypi.org/)
- [清华镜像源](https://mirrors.tuna.tsinghua.edu.cn/help/pypi/)
- [阿里镜像源](https://developer.aliyun.com/mirror/pypi)
- [pip官方文档](https://pip.pypa.io/)

---

**提示**: 如果网络条件允许,建议使用官方PyPI以获得最佳体验。如遇网络问题,可临时切换到国内镜像源。
