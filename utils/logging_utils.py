import logging
import os
from datetime import datetime

def get_logger(name, log_file=None, level=logging.INFO):
    """
    Tạo logger với cấu hình chuẩn.
    
    Args:
        name: Tên của logger
        log_file: Đường dẫn file log, mặc định là None (sử dụng file mặc định)
        level: Mức độ log
        
    Returns:
        logging.Logger: Logger đã cấu hình
    """
    # Tạo thư mục logs nếu chưa tồn tại
    logs_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs")
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)
    
    # Nếu không có log_file cụ thể, tạo tên file dựa trên timestamp
    if log_file is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = os.path.join(logs_dir, f"backup_photos_{timestamp}.log")
    elif not os.path.isabs(log_file):
        log_file = os.path.join(logs_dir, log_file)
    
    # Tạo logger
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Xóa handlers cũ nếu có
    if logger.handlers:
        logger.handlers = []
    
    # Tạo file handler
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(level)
    
    # Tạo console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    
    # Định dạng log
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # Thêm handlers vào logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

def setup_global_logging(level=logging.INFO):
    """
    Thiết lập cấu hình logging cho toàn bộ ứng dụng.
    
    Args:
        level: Mức độ log
        
    Returns:
        logging.Logger: Root logger
    """
    # Đảm bảo thư mục logs tồn tại
    logs_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs")
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)
        
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(logs_dir, f"backup_photos_{timestamp}.log")
    
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    
    return logging.getLogger()