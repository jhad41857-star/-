import os
from flask import Flask, render_template, request, send_file, after_this_request
import yt_dlp

app = Flask(__name__)

# إنشاء مجلد للتحميلات إذا لم يكن موجوداً
DOWNLOAD_FOLDER = 'downloads'
if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download():
    url = request.form.get('video_url')
    if not url:
        return "يرجى إدخال رابط الفيديو"

    try:
        # إعدادات التحميل لجعلها متوافقة مع السيرفر
        ydl_opts = {
            'format': 'best',
            'outtmpl': f'{DOWNLOAD_FOLDER}/%(title)s.%(ext)s',
            'restrictfilenames': True,
            'noplaylist': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file_path = ydl.prepare_filename(info)

        # حذف الملف من السيرفر فور إرساله للمستخدم للحفاظ على المساحة
        @after_this_request
        def remove_file(response):
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
            except Exception as error:
                print(f"Error deleting file: {error}")
            return response

        return send_file(file_path, as_attachment=True)

    except Exception as e:
        return f"حدث خطأ أثناء التحميل: {str(e)}"

if __name__ == '__main__':
    # التشغيل على بورت متوافق مع الاستضافات العالمية
