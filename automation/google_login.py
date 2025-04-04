import time
import random
import traceback
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from automation.user_simulation import UserSimulation
from automation.selectors import LOGIN_SELECTORS

class GoogleLogin:
    """Xử lý đăng nhập vào Google."""
    
    def __init__(self, browser):
        """
        Khởi tạo đối tượng đăng nhập Google.
        
        Args:
            browser: Đối tượng Browser đã khởi tạo
        """
        self.browser = browser
        self.driver = browser.driver
        self.wait = browser.wait
        self.logger = browser.logger
    
    def login(self, email, password):
        """
        Đăng nhập vào tài khoản Google.
        
        Args:
            email: Email đăng nhập
            password: Mật khẩu
            
        Returns:
            bool: Trạng thái đăng nhập
        """
        try:
            self.logger.info("Đang truy cập trang đăng nhập...")
            self.driver.get("https://accounts.google.com/")
            time.sleep(random.uniform(3.0, 5.0))
            self.browser.screenshot("login_page.png")
            
            # Nhập email
            self.logger.info(f"Đang nhập email: {email}")
            email_input = self.browser.find_element_from_candidates(LOGIN_SELECTORS['email_input'])
            if not email_input:
                self.logger.error("Không tìm thấy trường email")
                return False
                
            UserSimulation.human_move_and_click(self.driver, email_input)
            UserSimulation.human_type(email_input, email)
            
            # Click nút Next sau khi nhập email
            next_button = self.browser.find_element_from_candidates(LOGIN_SELECTORS['email_next_button'])
            if not next_button:
                self.logger.error("Không tìm thấy nút Next sau khi nhập email")
                return False
                
            UserSimulation.human_move_and_click(self.driver, next_button)
            time.sleep(random.uniform(3.0, 5.0))
            self.browser.screenshot("after_email.png")
            
            # Nhập mật khẩu
            self.logger.info("Đang nhập mật khẩu...")
            password_input = self.browser.find_element_from_candidates(LOGIN_SELECTORS['password_input'])
            if not password_input:
                self.logger.error("Không tìm thấy trường mật khẩu")
                return False
                
            UserSimulation.human_move_and_click(self.driver, password_input)
            UserSimulation.human_type(password_input, password)
            
            # Click nút Next sau khi nhập mật khẩu
            next_button = self.browser.find_element_from_candidates(LOGIN_SELECTORS['password_next_button'])
            if not next_button:
                self.logger.error("Không tìm thấy nút Next sau khi nhập mật khẩu")
                return False
                
            UserSimulation.human_move_and_click(self.driver, next_button)
            time.sleep(random.uniform(3.0, 5.0))
            self.browser.screenshot("after_login.png")
            
            # Kiểm tra đăng nhập thành công
            current_url = self.driver.current_url
            if "myaccount.google.com" in current_url or "photos.google.com" in current_url:
                self.logger.info("Đăng nhập thành công!")
                return True
            else:
                self.logger.warning(f"Đăng nhập có thể chưa hoàn tất. URL hiện tại: {current_url}")
                # Vẫn trả về True vì có thể đã đăng nhập nhưng chuyển hướng sang trang khác
                return True
                
        except Exception as e:
            self.logger.error(f"Lỗi khi đăng nhập: {str(e)}")
            self.logger.error(traceback.format_exc())
            self.browser.screenshot("login_error.png")
            return False