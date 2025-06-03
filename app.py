from flask import Flask, request, render_template, send_from_directory
from werkzeug.utils import secure_filename
from PIL import Image
import os
import uuid
from test import draw_landmarks_on_image
from test import face
from test import GetServerIP
from flask import Flask, jsonify
from FaceArk import GetPicDesc
from FaceArk import GetFinalData


# 设置静态文件夹路径
APP_ROOT = os.path.dirname(os.path.abspath(__file__))
STATIC_FOLDER = os.path.join(APP_ROOT, 'static')

app = Flask(__name__)

# 配置
UPLOAD_FOLDER = 'uploads'
PROCESSED_FOLDER = 'processed'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['PROCESSED_FOLDER'] = PROCESSED_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 限制上传大小为16MB

# 确保文件夹存在
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/processed/<filename>')
def processed_file(filename):
    return send_from_directory(app.config['PROCESSED_FOLDER'], filename)

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    original_img = None
    processed_img = None
    error = None
    
    if request.method == 'POST':
        # 检查是否有文件部分
        if 'file' not in request.files:
            error = 'No file part'
        else:
            file = request.files['file']
            
            # 检查是否选择了文件
            if file.filename == '':
                error = 'No selected file'
            elif file and allowed_file(file.filename):
                # 生成唯一文件名
                file_ext = file.filename.rsplit('.', 1)[1].lower()
                unique_filename = f"{uuid.uuid4().hex}.{file_ext}"
                upload_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
                
                # 保存原始文件
                file.save(upload_path)
                original_img = unique_filename
                
                # 处理图片
                processed_filename = f"processed_{unique_filename}"
                processed_path = os.path.join(app.config['PROCESSED_FOLDER'], processed_filename)
                
                img = Image.open(upload_path)
                gray_img = draw_landmarks_on_image(img, upload_path)
                gray_img.save(processed_path)
            else:
                error = 'File type not allowed'
    
    return render_template('index.html', 
                         original_img=original_img,
                         processed_img=processed_img,
                         error=error)

@app.route('/test_line', methods=['GET', 'POST'])
def upload_file_line():
    original_img = None
    processed_img = None
    error = None
    
    if request.method == 'POST':
        # 检查是否有文件部分
        if 'file' not in request.files:
            error = 'No file part'
        else:
            file = request.files['file']
            
            # 检查是否选择了文件
            if file.filename == '':
                error = 'No selected file'
            elif file and allowed_file(file.filename):
                # 生成唯一文件名
                file_ext = file.filename.rsplit('.', 1)[1].lower()
                unique_filename = f"{uuid.uuid4().hex}.{file_ext}"
                save_path = os.path.join('/var/www/html/imgs', unique_filename)
                # 保存原始文件
                file.save(save_path)
                file.close()

                # 处理图片
                processed_filename = f"processed_{unique_filename}"
                processed_path = os.path.join(app.config['PROCESSED_FOLDER'], processed_filename)

                url = f'http://{GetServerIP()}/imgs/{unique_filename}'
                fire_ret = GetPicDesc(url)
                original_img = Image.open(save_path)

                final_data = GetFinalData(fire_ret, save_path, original_img.width, original_img.height)
                processed_img = dectedAndDrawLine(processed_img, final_data)
                processed_img.save(processed_path)

            else:
                error = 'File type not allowed'
    
    return render_template('index.html', 
                         original_img=unique_filename,
                         processed_img=processed_filename,
                         error=error)

@app.route('/face', methods=['GET', 'POST'])
def upload_file_face():
    if request.method == 'POST':
        data = {}
        # 检查是否有文件部分
        if 'file' not in request.files:
            error = 'No file part'
            data['ret'] = 'Failure'
            data['msg'] = error
        else:
            file = request.files['file']
            
            # 检查是否选择了文件
            if file.filename == '':
                error = 'No selected file'
                data['ret'] = 'Failure'
                data['msg'] = error
            elif file and allowed_file(file.filename):
                # 生成唯一文件名
                file_ext = file.filename.rsplit('.', 1)[1].lower()
                unique_filename = f"{uuid.uuid4().hex}.{file_ext}"
 
                save_path = os.path.join('/var/www/html/imgs', unique_filename)
                # 保存原始文件
                file.save(save_path)
                file.close()

                feature_point = face(save_path)

                url = f'http://{GetServerIP()}/imgs/{unique_filename}'
                face_figure = GetPicDesc(url)

                
                data['ret'] = 'Success'
                data['msg'] = ''
                data['feature_point'] = feature_point
                data['face_figure'] = face_figure
                    
            else:
                error = 'File type not allowed'
                data['ret'] = 'Failure'
                data['msg'] = error
    try:
        jsonstr = jsonify(data)
        return jsonstr
    except Exception as e:
        return 'jsonify Error'

    

@app.route('/test_face')
def index():
    # 返回HTML文件
    return send_from_directory(STATIC_FOLDER, 'test_face.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)