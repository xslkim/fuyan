from flask import Flask, request, render_template, send_from_directory
from werkzeug.utils import secure_filename
from PIL import Image
import io
import os
import uuid
from test import draw_landmarks_on_image
from test import face
from test import GetServerIP
from test import draw_line_on_image
from flask import Flask, jsonify
from FaceArk import GetPicDesc
from FaceArk import GetFinalData
from FaceArk import GetClothDesc
from flask_cors import CORS
from datetime import datetime
import requests


# 设置静态文件夹路径
APP_ROOT = os.path.dirname(os.path.abspath(__file__))
STATIC_FOLDER = os.path.join(APP_ROOT, 'static')

app = Flask(__name__)

CORS(app)

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
                processed_img = processed_filename
                
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

                
                original_img = unique_filename

                # 处理图片
                processed_filename = f"processed_{unique_filename}"
                processed_path = os.path.join(app.config['PROCESSED_FOLDER'], processed_filename)
                

                url = f'http://{GetServerIP()}/imgs/{unique_filename}'
                fire_ret = GetPicDesc(url)
                img = Image.open(save_path)
                upload_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
                img.save(upload_path)

                if '图片是否有人' in fire_ret:
                    if '有人' in fire_ret['图片是否有人']:
                        final_data = GetFinalData(fire_ret, save_path, img.width, img.height)
                        out_img = draw_line_on_image(img, final_data)
                
                
                out_img.save(processed_path)
                processed_img = processed_filename

            else:
                error = 'File type not allowed'
    
    return render_template('index.html', 
                         original_img=original_img,
                         processed_img=processed_img,
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

                url = f'http://{GetServerIP()}/imgs/{unique_filename}'
                fire_ret = GetPicDesc(url)
                img = Image.open(save_path)

                final_data = {'图片是否有人':'没人'}
                if '图片是否有人' in fire_ret:
                    if '有人' in fire_ret['图片是否有人']:
                        final_data = GetFinalData(fire_ret, save_path, img.width, img.height)

                
                data['ret'] = 'Success'
                data['msg'] = ''
                data['data'] = final_data
                    
            else:
                error = 'File type not allowed'
                data['ret'] = 'Failure'
                data['msg'] = error
    try:
        jsonstr = jsonify(data)
        return jsonstr
    except Exception as e:
        return 'jsonify Error'


def allowed_file(filename):
    """检查文件扩展名是否合法"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def generate_filename(url):
    """生成唯一的文件名"""
    ext = url.split('.')[-1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        ext = 'jpg'  # 默认扩展名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    unique_id = str(uuid.uuid4())[:8]
    return f"{timestamp}_{unique_id}.{ext}"

@app.route('/face_url', methods=['GET'])
def face_url():
    image_url = request.args.get('url')
    
    if not image_url:
        return jsonify({'error': 'Missing image URL parameter'}), 400
    
    try:
        # 下载图片
        response = requests.get(image_url, stream=True)
        response.raise_for_status()
        
        # 检查内容类型是否为图片
        content_type = response.headers.get('content-type', '')
        if 'image' not in content_type:
            return jsonify({'error': 'URL does not point to an image'}), 400
        
        # 打开图片进行分析
        img = Image.open(io.BytesIO(response.content))
        
        # 生成保存的文件名
        filename = generate_filename(image_url)
        save_path = os.path.join('/var/www/html/imgs', filename)
        
        # 保存图片（保持原始格式）
        img.save(save_path, format=img.format if img.format else 'JPEG')
        data  = {}
        fire_ret = GetPicDesc(image_url)
        # img = Image.open(save_path)

        final_data = {'图片是否有人':'没人'}
        if '图片是否有人' in fire_ret:
            if '有人' in fire_ret['图片是否有人']:
                final_data = GetFinalData(fire_ret, save_path, img.width, img.height)

        data['ret'] = 'Success'
        data['msg'] = ''
        data['data'] = final_data
        
        try:
            jsonstr = jsonify(data)
            return jsonstr
        except Exception as e:
            return 'jsonify Error'
    
    except requests.exceptions.RequestException as e:
        return jsonify({'error': f'Failed to download image: {str(e)}'}), 400
    except IOError as e:
        return jsonify({'error': f'Error processing image: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'error': f'Unexpected error: {str(e)}'}), 500
    

@app.route('/test_face')
def index():
    # 返回HTML文件
    return send_from_directory(STATIC_FOLDER, 'test_face.html')


@app.route('/test_cloth', methods=['POST'])
def test_cloth():
    # 检查是否有文件上传
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    
    # 检查文件名是否为空
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    # 检查文件是否为图片
    if not file.filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
        return jsonify({'error': 'Unsupported file format'}), 400
    
    try:
        # 生成唯一文件名
        file_ext = file.filename.rsplit('.', 1)[1].lower()
        unique_filename = f"{uuid.uuid4().hex}.{file_ext}"

        save_path = os.path.join('/var/www/html/imgs', unique_filename)
        # 保存原始文件
        file.save(save_path)
        file.close()

        url = f'http://{GetServerIP()}/imgs/{unique_filename}'
        clothDesc = GetClothDesc(url)

        img = Image.open(save_path)
        original_format = img.format
        original_mode = img.mode
        original_size = img.size
        original_width, original_height = original_size
        gray_img = img.convert('L')

        # 保存处理后的图片
        processed_filename = f"processed_{unique_filename}"
        processed_path = os.path.join('/var/www/html/imgs', processed_filename)
        gray_img.save(processed_path, format='JPEG')
        process_url = f'http://{GetServerIP()}/imgs/{processed_filename}'
        
        # 准备返回的JSON数据
        result = {
            'status': 'success',
            'original': {
                'filename': unique_filename,
                'format': original_format,
                'mode': original_mode,
                'width': original_width,
                'height': original_height,
                'size': original_size,
                'clothDesc':clothDesc
            },
            'processed': {
                'filename': processed_filename,
                'url': process_url,
                'format': 'JPEG',
                'mode': 'L',
                'width': original_width,
                'height': original_height,
                'processing_time_seconds': 2
            },
            'message': 'Image successfully converted to grayscale'
        }
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500
    

@app.route('/cloth', methods=['POST'])
def cloth():
    # 检查是否有文件上传
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    
    # 检查文件名是否为空
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    # 检查文件是否为图片
    if not file.filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
        return jsonify({'error': 'Unsupported file format'}), 400
    
    try:
        # 生成唯一文件名
        file_ext = file.filename.rsplit('.', 1)[1].lower()
        unique_filename = f"{uuid.uuid4().hex}.{file_ext}"

        save_path = os.path.join('/var/www/html/imgs', unique_filename)
        # 保存原始文件
        file.save(save_path)
        file.close()

        url = f'http://{GetServerIP()}/imgs/{unique_filename}'
        clothDesc = GetClothDesc(url)
        data = {}
        data['ret'] = 'Success'
        data['msg'] = ''
        data['data'] = clothDesc
        
        return jsonify(data) 
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)