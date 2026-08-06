import os
import re
import uuid
import threading
import subprocess
from flask import Flask, render_template, request, jsonify, send_file, abort
from tts_core import VOICES, convert_file_to_speech

app = Flask(__name__)


def get_version_info():
    """统计项目自身提交次数作为 build 号，结合 SVN 最后修改日期自动拼装"""
    project_dir = os.path.dirname(os.path.abspath(__file__))
    build = ''
    date_part = ''
    # 统计项目目录的提交次数
    try:
        output = subprocess.check_output(
            ['svn', 'log', '-q', '--stop-on-copy', project_dir],
            text=True, stderr=subprocess.DEVNULL
        )
        build = str(len(re.findall(r'^r\d+ \|', output, re.MULTILINE)))
    except (subprocess.CalledProcessError, FileNotFoundError, Exception):
        pass
    # 从 SVN 获取最后修改日期
    try:
        date_str = subprocess.check_output(
            ['svn', 'info', '--show-item', 'last-changed-date', project_dir],
            text=True, stderr=subprocess.DEVNULL
        ).strip()
        if date_str:
            date_part = date_str.split('T')[0]
    except (subprocess.CalledProcessError, FileNotFoundError, Exception):
        pass
    # 拼装
    if build and date_part:
        return f"build {build} · {date_part}"
    elif build:
        return f"build {build}"
    elif date_part:
        return date_part
    else:
        return ""

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
OUTPUT_FOLDER = os.path.join(os.path.dirname(__file__), 'output')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

ALLOWED_EXTENSIONS = {'txt'}
ALLOWED_AUDIO_EXTENSIONS = {'mp3', 'wav', 'flac', 'm4a', 'ogg'}

tasks = {}
whisper_model = None


def load_whisper_model():
    global whisper_model
    if whisper_model is None:
        import whisper
        import os
        
        model_cache_dir = os.path.expanduser("~/.cache/whisper/")
        model_path = os.path.join(model_cache_dir, "small.pt")
        
        if not os.path.exists(model_path):
            print("⏳ 正在下载 Whisper small 模型（约466MB）...")
            os.makedirs(model_cache_dir, exist_ok=True)
            
            try:
                import wget
                model_url = "https://www.modelscope.cn/api/v1/models/openai-mirror/whisper-small/repo/files?file=small.pt"
                wget.download(model_url, model_path)
                print("\n✅ 模型下载完成")
            except ImportError:
                print("⚠️ 未安装 wget，尝试使用内置方式下载...")
        
        print("🔧 加载 Whisper 模型...")
        whisper_model = whisper.load_model("small", device="cpu")
        print("✅ Whisper 模型加载完成")
    return whisper_model


def convert_to_simplified(text):
    try:
        from zhconv import convert
        return convert(text, 'zh-cn')
    except ImportError:
        return text


def allowed_audio_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_AUDIO_EXTENSIONS


def format_time(seconds):
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = seconds % 60
    milliseconds = int((seconds - int(seconds)) * 1000)
    seconds = int(seconds)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d},{milliseconds:03d}"


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def run_conversion(task_id, files, voice, rate, volume, format_type):
    """在后台线程中执行转换"""
    try:
        output_files = []
        total = len(files)
        
        for idx, text_file in enumerate(files):
            filename = os.path.basename(text_file)
            progress = int((idx + 1) / total * 100)
            tasks[task_id] = {
                'status': 'processing',
                'progress': progress,
                'current_file': filename,
                'output_files': output_files
            }
            
            output_file = convert_file_to_speech(
                text_file, voice, rate, volume, OUTPUT_FOLDER, format_type
            )
            output_files.append(os.path.basename(output_file))
        
        tasks[task_id] = {
            'status': 'completed',
            'progress': 100,
            'current_file': None,
            'output_files': output_files
        }
    
    except Exception as e:
        tasks[task_id] = {
            'status': 'error',
            'progress': 0,
            'current_file': None,
            'error': str(e)
        }


@app.route('/')
def index():
    version = get_version_info()
    return render_template('index.html', voices=VOICES, version=version)


@app.route('/api/voices')
def get_voices():
    return jsonify(VOICES)


@app.route('/api/convert', methods=['POST'])
def convert():
    if 'files' not in request.files:
        return jsonify({'error': '请选择文件'}), 400
    
    files = request.files.getlist('files')
    if not files:
        return jsonify({'error': '请选择文件'}), 400
    
    voice = request.form.get('voice', 'zh-CN-XiaoxiaoNeural')
    rate = request.form.get('rate', 'normal')
    volume = request.form.get('volume', 'normal')
    format_type = request.form.get('format', 'mp3')
    
    task_id = str(uuid.uuid4())
    
    saved_files = []
    for file in files:
        if file and allowed_file(file.filename):
            filepath = os.path.join(UPLOAD_FOLDER, file.filename)
            file.save(filepath)
            saved_files.append(filepath)
    
    if not saved_files:
        return jsonify({'error': '请选择有效的文本文件'}), 400
    
    tasks[task_id] = {
        'status': 'processing',
        'progress': 0,
        'current_file': None,
        'output_files': []
    }
    
    thread = threading.Thread(
        target=run_conversion,
        args=(task_id, saved_files, voice, rate, volume, format_type)
    )
    thread.daemon = True
    thread.start()
    
    return jsonify({'task_id': task_id})


