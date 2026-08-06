'''
Author       : Leon Lee
Date         : 2026-07-19 19:51:20
LastEditors  : Leon
LastEditTime : 2026-07-19 21:48:01
Description  : file content
FilePath     : /tts/test_tts_pause.py
'''
import os
import asyncio
from tts_core import convert_text_to_speech, generate_silence

TEST_TEXT = "床前明月光，疑是地上霜。举头望明月，低头思故乡。"

PAUSE_TESTS = {
    'original': TEST_TEXT,
    
    'pause_300': "床前明月光，{pause=300}疑是地上霜。{pause=300}举头望明月，{pause=300}低头思故乡。",
    
    'pause_500': "床前明月光，{pause=500}疑是地上霜。{pause=500}举头望明月，{pause=500}低头思故乡。",
    
    'pause_1000': "床前明月光，{pause=1000}疑是地上霜。{pause=1000}举头望明月，{pause=1000}低头思故乡。",
    
    'mixed_pause': "床前明月光，{pause=200}疑是地上霜。{pause=500}举头望明月，{pause=300}低头思故乡。{pause=800}",
    
    'sentence_pause': "床前明月光。{pause=500}疑是地上霜。{pause=500}举头望明月。{pause=500}低头思故乡。",
}


async def test_pause_effect(voice, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    
    print("=" * 60)
    print("TTS 停顿效果测试（使用 {pause=xxx} 标记）")
    print("=" * 60)
    print(f"语音: {voice}")
    print(f"输出目录: {output_dir}")
    print()
    
    for test_name, text in PAUSE_TESTS.items():
        output_file = os.path.join(output_dir, f"test_{test_name}.mp3")
        
        print(f"正在生成: {test_name}")
        print(f"  文本: {text[:50]}..." if len(text) > 50 else f"  文本: {text}")
        
        try:
            await convert_text_to_speech(text, voice, 'normal', 'normal', output_file)
            file_size = os.path.getsize(output_file) / 1024
            print(f"  ✅ 生成成功: {output_file} ({file_size:.2f} KB)")
        except Exception as e:
            print(f"  ❌ 生成失败: {e}")
        print()
    
    print("=" * 60)
    print("测试完成！请对比生成的音频文件")
    print("=" * 60)
    print()
    print("测试类型说明:")
    print("  original: 原始文本，无停顿")
    print("  pause_300: 每句后停顿300ms")
    print("  pause_500: 每句后停顿500ms")
    print("  pause_1000: 每句后停顿1000ms")
    print("  mixed_pause: 混合停顿（200/500/300/800ms）")
    print("  sentence_pause: 句号后停顿500ms")


if __name__ == "__main__":
    import sys
    
    voice = "zh-CN-XiaoxiaoNeural"
    if len(sys.argv) > 1:
        voice = sys.argv[1]
    
    output_dir = "output/tts_pause_test"
    
    asyncio.run(test_pause_effect(voice, output_dir))