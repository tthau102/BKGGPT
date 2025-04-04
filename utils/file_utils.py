import os
import json

def ensure_dir_exists(directory):
    """
    Đảm bảo thư mục tồn tại, tạo nếu cần.
    
    Args:
        directory: Đường dẫn thư mục
    """
    if not os.path.exists(directory):
        os.makedirs(directory)

def load_json(file_path, default=None):
    """
    Đọc file JSON từ đường dẫn.
    
    Args:
        file_path: Đường dẫn file JSON
        default: Giá trị mặc định nếu file không tồn tại
        
    Returns:
        dict: Dữ liệu JSON hoặc giá trị mặc định
    """
    if not os.path.exists(file_path):
        return default if default is not None else {}
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Lỗi khi đọc file {file_path}: {str(e)}")
        return default if default is not None else {}

def save_json(file_path, data, pretty=True):
    """
    Lưu dữ liệu vào file JSON.
    
    Args:
        file_path: Đường dẫn file JSON
        data: Dữ liệu cần lưu
        pretty: Định dạng JSON đẹp
    """
    try:
        # Đảm bảo thư mục tồn tại
        directory = os.path.dirname(file_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)
        
        # Ghi file
        with open(file_path, 'w', encoding='utf-8') as f:
            if pretty:
                json.dump(data, f, ensure_ascii=False, indent=2)
            else:
                json.dump(data, f, ensure_ascii=False)
    except Exception as e:
        print(f"Lỗi khi lưu file {file_path}: {str(e)}")