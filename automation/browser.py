import os
import time
import random
import traceback
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

from utils.logging_utils import get_logger

class Browser:
    """Lớp quản lý trình duyệt tự động."""
    
    def __init__(self, headless=True, screenshots_dir="screenshots"):
        """
        Khởi tạo trình duyệt Chrome.
        
        Args:
            headless: Có chạy ở chế độ headless hay không
            screenshots_dir: Thư mục lưu screenshots
        """
        self.logger = get_logger(__name__)
        self.screenshots_dir = screenshots_dir
        
        # Tạo thư mục screenshots nếu chưa tồn tại
        if not os.path.exists(screenshots_dir):
            os.makedirs(screenshots_dir)
        
        # Thiết lập Chrome options
        self.chrome_options = Options()
        if headless:
            self.chrome_options.add_argument("--headless")
        
        self.chrome_options.add_argument("--no-sandbox")
        self.chrome_options.add_argument("--disable-dev-shm-usage")
        self.chrome_options.add_argument("--window-size=1920,1080")
        self.chrome_options.add_argument("--disable-gpu")
        self.chrome_options.add_argument("--disable-notifications")
        self.chrome_options.add_argument("--disable-popup-blocking")
        
        # Ẩn dấu hiệu automation
        self.chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        self.chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36")
        self.chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        self.chrome_options.add_experimental_option("useAutomationExtension", False)
        
        self.driver = None
        self.wait = None
    
    def start(self):
        """Khởi động trình duyệt."""
        self.logger.info("Đang khởi tạo WebDriver...")
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=self.chrome_options)
        self.wait = WebDriverWait(self.driver, 30)  # Tăng timeout lên 30s
        
        # Tùy chỉnh WebDriver để tránh phát hiện
        self.driver.execute_cdp_cmd("Network.setUserAgentOverride", {
            "userAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
        })
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        # Mở trình duyệt toàn màn hình
        self.driver.maximize_window()
        time.sleep(random.uniform(1.0, 2.0))
        
        return self
    
    def screenshot(self, filename):
        """
        Chụp ảnh màn hình.
        
        Args:
            filename: Tên file cần lưu
        """
        if self.driver:
            full_path = os.path.join(self.screenshots_dir, filename)
            self.driver.save_screenshot(full_path)
            self.logger.info(f"Đã chụp ảnh màn hình: {full_path}")
    
    def find_element_from_candidates(self, selector_list):
        """
        Tìm phần tử từ danh sách selector ứng viên.
        
        Args:
            selector_list: Danh sách các selector ứng viên
            
        Returns:
            WebElement hoặc None
        """
        for selector in selector_list:
            by_method = getattr(By, selector['by'].upper())
            try:
                element = self.wait.until(EC.presence_of_element_located((by_method, selector['value'])))
                self.logger.info(f"Tìm thấy phần tử với {selector['by']}='{selector['value']}'")
                return element
            except:
                continue
        
        return None
    
    def close(self):
        """Đóng trình duyệt."""
        if self.driver:
            # Đôi khi truy cập một trang khác trước khi thoát
            if random.random() < 0.3:  # 30% cơ hội
                self.driver.get("https://photos.google.com")
                time.sleep(random.uniform(2.0, 4.0))
            
            self.driver.quit()
            self.logger.info("Đã đóng WebDriver")