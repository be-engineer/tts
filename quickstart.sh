#!/bin/bash
# 快速开始脚本 - 一键设置和测试

set -e

echo "============================================================"
echo "阿里云TTS - 快速开始"
echo "============================================================"
echo ""

# 检查Python版本
echo "1️⃣  检查Python环境..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo "   ✓ $PYTHON_VERSION"
else
    echo "   ✗ 未找到Python3,请先安装Python 3.6+"
    exit 1
fi
echo ""

# 运行测试脚本
echo "2️⃣  创建虚拟环境并运行测试..."
echo ""

./run.sh test_venv.py

echo ""
echo "============================================================"
echo "下一步:"
echo "============================================================"
echo ""
echo "1. 配置阿里云密钥:"
echo "   export ALIYUN_TTS_APP_KEY='your_app_key'"
echo "   export ALIYUN_ACCESS_KEY_ID='your_access_key_id'"
echo "   export ALIYUN_ACCESS_KEY_SECRET='your_access_key_secret'"
echo ""
echo "2. 运行TTS脚本:"
echo "   ./run.sh aliyun_tts_sdk.py"
echo ""
echo "3. 查看示例:"
echo "   ./run.sh example.py"
echo ""
echo "4. 阅读文档:"
echo "   cat README.md"
echo "   cat VENV_GUIDE.md"
echo ""
echo "============================================================"
