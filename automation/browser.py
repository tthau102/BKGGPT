import os
import time
import random
import logging
import traceback
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager

from automation.user_simulation import UserSimulation
from automation.selectors import LOGIN_SELECTORS, ALBUM_SELECTORS
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
            self.logger.info("Đang đăng nhập vào Google...")
            self.driver.get("https://accounts.google.com/signin")
            
            # Đợi trang tải với thời gian biến đổi
            time.sleep(random.uniform(2.0, 4.0))
            self.screenshot("login_page.png")
            
            # Nhập email
            self.logger.info("Đang tìm trường nhập email...")
            email_input = self.find_element_from_candidates(LOGIN_SELECTORS['email_input'])
            
            if email_input:
                UserSimulation.human_move_and_click(self.driver, email_input)
                time.sleep(random.uniform(0.5, 1.0))
                
                # Xóa giá trị hiện tại nếu có
                current_value = email_input.get_attribute("value")
                if current_value:
                    for _ in range(len(current_value)):
                        email_input.send_keys(Keys.BACKSPACE)
                        time.sleep(random.uniform(0.05, 0.15))
                
                # Nhập email
                self.logger.info(f"Đang nhập email: {email}")
                UserSimulation.human_type(email_input, email)
                time.sleep(random.uniform(0.5, 1.5))
                self.screenshot("after_email_input.png")
                
                # Mô phỏng thao tác ngẫu nhiên
                UserSimulation.simulate_random_actions(self.driver)
                
                # Click nút Next
                next_button = self.find_element_from_candidates(LOGIN_SELECTORS['email_next_button'])
                if next_button:
                    self.logger.info("Đã tìm thấy nút Next, chuẩn bị click...")
                    UserSimulation.human_move_and_click(self.driver, next_button)
                    self.logger.info("Đã click nút Next sau khi nhập email")
                else:
                    self.logger.error("Không tìm thấy nút Next sau khi nhập email")
                    self.screenshot("no_next_button.png")
                    return False
            else:
                self.logger.error("Không tìm thấy trường nhập email")
                self.screenshot("no_email_field.png")
                return False
            
            # Đợi trang mật khẩu
            time.sleep(random.uniform(3.0, 5.0))
            self.screenshot("password_page.png")
            
            # Nhập mật khẩu
            self.logger.info("Đang chờ màn hình nhập mật khẩu...")
            password_input = self.find_element_from_candidates(LOGIN_SELECTORS['password_input'])
            
            if password_input:
                UserSimulation.human_move_and_click(self.driver, password_input)
                time.sleep(random.uniform(0.5, 1.0))
                
                # Xóa giá trị hiện tại nếu có
                current_value = password_input.get_attribute("value")
                if current_value:
                    for _ in range(len(current_value)):
                        password_input.send_keys(Keys.BACKSPACE)
                        time.sleep(random.uniform(0.05, 0.15))
                
                # Nhập mật khẩu
                self.logger.info("Đang nhập mật khẩu...")
                UserSimulation.human_type(password_input, password)
                time.sleep(random.uniform(0.5, 1.5))
                self.screenshot("after_password_input.png")
                
                # Mô phỏng thao tác ngẫu nhiên
                UserSimulation.simulate_random_actions(self.driver)
                
                # Click nút Next
                next_button = self.find_element_from_candidates(LOGIN_SELECTORS['password_next_button'])
                if next_button:
                    self.logger.info("Đã tìm thấy nút Next sau password, chuẩn bị click...")
                    UserSimulation.human_move_and_click(self.driver, next_button)
                    self.logger.info("Đã click nút Next sau khi nhập mật khẩu")
                else:
                    self.logger.error("Không tìm thấy nút Next sau khi nhập mật khẩu")
                    self.screenshot("no_password_next_button.png")
                    return False
            else:
                self.logger.error("Không tìm thấy trường nhập mật khẩu")
                self.screenshot("no_password_field.png")
                return False
            
            # Chờ đăng nhập thành công
            self.logger.info("Chờ đăng nhập hoàn tất...")
            time.sleep(random.uniform(7.0, 12.0))
            self.screenshot("after_login.png")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Lỗi khi đăng nhập: {str(e)}")
            self.logger.error(traceback.format_exc())
            self.screenshot("login_error.png")
            return False
    
    def visit_photos_homepage(self):
        """Truy cập trang chủ Google Photos."""
        if random.random() < 0.7:  # 70% cơ hội ghé thăm trang chủ
            self.logger.info("Ghé thăm trang chủ Google Photos trước khi đi đến album...")
            self.driver.get("https://photos.google.com")
            time.sleep(random.uniform(3.0, 6.0))
            
            # Mô phỏng scroll
            UserSimulation.human_scroll(self.driver, 'down', random.randint(300, 700))
            time.sleep(random.uniform(1.0, 3.0))
            
            # Đôi khi scroll lên lại
            if random.random() < 0.5:
                UserSimulation.human_scroll(self.driver, 'up', random.randint(100, 300))
            
            # Chụp ảnh màn hình trang chủ
            self.screenshot("photos_homepage.png")
    
    def access_album(self, album_url):
        """
        Truy cập một album Google Photos.
        
        Args:
            album_url: URL của album
            
        Returns:
            bool: Trạng thái truy cập
        """
        try:
            self.logger.info(f"Đang truy cập album: {album_url}")
            self.driver.get(album_url)
            
            # Đợi trang tải với thời gian biến thiên
            time.sleep(random.uniform(5.0, 10.0))
            
            # Mô phỏng di chuyển chuột trên trang
            actions = self.driver.find_elements(By.TAG_NAME, "body")[0]
            UserSimulation.human_move_and_click(self.driver, actions)
            time.sleep(random.uniform(0.5, 1.5))
            
            # Chụp ảnh màn hình để debug
            self.screenshot("album_page.png")
            self.logger.info("Đã chụp ảnh màn hình trang album")
            
            # Mô phỏng việc xem album
            UserSimulation.human_scroll(self.driver, 'down', random.randint(200, 500))
            time.sleep(random.uniform(1.0, 3.0))
            
            if random.random() < 0.5:
                UserSimulation.human_scroll(self.driver, 'up', random.randint(100, 300))
            
            return True
        
        except Exception as e:
            self.logger.error(f"Lỗi khi truy cập album: {str(e)}")
            self.logger.error(traceback.format_exc())
            self.screenshot("album_error.png")
            return False
    
    def save_photos(self):
        """
        Lưu ảnh từ album đang mở.
        
        Returns:
            bool: Trạng thái lưu ảnh
        """
        try:
            self.logger.info("Tìm nút 'Lưu ảnh'...")
            
            # Tìm tất cả buttons trên trang để debug
            all_buttons = self.driver.find_elements(By.TAG_NAME, "button")
            self.logger.info(f"Tìm thấy {len(all_buttons)} buttons trên trang album")
            for i, btn in enumerate(all_buttons):
                if btn.is_displayed():
                    self.logger.info(f"Button #{i}: text='{btn.text}', aria-label='{btn.get_attribute('aria-label')}'")
            
            # Tìm nút 'Lưu ảnh'
            save_button = self.find_element_from_candidates(ALBUM_SELECTORS['save_button'])
            
            # Nếu không tìm thấy từ selectors, thử tìm bằng cách duyệt tất cả buttons
            if not save_button:
                for btn in all_buttons:
                    if btn.is_displayed() and ('Lưu' in btn.text or (btn.get_attribute('aria-label') and 'Lưu' in btn.get_attribute('aria-label'))):
                        save_button = btn
                        self.logger.info(f"Tìm thấy nút Lưu qua text hoặc aria-label")
                        break
            
            if save_button:
                self.logger.info("Đã tìm thấy nút 'Lưu ảnh', chuẩn bị click...")
                
                # Mô phỏng người dùng cuộn đến nút Lưu
                self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", save_button)
                time.sleep(random.uniform(0.8, 1.5))
                
                self.screenshot("before_save_click.png")
                
                # Mô phỏng việc di chuyển chuột và click vào nút Lưu
                UserSimulation.human_move_and_click(self.driver, save_button)
                self.logger.info("Đã click nút 'Lưu ảnh'")
                
                # Đợi xử lý với thời gian biến thiên
                time.sleep(random.uniform(3.0, 5.0))
                self.screenshot("after_save_click.png")
                
                return True
            else:
                self.logger.error("Không tìm thấy nút 'Lưu ảnh'")
                
                # Thử cách khác: Sử dụng JavaScript để tìm và click nút lưu
                try:
                    result = self.driver.execute_script("""
                        // Tìm tất cả các buttons có thể nhìn thấy
                        const buttons = Array.from(document.querySelectorAll('button'));
                        const visibleButtons = buttons.filter(btn => {
                            const rect = btn.getBoundingClientRect();
                            return rect.width > 0 && 
                                rect.height > 0 && 
                                window.getComputedStyle(btn).visibility !== 'hidden' &&
                                window.getComputedStyle(btn).display !== 'none';
                        });
                        
                        console.log('Visible buttons:', visibleButtons.map(b => ({
                            text: b.textContent?.trim(),
                            ariaLabel: b.getAttribute('aria-label')
                        })));
                        
                        // Tìm button có chữ "Lưu"
                        const saveButton = visibleButtons.find(btn => 
                            (btn.textContent && btn.textContent.includes('Lưu')) || 
                            (btn.getAttribute('aria-label') && btn.getAttribute('aria-label').includes('Lưu'))
                        );
                            if (saveButton) {
                                // Di chuyển đến nút trước khi click
                                saveButton.scrollIntoView({behavior: 'smooth', block: 'center'});
                                
                                // Tạo độ trễ giống hành vi người dùng
                                setTimeout(() => {
                                    // Tạo hiệu ứng hover trước khi click
                                    const mouseoverEvent = new MouseEvent('mouseover', {
                                        'view': window,
                                        'bubbles': true,
                                        'cancelable': true
                                    });
                                    saveButton.dispatchEvent(mouseoverEvent);
                                    
                                    // Tạo độ trễ giữa hover và click
                                    setTimeout(() => {
                                        saveButton.click();
                                    }, Math.random() * 500 + 200);
                                }, Math.random() * 1000 + 500);
                                
                                return true;
                            }
                            return false;
                        """)
                    
                    time.sleep(random.uniform(1.5, 3.0))  # Đợi JavaScript hoàn thành
                    self.screenshot("after_js_save_click.png")
                    
                    if result:
                        self.logger.info("Đã tìm và click nút 'Lưu ảnh' bằng JavaScript")
                        # Đợi xử lý với thời gian biến thiên
                        time.sleep(random.uniform(3.0, 5.0))
                        return True
                    else:
                        self.logger.error("Không tìm thấy nút 'Lưu ảnh' bằng JavaScript")
                except Exception as e:
                    self.logger.error(f"Lỗi khi tìm nút 'Lưu ảnh' bằng JavaScript: {str(e)}")
                
                return False
        
        except Exception as e:
            self.logger.error(f"Lỗi khi lưu ảnh: {str(e)}")
            self.logger.error(traceback.format_exc())
            self.screenshot("save_photos_error.png")
            return False
    
    def close(self):
        """Đóng trình duyệt."""
        if self.driver:
            # Đôi khi truy cập một trang khác trước khi thoát
            if random.random() < 0.3:  # 30% cơ hội
                self.driver.get("https://photos.google.com")
                time.sleep(random.uniform(2.0, 4.0))
            
            self.driver.quit()
            self.logger.info("Đã đóng WebDriver")