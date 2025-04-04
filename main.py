#!/usr/bin/env python3
"""
BKGGPT: Công cụ backup Google Photos tự động
"""

import os
import argparse
import time

from config.settings import GOOGLE_EMAIL, GOOGLE_PASSWORD, ALBUM_URL, HEADLESS_MODE, SCREENSHOTS_DIR
from auth.google_auth import GoogleAuth
from api.photos_api import GooglePhotosAPI
from automation.browser import Browser
from utils.logging_utils import setup_global_logging, get_logger
from utils.file_utils import ensure_dir_exists

def get_albums_list():
    """Lấy danh sách album từ Google Photos API."""
    logger = get_logger("get_albums")
    
    # Xác thực với Google
    auth = GoogleAuth()
    auth.authenticate()
    
    # Khởi tạo Google Photos API
    photos_api = GooglePhotosAPI(auth)
    
    # Lấy danh sách album
    albums, next_page_token = photos_api.get_albums()
    
    # Lấy danh sách album được chia sẻ
    shared_albums, shared_next_page_token = photos_api.get_shared_albums()
    
    logger.info(f"Đã lấy {len(albums)} album thường và {len(shared_albums)} album được chia sẻ")
    
    return albums, shared_albums

def clone_album(album_url=None):
    """
    Sao chép media từ album được chia sẻ vào tài khoản backup.
    
    Args:
        album_url: URL của album, mặc định lấy từ cấu hình
    """
    # Đảm bảo thư mục screenshots tồn tại
    ensure_dir_exists(SCREENSHOTS_DIR)
    
    # Thiết lập logging
    logger = get_logger("clone_album")
    logger.info("Bắt đầu sao chép album")
    
    if not album_url:
        album_url = ALBUM_URL
    
    if not album_url:
        logger.error("Không có URL album. Hãy cung cấp qua tham số hoặc biến môi trường ALBUM_URL")
        return False
    
    if not GOOGLE_EMAIL or not GOOGLE_PASSWORD:
        logger.error("Vui lòng đặt biến môi trường GOOGLE_EMAIL và GOOGLE_PASSWORD")
        return False
    
    try:
        # Khởi tạo trình duyệt
        browser = Browser(headless=HEADLESS_MODE, screenshots_dir=SCREENSHOTS_DIR)
        browser.start()
        
        # Đăng nhập
        logger.info(f"Đăng nhập với tài khoản {GOOGLE_EMAIL}")
        if not browser.login(GOOGLE_EMAIL, GOOGLE_PASSWORD):
            logger.error("Đăng nhập thất bại")
            browser.close()
            return False
        
        # Truy cập trang chủ Google Photos (tùy chọn)
        browser.visit_photos_homepage()
        
        # Truy cập album
        logger.info(f"Truy cập album: {album_url}")
        if not browser.access_album(album_url):
            logger.error("Không thể truy cập album")
            browser.close()
            return False
        
        # Lưu ảnh
        logger.info("Đang lưu ảnh từ album")
        if not browser.save_photos():
            logger.error("Không thể lưu ảnh")
            browser.close()
            return False
        
        logger.info("Hoàn thành sao chép album!")
        
        # Đóng browser
        browser.close()
        return True
        
    except Exception as e:
        logger.error(f"Lỗi khi sao chép album: {str(e)}")
        return False

def main():
    """Hàm chính của ứng dụng."""
    # Thiết lập logging
    setup_global_logging()
    logger = get_logger("main")
    
    # Parse tham số dòng lệnh
    parser = argparse.ArgumentParser(description="BKGGPT: Công cụ backup Google Photos tự động")
    subparsers = parser.add_subparsers(dest="command", help="Lệnh cần thực hiện")
    
    # Subcommand: list - Lấy danh sách album
    list_parser = subparsers.add_parser("list", help="Lấy danh sách album")
    
    # Subcommand: clone - Sao chép album
    clone_parser = subparsers.add_parser("clone", help="Sao chép album")
    clone_parser.add_argument("--url", help="URL của album cần sao chép")
    
    args = parser.parse_args()
    
    # Thực hiện lệnh
    if args.command == "list":
        get_albums_list()
    elif args.command == "clone":
        clone_album(args.url)
    else:
        # Mặc định nếu không có tham số
        parser.print_help()

if __name__ == "__main__":
    main()