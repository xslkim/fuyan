from flask import Flask, request, render_template, send_from_directory
from werkzeug.utils import secure_filename
from PIL import Image
import os
import uuid
from test import dectedAndDraw
from test import face
from test import GetServerIP
from flask import Flask, jsonify
from FaceArk import GetPicDesc


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

def process_image(input_path, output_path):
    try:
        img = Image.open(input_path)
                
        gray_img = dectedAndDraw(img, input_path)

        
        gray_img.save(output_path)
        return True
    except Exception as e:
        print(f"Error processing image: {e}")
        return False
    

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
                
                if process_image(upload_path, processed_path):
                    processed_img = processed_filename
                else:
                    error = 'Error processing image'
            else:
                error = 'File type not allowed'
    
    return render_template('index.html', 
                         original_img=original_img,
                         processed_img=processed_img,
                         error=error)

@app.route('/face', methods=['GET', 'POST'])
def upload_file_face():
    error = None
    
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
                # upload_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
                
                save_path = os.path.join('/var/www/html/imgs', unique_filename)
                # 保存原始文件
                file.save(save_path)
                file.close()
                
                
                feature_point = face(save_path)

                url = f'http://{GetServerIP()}/imgs/{unique_filename}'
                face_figure = GetPicDesc(url)

                
                if feature_point == None:
                    data['ret'] = 'Failure'
                    data['msg'] = 'No Face'
                else:
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