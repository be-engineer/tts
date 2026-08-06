'''
Author       : Leon Lee
Date         : 2026-07-19 15:45:47
LastEditors  : Leon
LastEditTime : 2026-07-19 16:11:50
Description  : file content
FilePath     : /tts/test_whisper.py
'''
import whisper
import os
import sys
import time

def test_whisper(audio_file=None):
    print("=" * 60)
    print("🔊 Whisper 语音识别测试程序")
    print("=" * 60)
    
    if audio_file:
        if os.path.exists(audio_file):
            test_audio = audio_file
        else:
            print(f"❌ 文件不存在: {audio_file}")
            sys.exit(1)
    else:
        test_audio = None
        for ext in [".wav", ".mp3", ".flac", ".m4a"]:
            for f in os.listdir("."):
                if f.lower().endswith(ext):
                    test_audio = f
                    break
            if test_audio:
                break
        
        if test_audio and os.path.exists(test_audio):
            print(f"\n🎵 找到测试音频文件: {test_audio}")
        else:
            print("\n⚠️  未找到音频文件，请指定文件名:")
            print("  python test_whisper.py your_audio.mp3")
            sys.exit(1)
    
    print("\n📥 正在加载 small 模型...")
    start_time = time.time()
    
    try:
        model = whisper.load_model("small")
        load_time = time.time() - start_time
        print(f"✅ 模型加载成功! 耗时: {load_time:.2f}秒")
    except Exception as e:
        print(f"❌ 模型加载失败: {e}")
        print("\n💡 提示: 首次运行需要下载模型，可能需要较长时间")
        print("如果下载失败，可以手动从 ModelScope 下载:")
        print("https://www.modelscope.cn/models/openai-mirror/whisper-small/files")
        print("下载后放到 ~/.cache/whisper/ 目录")
        sys.exit(1)
    
    print("\n🔍 正在识别音频...")
    start_time = time.time()
    
    try:
        result = model.transcribe(test_audio, language="zh", verbose=True)
        transcribe_time = time.time() - start_time
        
        print("\n" + "=" * 60)
        print("📝 识别结果:")
        print("=" * 60)
        print(result["text"])
        
        print("\n📊 分段结果（带时间戳）:")
        for i, segment in enumerate(result["segments"], 1):
            start = segment["start"]
            end = segment["end"]
            text = segment["text"]
            print(f"  [{i}] {start:.2f}s - {end:.2f}s: {text}")
        
        print("\n⏱️ 识别耗时: {:.2f}秒".format(transcribe_time))
        print("📊 音频时长: {:.2f}秒".format(result["segments"][-1]["end"] if result["segments"] else 0))
        
        output_file = os.path.splitext(test_audio)[0] + ".txt"
        with open(output_file, "w", encoding="utf-8") as f:
            f.write("=" * 60 + "\n")
            f.write("Whisper 语音识别结果\n")
            f.write("源文件: " + test_audio + "\n")
            f.write("识别时间: " + time.strftime("%Y-%m-%d %H:%M:%S") + "\n")
            f.write("=" * 60 + "\n\n")
            f.write("全文识别:\n")
            f.write(result["text"] + "\n\n")
            f.write("分段识别（带时间戳）:\n")
            for i, segment in enumerate(result["segments"], 1):
                start = segment["start"]
                end = segment["end"]
                text = segment["text"]
                f.write(f"  [{i}] {start:.2f}s - {end:.2f}s: {text}\n")
        
        print(f"\n💾 结果已保存到: {output_file}")
        
    except Exception as e:
        print(f"❌ 识别失败: {e}")
        print("\n💡 可能需要安装 ffmpeg:")
        print("  Ubuntu/Debian: sudo apt install ffmpeg")
        print("  macOS: brew install ffmpeg")
        print("  Windows: 下载 ffmpeg 并添加到 PATH")
        sys.exit(1)

if __name__ == "__main__":
    audio_file = sys.argv[1] if len(sys.argv) > 1 else None
    test_whisper(audio_file)
