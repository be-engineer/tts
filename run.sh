#!/bin/bash

# 命令:
#   ./run.sh start        启动 Web 服务 (后台运行)
#   ./run.sh stop         停止 Web 服务
#   ./run.sh restart      重启 Web 服务
#   ./run.sh status       查看服务状态
#   ./run.sh log          查看服务日志 (实时)
#   ./run.sh gui          运行 GUI 程序
#   ./run.sh help         显示此帮助信息

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$SCRIPT_DIR/venv"
VENV_PYTHON="$VENV_DIR/bin/python"
VENV_PIP="$VENV_DIR/bin/pip"
PID_FILE="$SCRIPT_DIR/tts_server.pid"
LOG_FILE="$SCRIPT_DIR/tts_server.log"
WEB_APP="$SCRIPT_DIR/web_app.py"

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'


activate_venv() {
    if [ ! -f "$VENV_PYTHON" ]; then
        echo -e "${YELLOW}ℹ️  未检测到虚拟环境,正在创建...${NC}"
        python3 -m venv "$VENV_DIR"
        echo -e "${GREEN}✓ 虚拟环境创建成功${NC}"
    else
        echo -e "${GREEN}✓ 检测到现有虚拟环境${NC}"
    fi
    
    echo "🔧 激活虚拟环境..."
    source "$VENV_DIR/bin/activate"
}


install_dependencies() {
    local install_gui=${1:-false}
    local install_recognize=${2:-false}
    if [ ! -f "$SCRIPT_DIR/requirements.txt" ]; then
        echo -e "${YELLOW}⚠️  未找到requirements.txt文件${NC}"
        return 0
    fi

    echo "📦 检查并安装依赖包..."
    pip install --upgrade pip -q --timeout 30 || true

    # Web服务核心依赖（必需）
    local core_pkgs="edge-tts websocket-client Flask"
    echo "🔧 安装 Web 服务核心依赖..."
    if timeout 30 pip install $core_pkgs \
        --timeout 30 \
        --no-cache-dir; then
        echo -e "${GREEN}✓ 核心依赖安装成功${NC}"
    else
        echo -e "${RED}✗ 核心依赖安装失败,无法继续${NC}"
        return 1
    fi

    # 语音识别依赖（可选）
    if [ "$install_recognize" = "true" ]; then
        echo "🔧 安装语音识别依赖 (Whisper)..."
        if timeout 300 pip install openai-whisper zhconv \
            --timeout 60 \
            --no-cache-dir; then
            echo -e "${GREEN}✓ 语音识别依赖安装成功${NC}"
        else
            echo -e "${YELLOW}⚠️  语音识别依赖安装失败,语音识别功能不可用${NC}"
        fi
    fi

    # GUI依赖（仅在运行GUI时安装）
    if [ "$install_gui" = "true" ]; then
        echo "🔧 安装 GUI 依赖..."
        if timeout 300 pip install PyQt6 pygame \
            --timeout 60 \
            --no-cache-dir; then
            echo -e "${GREEN}✓ GUI依赖安装成功${NC}"
        else
            echo -e "${YELLOW}⚠️  GUI依赖安装失败,GUI功能可能不可用${NC}"
        fi
    fi

    echo -e "${GREEN}✓ 依赖安装完成${NC}"
    return 0
}


start_server() {
    if [ -f "$PID_FILE" ]; then
        pid=$(cat "$PID_FILE")
        if kill -0 "$pid" 2>/dev/null; then
            echo -e "${YELLOW}⚠️  服务已经在运行中 (PID: $pid)${NC}"
            echo ""
            echo "📡 访问地址:"
            echo "   - 本机访问: http://localhost:5001"
            echo "   - 局域网访问:"
            for ip in $(hostname -I 2>/dev/null | tr ' ' '\n' | grep -v '^$'); do
                echo "     http://$ip:5001"
            done
            echo ""
            echo "📝 日志文件: $LOG_FILE"
            return 0
        else
            rm "$PID_FILE"
        fi
    fi
    
    activate_venv
    install_dependencies false true || return 1

    echo -e "${GREEN}🚀 正在启动 Web 服务...${NC}"
    nohup python "$WEB_APP" > "$LOG_FILE" 2>&1 &
    pid=$!
    echo "$pid" > "$PID_FILE"
    
    sleep 2
    
    if kill -0 "$pid" 2>/dev/null; then
        echo -e "${GREEN}✓ Web 服务启动成功 (PID: $pid)${NC}"
        echo ""
        echo "📡 访问地址:"
        echo "   - 本机访问: http://localhost:5001"
        echo "   - 局域网访问:"
        for ip in $(hostname -I 2>/dev/null | tr ' ' '\n' | grep -v '^$'); do
            echo "     http://$ip:5001"
        done
        echo ""
        echo "💡 IDE 预览提示:"
        echo "   - 点击 IDE 右上角的眼睛图标打开预览"
        echo "   - 或按 Ctrl+Shift+P 输入 'Preview' 打开"
        echo ""
        echo "📝 日志文件: $LOG_FILE"
    else
        echo -e "${RED}✗ Web 服务启动失败${NC}"
        cat "$LOG_FILE"
        rm "$PID_FILE"
        return 1
    fi
}


