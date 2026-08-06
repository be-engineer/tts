#根据https://github.com/smallnew666/edge-tts-ui 产生静音方法
import os
import re
import asyncio
import edge_tts

VOICES = {
    'zh-CN-XiaoxiaoNeural': '晓晓 (女声)',
    'zh-CN-XiaoyiNeural': '晓伊 (女声)',
    'zh-CN-YunjianNeural': '云健 (男声)',
    'zh-CN-YunxiNeural': '云希 (男声)',
    'zh-CN-YunxiaNeural': '云夏 (男声)',
    'zh-CN-YunyangNeural': '云阳 (男声)',
    'zh-CN-liaoning-XiaobeiNeural': '小北 (辽宁方言)',
    'zh-CN-shaanxi-XiaoniNeural': '小妮 (陕西方言)'
}

"""
生成静音音频数据（MP3格式）

工作原理：
1. 计算静音时长对应的采样帧数：num_frames = sample_rate * duration_ms / 1000
2. 创建静音采样数据：全部用0填充（b'\x00'），0表示没有声音波形
3. 使用 lameenc 编码器将PCM原始音频编码为MP3格式
4. 返回编码后的MP3字节数据，可直接拼接到其他音频数据中

参数说明：
- duration_ms: 静音时长（毫秒）
- sample_rate: 采样率，默认24000（edge-tts使用的采样率）
- bit_depth: 位深度，默认16位

为什么不用SSML的<break>标签？
edge-tts库不支持自定义SSML（官方已移除该功能），因此需要手动生成静音音频
并与语音片段合并，实现停顿效果。

:param duration_ms: 静音时长（毫秒）
:param sample_rate: 采样率，默认24000
:param bit_depth: 位深度，默认16
:return: 静音MP3字节数据
"""
def generate_silence(duration_ms, sample_rate=24000, bit_depth=16):

    num_frames = int(sample_rate * duration_ms / 1000)
    silent_frame = b'\x00' * (bit_depth // 8) * num_frames

    try:
        import lameenc
        encoder = lameenc.Encoder()
        encoder.set_channels(1)
        encoder.set_in_sample_rate(sample_rate)
        encoder.set_bit_rate(128)
        encoder.set_out_sample_rate(sample_rate)
        encoder.set_quality(2)

        mp3_data = encoder.encode(silent_frame)
        mp3_data += encoder.flush()
        return mp3_data
    except ImportError:
        raise ImportError(
            "停顿功能依赖 lameenc 库，请执行: pip install lameenc"
        )


def get_rate_value(rate):
    """获取语速值"""
    rate_mapping = {
        'fast': '+20%',
        'slow': '-20%',
        'normal': '+0%'
    }
    return rate_mapping.get(rate, '+0%')


def get_volume_value(volume):
    """获取音量值"""
    volume_mapping = {
        'loud': '+20%',
        'quiet': '-20%',
        'normal': '+0%'
    }
    return volume_mapping.get(volume, '+0%')


async def convert_text_to_speech(text, voice, rate, volume, output_file):
    """
    将文本转换为语音（支持 {pause=xxx} 停顿标记）
    :param text: 要转换的文本
    :param voice: 语音ID
    :param rate: 语速 (fast/slow/normal)
    :param volume: 音量 (loud/quiet/normal)
    :param output_file: 输出文件路径
    :return: 输出文件路径
    """
    rate_value = get_rate_value(rate)
    volume_value = get_volume_value(volume)

    segments = re.split(r'(\{pause=\d+\})', text)
    combined_audio = b''

    for segment in segments:
        if re.match(r'\{pause=\d+\}', segment):
            pause_duration = int(re.search(r'\d+', segment).group())
            silence = await asyncio.to_thread(generate_silence, pause_duration)
            combined_audio += silence
        elif segment.strip():
            communicate = edge_tts.Communicate(
                segment,
                voice,
                rate=rate_value,
                volume=volume_value
            )
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    combined_audio += chunk["data"]

    with open(output_file, "wb") as f:
        f.write(combined_audio)

    import subprocess
    subprocess.run(
        ['ffmpeg', '-y', '-i', output_file, '-ac', '1', '-ar', '24000',
         '-b:a', '48k', '-f', 'mp3', f"{output_file}.tmp.mp3"],
        capture_output=True
    )
    
    import os
    os.replace(f"{output_file}.tmp.mp3", output_file)

    return output_file


def convert_file_to_speech(text_file, voice, rate, volume, output_dir, format_type='mp3'):
    """
    将文本文件转换为语音
    :param text_file: 文本文件路径
    :param voice: 语音ID
    :param rate: 语速 (fast/slow/normal)
    :param volume: 音量 (loud/quiet/normal)
    :param output_dir: 输出目录
    :param format_type: 输出格式 (mp3/wav)
    :return: 输出文件路径
    """
    os.makedirs(output_dir, exist_ok=True)

    with open(text_file, 'r', encoding='utf-8') as f:
        text = f.read()

    filename = os.path.basename(text_file)
    base_name = os.path.splitext(filename)[0]
    voice_name = voice.replace('-', '_')
    output_file = os.path.join(output_dir, f"{base_name}_{voice_name}.{format_type}")

    max_retries = 3
    retry_count = 0
    last_error = None

    while retry_count < max_retries:
        try:
            asyncio.run(convert_text_to_speech(text, voice, rate, volume, output_file))
            return output_file
        except Exception as e:
            last_error = str(e)
            retry_count += 1
            if retry_count < max_retries:
                import time
                time.sleep(2)
            else:
                raise Exception(f"转换失败（已重试{max_retries}次）: {last_error}")