@app.route('/api/status/<task_id>')
def get_status(task_id):
    if task_id not in tasks:
        return jsonify({'error': '任务不存在'}), 404
    
    return jsonify(tasks[task_id])


@app.route('/api/download/<filename>')
def download_file(filename):
    filepath = os.path.join(OUTPUT_FOLDER, filename)
    if not os.path.exists(filepath):
        abort(404)
    
    response = send_file(filepath, as_attachment=True)
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response


@app.route('/api/preview', methods=['POST'])
def preview_voice():
    voice = request.form.get('voice', 'zh-CN-XiaoxiaoNeural')
    rate = request.form.get('rate', 'normal')
    volume = request.form.get('volume', 'normal')
    
    import asyncio
    from tts_core import convert_text_to_speech
    
    preview_file = os.path.join(OUTPUT_FOLDER, f'preview_{voice}.mp3')
    
    try:
        asyncio.run(convert_text_to_speech(
            '你好，这是语音预览。',
            voice,
            rate,
            volume,
            preview_file
        ))
        
        if os.path.exists(preview_file):
            return send_file(preview_file, mimetype='audio/mpeg')
        else:
            return jsonify({'error': '预览生成失败'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/download_all/<task_id>')
def download_all(task_id):
    if task_id not in tasks:
        return jsonify({'error': '任务不存在'}), 404
    
    task = tasks[task_id]
    if task['status'] != 'completed':
        return jsonify({'error': '任务未完成'}), 400
    
    output_files = task['output_files']
    if not output_files:
        return jsonify({'error': '没有生成的文件'}), 400
    
    first_file = output_files[0]
    filepath = os.path.join(OUTPUT_FOLDER, first_file)
    return send_file(filepath, as_attachment=True)


@app.route('/api/recognize', methods=['POST'])
def recognize():
    if 'files' not in request.files:
        return jsonify({'error': '请选择文件'}), 400
    
    files = request.files.getlist('files')
    if not files:
        return jsonify({'error': '请选择文件'}), 400
    
    saved_files = []
    for file in files:
        if file and allowed_audio_file(file.filename):
            filepath = os.path.join(UPLOAD_FOLDER, file.filename)
            file.save(filepath)
            saved_files.append(filepath)
    
    if not saved_files:
        return jsonify({'error': '请选择有效的音频文件'}), 400
    
    task_id = str(uuid.uuid4())
    
    tasks[task_id] = {
        'status': 'processing',
        'progress': 0,
        'current_file': None,
        'output_files': [],
        'transcripts': {}
    }
    
    def run_recognition():
        try:
            model = load_whisper_model()
            transcripts = {}
            
            for idx, audio_file in enumerate(saved_files):
                filename = os.path.basename(audio_file)
                progress = int((idx + 1) / len(saved_files) * 100)
                
                result = model.transcribe(audio_file, language="zh")
                
                simplified_text = convert_to_simplified(result["text"])
                
                txt_filename = os.path.splitext(filename)[0] + '.txt'
                txt_path = os.path.join(OUTPUT_FOLDER, txt_filename)
                with open(txt_path, 'w', encoding='utf-8') as f:
                    f.write(simplified_text)
                
                srt_filename = os.path.splitext(filename)[0] + '.srt'
                srt_path = os.path.join(OUTPUT_FOLDER, srt_filename)
                with open(srt_path, 'w', encoding='utf-8') as f:
                    for i, segment in enumerate(result["segments"], 1):
                        start = format_time(segment['start'])
                        end = format_time(segment['end'])
                        text = convert_to_simplified(segment['text'].strip())
                        f.write(f"{i}\n{start} --> {end}\n{text}\n\n")
                
                simplified_segments = []
                for seg in result["segments"]:
                    simplified_segments.append({
                        'start': seg['start'],
                        'end': seg['end'],
                        'text': convert_to_simplified(seg['text'])
                    })
                
                transcripts[filename] = {
                    'text': simplified_text,
                    'segments': simplified_segments,
                    'output_file': txt_filename,
                    'srt_file': srt_filename
                }
                
                tasks[task_id] = {
                    'status': 'processing',
                    'progress': progress,
                    'current_file': filename,
                    'output_files': list(transcripts.keys()),
                    'transcripts': transcripts
                }
            
            tasks[task_id] = {
                'status': 'completed',
                'progress': 100,
                'current_file': None,
                'output_files': list(transcripts.keys()),
                'transcripts': transcripts
            }
        
        except Exception as e:
            tasks[task_id] = {
                'status': 'error',
                'progress': 0,
                'current_file': None,
                'error': str(e)
            }
    
    thread = threading.Thread(target=run_recognition)
    thread.daemon = True
    thread.start()
    
    return jsonify({'task_id': task_id})


@app.route('/api/recognize_status/<task_id>')
def get_recognize_status(task_id):
    if task_id not in tasks:
        return jsonify({'error': '任务不存在'}), 404
    
    return jsonify(tasks[task_id])


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=False)