stop_server() {
    if [ ! -f "$PID_FILE" ]; then
        echo -e "${YELLOW}⚠️  服务未运行${NC}"
        return 0
    fi
    
    pid=$(cat "$PID_FILE")
    
    if kill -0 "$pid" 2>/dev/null; then
        echo -e "${YELLOW}⏹️  正在停止服务 (PID: $pid)...${NC}"
        kill "$pid"
        sleep 2
        
        if kill -0 "$pid" 2>/dev/null; then
            echo -e "${YELLOW}⚠️  优雅停止失败,强制终止...${NC}"
            kill -9 "$pid"
        fi
        
        rm "$PID_FILE"
        echo -e "${GREEN}✓ 服务已停止${NC}"
    else
        echo -e "${YELLOW}⚠️  进程不存在,清理PID文件${NC}"
        rm "$PID_FILE"
    fi
}


restart_server() {
    stop_server
    if [ -f "$PID_FILE" ]; then
        rm "$PID_FILE"
    fi
    echo ""
    start_server
}


show_status() {
    if [ ! -f "$PID_FILE" ]; then
        echo -e "${RED}✗ 服务未运行${NC}"
        return 0
    fi
    
    pid=$(cat "$PID_FILE")
    
    if kill -0 "$pid" 2>/dev/null; then
        echo -e "${GREEN}✓ 服务正在运行 (PID: $pid)${NC}"
        echo ""
        echo "📡 访问地址:"
        echo "   - 本机访问: http://localhost:5001"
        echo "   - 局域网访问:"
        for ip in $(hostname -I 2>/dev/null | tr ' ' '\n' | grep -v '^$'); do
            echo "     http://$ip:5001"
        done
        echo ""
        echo "📝 日志文件: $LOG_FILE"
    else
        echo -e "${RED}✗ 服务已停止 (PID文件存在但进程不存在)${NC}"
        rm "$PID_FILE"
    fi
}


show_log() {
    if [ ! -f "$LOG_FILE" ]; then
        echo -e "${YELLOW}⚠️  日志文件不存在${NC}"
        return 0
    fi
    
    echo "📝 服务日志:"
    echo "============================================================"
    tail -f "$LOG_FILE"
}


run_gui() {
    activate_venv
    install_dependencies true || return 1
    
    echo ""
    echo "============================================================"
    echo "虚拟环境已激活: $VIRTUAL_ENV"
    echo "Python版本: $(python --version)"
    echo "============================================================"
    echo ""
    
    python "$SCRIPT_DIR/edge_tts_gui_pyqt.py"
    EXIT_CODE=$?
    
    echo ""
    echo "============================================================"
    if [ $EXIT_CODE -eq 0 ]; then
        echo -e "${GREEN}✓ GUI程序执行成功${NC}"
    else
        echo -e "${RED}✗ GUI程序执行失败 (退出码: $EXIT_CODE)${NC}"
    fi
    echo "============================================================"
    
    deactivate
    exit $EXIT_CODE
}


show_help() {
    echo "📢 Edge TTS 文本转语音 - 运行脚本"
    echo ""
    echo "用法: ./run.sh [命令]"
    echo ""
    echo "命令:"
    echo "  start        启动 Web 服务 (后台运行)"
    echo "  stop         停止 Web 服务"
    echo "  restart      重启 Web 服务"
    echo "  status       查看服务状态"
    echo "  log          查看服务日志 (实时)"
    echo "  gui          运行 GUI 程序"
    echo "  help         显示此帮助信息"
    echo ""
    echo "默认行为: 如果未指定命令,运行 GUI 程序"
    echo ""
    echo "Web 服务访问地址: http://localhost:5001"
    echo "支持手机和电脑浏览器访问"
}


if [ $# -eq 0 ]; then
    run_gui
else
    case "$1" in
        start)
            start_server
            ;;
        stop)
            stop_server
            ;;
        restart)
            restart_server
            ;;
        status)
            show_status
            ;;
        log)
            show_log
            ;;
        gui)
            run_gui
            ;;
        help)
            show_help
            ;;
        *)
            echo -e "${RED}✗ 未知命令: $1${NC}"
            show_help
            exit 1
            ;;
    esac
fi