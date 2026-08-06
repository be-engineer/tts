# Edge TTS 使用指南

## ✅ 已成功配置!

Edge TTS现在已经可以正常使用了!

---

## 🚀 快速开始

### 运行测试

```bash
# 直接运行(默认脚本)
./run.sh

# 或指定运行
./run.sh microsoft_edge_tts.py
```

### 输出文件

生成的音频文件: `edge_output.mp3`

播放音频:
```bash
# Linux
mpv edge_output.mp3
# 或
vlc edge_output.mp3

# Mac
open edge_output.mp3

# Windows
start edge_output.mp3
```

---

## 🎤 可用语音

Edge TTS提供15+种中文语音:

### 女声
- **xiaoxiao** (晓晓) - 温柔女声 ⭐推荐
- xiaoyi (晓伊)
- xiaochen (晓陈)
- xiaohan (晓涵)
- xiaomeng (晓梦)
- xiaomo (晓墨)
- xiaoqiu (晓秋)
- xiaorui (晓睿)
- xiaoshuang (晓双) - 儿童女声
- xiaoxuan (晓萱)
- xiaoyan (晓颜)
- xiaoyou (晓悠) - 儿童女声

### 男声
- **yunxi** (云希) - 沉稳男声 ⭐推荐
- yunjian (云健)
- yunxia (云夏)
- yunye (云野)
- yunze (云泽)

---

## 💡 使用示例

### 基础用法

```python
from microsoft_edge_tts import EdgeTTS

# 创建TTS客户端
tts = EdgeTTS(voice='xiaoxiao')

# 转换文本
tts.text_to_speech("你好,世界!", "output.mp3")
```

### 调整语速、音调

```python
tts.text_to_speech(
    text="你好,这是测试",
    output_file="output.mp3",
    rate='+10%',    # 加快10%
    volume='+20%',  # 增大20%
    pitch='+5Hz'    # 提高5Hz
)
```

### 批量处理

```python
texts = [
    "第一段文本",
    "第二段文本",
    "第三段文本"
]

tts = EdgeTTS(voice='xiaoxiao')
for i, text in enumerate(texts):
    tts.text_to_speech(text, f"output_{i}.mp3")
```

### 切换语音

```python
# 使用男声
tts = EdgeTTS(voice='yunxi')
tts.text_to_speech("你好", "male_voice.mp3")

# 使用儿童女声
tts = EdgeTTS(voice='xiaoshuang')
tts.text_to_speech("你好", "child_voice.mp3")
```

---

## 🔧 高级用法

### 查看所有可用语音

```python
from microsoft_edge_tts import EdgeTTS

tts = EdgeTTS()
tts.list_voices()
```

### 自定义参数

```python
# 慢速、低音调
tts.text_to_speech(
    text="慢慢说",
    output_file="slow.mp3",
    rate='-20%',
    pitch='-10Hz'
)

# 快速、高音调
tts.text_to_speech(
    text="快快说",
    output_file="fast.mp3",
    rate='+30%',
    pitch='+15Hz'
)
```

---

## ❓ 常见问题

### Q1: 为什么文件名是microsoft_edge_tts.py?

**A**: 避免与edge-tts库的名称冲突。如果命名为edge_tts.py,Python会导入我们的文件而不是库。

### Q2: 可以离线使用吗?

**A**: 不可以,Edge TTS需要网络连接来访问微软的服务。

### Q3: 有调用限制吗?

**A**: 目前免费且无明显限制,但建议不要高频滥用。

### Q4: 音质如何?

**A**: 非常好!接近真人发音,比大多数开源方案好。

### Q5: 支持其他语言吗?

**A**: 支持!Edge TTS支持100+语言和方言。

---

## 🎯 与其他方案对比

| 特性     | Edge TTS | Coqui TTS | 阿里云TTS |
| -------- | -------- | --------- | --------- |
| 费用     | ✅ 免费   | ✅ 免费    | ❌ 收费    |
| 需要网络 | ✅ 是     | ❌ 否      | ✅ 是      |
| 音质     | ⭐⭐⭐⭐⭐    | ⭐⭐⭐       | ⭐⭐⭐⭐⭐     |
| 速度     | ⭐⭐⭐⭐     | ⭐⭐        | ⭐⭐⭐⭐⭐     |
| 隐私     | ⚠️ 一般   | ✅ 好      | ⚠️ 一般    |

---

## 📝 代码位置

- **主脚本**: `microsoft_edge_tts.py`
- **依赖**: `requirements.txt` (已包含edge-tts)
- **文档**: `docs/FREE_TTS_COMPARISON.md`

---

## 🔗 相关资源

- [Edge TTS GitHub](https://github.com/rany2/edge-tts)
- [微软Azure TTS](https://azure.microsoft.com/services/cognitive-services/text-to-speech/)
- [项目文档](docs/FREE_TTS_COMPARISON.md)

---

**提示**: Edge TTS是目前最好用的免费TTS方案,推荐优先使用! 🎉
