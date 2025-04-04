from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
import os
import time
import logging
import traceback
import random
import subprocess
import platform

def kill_chrome_processes():
    """Đóng tất cả tiến trình Chrome đang chạy"""
    try:
        if platform.system() == "Windows":
            subprocess.run(["taskkill", "/F", "/IM", "chrome.exe", "/T"], capture_output=True)
            subprocess.run(["taskkill", "/F", "/IM", "chromedriver.exe", "/T"], capture_output=True)
        else:  # Linux hoặc macOS
            subprocess.run(["pkill", "-f", "chrome"], capture_output=True)
            subprocess.run(["pkill", "-f", "chromedriver"], capture_output=True)
        logging.info("Đã dọn dẹp các tiến trình Chrome")
    except Exception as e:
        logging.warning(f"Không thể dọn dẹp tiến trình Chrome: {str(e)}")

# Thiết lập logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler("backup_photos.log"), logging.StreamHandler()]
)

# Thông tin xác thực - nên lưu trong biến môi trường
EMAIL = os.environ.get('GOOGLE_EMAIL')
PASSWORD = os.environ.get('GOOGLE_PASSWORD')
ALBUM_URL = os.environ.get('ALBUM_URL')

# Thiết lập Chrome options cho headless mode
chrome_options = Options()
# chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--window-size=1920,1080")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--disable-notifications")
chrome_options.add_argument("--disable-popup-blocking")

# Thêm thư mục user data riêng để tránh xung đột
import tempfile
user_data_dir = tempfile.mkdtemp()
chrome_options.add_argument(f"--user-data-dir={user_data_dir}")

# Ẩn dấu hiệu automation
chrome_options.add_argument("--disable-blink-features=AutomationControlled")
chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36")
chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
chrome_options.add_experimental_option("useAutomationExtension", False)

# Hàm để mô phỏng việc gõ phím như người dùng thực
def human_type(element, text, min_delay=0.05, max_delay=0.25):
    for char in text:
        element.send_keys(char)
        # Thời gian delay ngẫu nhiên giữa các phím
        time.sleep(random.uniform(min_delay, max_delay))
    
    # Đôi khi dừng lại lâu hơn (mô phỏng người dùng suy nghĩ)
    if random.random() < 0.2:  # 20% cơ hội dừng lại lâu hơn
        time.sleep(random.uniform(0.5, 1.5))

# Hàm mô phỏng click chuột đơn giản và an toàn hơn
def safe_click(driver, element):
    try:
        # Đảm bảo phần tử hiển thị trong view
        driver.execute_script("arguments[0].scrollIntoView({behavior: 'auto', block: 'center'});", element)
        time.sleep(random.uniform(0.5, 1.0))
        
        # Thử click bằng JavaScript trước
        driver.execute_script("arguments[0].click();", element)
        logging.info(f"Đã click thành công bằng JavaScript vào phần tử: {element.get_attribute('outerHTML')[:50]}...")
        return True
    except Exception as e:
        logging.warning(f"Không thể click bằng JavaScript: {str(e)}")
        try:
            # Thử click bằng Selenium
            element.click()
            logging.info(f"Đã click thành công bằng Selenium vào phần tử: {element.get_attribute('outerHTML')[:50]}...")
            return True
        except Exception as e:
            logging.error(f"Không thể click bằng cả JavaScript và Selenium: {str(e)}")
            return False

# Hàm scroll tự nhiên
def human_scroll(driver, direction='down', pixels=None, smooth=True):
    if pixels is None:
        pixels = random.randint(100, 500)  # Mặc định scroll một khoảng ngẫu nhiên
    
    if direction == 'down':
        pixels = abs(pixels)
    elif direction == 'up':
        pixels = -abs(pixels)
    
    if smooth:
        # Scroll mượt bằng nhiều bước nhỏ
        step_count = random.randint(5, 15)
        step_size = pixels / step_count
        for _ in range(step_count):
            driver.execute_script(f"window.scrollBy(0, {step_size})")
            time.sleep(random.uniform(0.01, 0.05))
    else:
        # Scroll ngay lập tức
        driver.execute_script(f"window.scrollBy(0, {pixels})")
    
    # Đôi khi dừng lại sau khi scroll để "đọc"
    if random.random() < 0.3:  # 30% cơ hội dừng lại để đọc
        time.sleep(random.uniform(0.8, 2.0))

# Thêm hàm để tìm phần tử một cách ổn định với nhiều cách thử khác nhau
def find_element_safely(driver, wait, locator_strategies, description):
    """
    Tìm phần tử bằng nhiều chiến lược khác nhau và trả về phần tử đầu tiên tìm thấy
    
    Args:
        driver: WebDriver instance
        wait: WebDriverWait instance
        locator_strategies: List of tuples (By, locator)
        description: Mô tả phần tử đang tìm để log
    
    Returns:
        WebElement hoặc None nếu không tìm thấy
    """
    logging.info(f"Đang tìm {description}...")
    
    for by, locator in locator_strategies:
        try:
            element = wait.until(EC.presence_of_element_located((by, locator)))
            logging.info(f"Đã tìm thấy {description} với {by}={locator}")
            return element
        except Exception:
            logging.info(f"Không tìm thấy {description} với {by}={locator}")
    
    logging.error(f"Không tìm thấy {description} với tất cả các locator strategy đã thử")
    return None

try:
    # Dọn dẹp tiến trình Chrome đang chạy
    kill_chrome_processes()

    # Khởi tạo WebDriver
    logging.info("Đang khởi tạo WebDriver...")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    wait = WebDriverWait(driver, 30)  # Tăng timeout lên 30s
    
    # Đảm bảo cửa sổ đủ lớn
    driver.maximize_window()
    actual_size = driver.execute_script("return [window.innerWidth, window.innerHeight];")
    logging.info(f"Kích thước cửa sổ thực tế: {actual_size}")
    
    # Tùy chỉnh WebDriver để tránh phát hiện
    driver.execute_cdp_cmd("Network.setUserAgentOverride", {
        "userAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
    })
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    # Đăng nhập vào Google
    logging.info("Đang đăng nhập vào Google...")
    driver.get("https://accounts.google.com/signin")
    
    # Đợi trang tải với thời gian biến đổi
    time.sleep(random.uniform(2.0, 4.0))
    
    # Chụp ảnh màn hình để debug
    driver.save_screenshot("login_page.png")
    
    # Tìm trường nhập email sử dụng nhiều chiến lược
    email_input_strategies = [
        (By.ID, "identifierId"),
        (By.XPATH, "//input[@type='email']"),
        (By.XPATH, "//input[@aria-label='Email or phone']"),
        (By.NAME, "identifier")
    ]
    
    email_input = find_element_safely(driver, wait, email_input_strategies, "trường nhập email")
    
    if email_input:
        # Xóa giá trị hiện tại nếu có
        current_value = email_input.get_attribute("value")
        if current_value:
            for _ in range(len(current_value)):
                email_input.send_keys(Keys.BACKSPACE)
                time.sleep(random.uniform(0.05, 0.15))
        
        # Nhập email giống người dùng thật
        logging.info(f"Đang nhập email: {EMAIL}")
        human_type(email_input, EMAIL)
        
        # Đợi một lúc sau khi nhập
        time.sleep(random.uniform(0.5, 1.5))
        
        driver.save_screenshot("after_email_input.png")
        
        # Tìm nút Next/Tiếp theo với nhiều chiến lược
        next_button_strategies = [
            (By.ID, "identifierNext"),
            (By.XPATH, "//button[contains(text(), 'Next')]"),
            (By.XPATH, "//span[contains(text(), 'Next')]/ancestor::button"),
            (By.XPATH, "//button[@jsname='LgbsSe']"),
            (By.XPATH, "//button[contains(@class, 'VfPpkd-LgbsSe')]")
        ]
        
        next_button = find_element_safely(driver, wait, next_button_strategies, "nút Next sau email")
        
        if next_button:
            # Chụp ảnh trước khi click
            driver.save_screenshot("before_next_click.png")
            
            # Sử dụng hàm click an toàn
            if safe_click(driver, next_button):
                logging.info("Đã click nút Next sau khi nhập email")
            else:
                logging.error("Không thể click nút Next")
                driver.save_screenshot("next_click_failed.png")
                # Thử phương pháp cuối cùng - đẩy form bằng Enter key
                email_input.send_keys(Keys.ENTER)
                logging.info("Đã thử submit form bằng phím Enter")
        else:
            logging.error("Không tìm thấy nút Next sau khi nhập email")
            driver.save_screenshot("no_next_button.png")
            # Thử phương pháp cuối cùng - đẩy form bằng Enter key
            email_input.send_keys(Keys.ENTER)
            logging.info("Đã thử submit form bằng phím Enter")
    else:
        logging.error("Không tìm thấy trường nhập email")
        driver.save_screenshot("no_email_field.png")
    
    # Đợi một lúc với thời gian biến thiên để mô phỏng thời gian tải trang
    time.sleep(random.uniform(5.0, 8.0))
    
    # Chụp ảnh màn hình để xác định trạng thái hiện tại
    driver.save_screenshot("before_password.png")
    
    # Nhập mật khẩu
    logging.info("Đang chờ màn hình nhập mật khẩu...")
    
    # Tìm trường nhập mật khẩu sử dụng nhiều chiến lược
    password_input_strategies = [
        (By.NAME, "Passwd"),
        (By.XPATH, "//input[@type='password']"),
        (By.XPATH, "//input[@aria-label='Enter your password']"),
        (By.CSS_SELECTOR, "input[type='password']")
    ]
    
    password_input = find_element_safely(driver, wait, password_input_strategies, "trường nhập mật khẩu")
    
    if password_input:
        # Đảm bảo phần tử nhìn thấy được
        driver.execute_script("arguments[0].scrollIntoView({behavior: 'auto', block: 'center'});", password_input)
        time.sleep(random.uniform(0.5, 1.0))
        
        # Xóa giá trị hiện tại nếu có
        current_value = password_input.get_attribute("value")
        if current_value:
            for _ in range(len(current_value)):
                password_input.send_keys(Keys.BACKSPACE)
                time.sleep(random.uniform(0.05, 0.15))
        
        # Nhập mật khẩu giống người dùng thật
        logging.info("Đang nhập mật khẩu...")
        human_type(password_input, PASSWORD)
        
        # Đợi một lúc sau khi nhập
        time.sleep(random.uniform(0.5, 1.5))
        
        driver.save_screenshot("after_password_input.png")
        
        # Tìm nút next sau password
        next_button_strategies = [
            (By.ID, "passwordNext"),
            (By.XPATH, "//button[contains(@class, 'VfPpkd-LgbsSe')]"),
            (By.XPATH, "//button[@jsname='LgbsSe']"),
            (By.XPATH, "//div[@id='passwordNext']/div/button")
        ]
        
        next_button = find_element_safely(driver, wait, next_button_strategies, "nút Next sau mật khẩu")
        
        if next_button:
            # Chụp ảnh trước khi click
            driver.save_screenshot("before_password_next_click.png")
            
            # Sử dụng hàm click an toàn
            if safe_click(driver, next_button):
                logging.info("Đã click nút Next sau khi nhập mật khẩu")
            else:
                logging.error("Không thể click nút Next sau mật khẩu")
                driver.save_screenshot("password_next_click_failed.png")
                # Thử phương pháp cuối cùng - đẩy form bằng Enter key
                password_input.send_keys(Keys.ENTER)
                logging.info("Đã thử submit form mật khẩu bằng phím Enter")
        else:
            logging.error("Không tìm thấy nút Next sau khi nhập mật khẩu")
            driver.save_screenshot("no_password_next_button.png")
            # Thử phương pháp cuối cùng - đẩy form bằng Enter key
            password_input.send_keys(Keys.ENTER)
            logging.info("Đã thử submit form mật khẩu bằng phím Enter")
    else:
        logging.error("Không tìm thấy trường nhập mật khẩu")
        driver.save_screenshot("no_password_field.png")
    
    # Chờ đăng nhập thành công với thời gian biến thiên
    logging.info("Chờ đăng nhập hoàn tất...")
    time.sleep(random.uniform(7.0, 12.0))
    driver.save_screenshot("after_login.png")
    
    # Truy cập album chia sẻ (chỉ khi có URL)
    if ALBUM_URL:
        try:
            logging.info(f"Đang truy cập album: {ALBUM_URL}")
            driver.get(ALBUM_URL)
            
            # Đợi trang tải với thời gian biến thiên
            time.sleep(random.uniform(5.0, 10.0))
            
            # Chụp ảnh màn hình để debug
            driver.save_screenshot("album_page.png")
            logging.info("Đã chụp ảnh màn hình trang album")
            
            # Mô phỏng việc xem album
            human_scroll(driver, 'down', random.randint(200, 500))
            time.sleep(random.uniform(1.0, 3.0))
            
            if random.random() < 0.5:
                human_scroll(driver, 'up', random.randint(100, 300))
            
            # Tìm nút "Lưu ảnh" với nhiều chiến lược
            save_button_strategies = [
                (By.XPATH, "//button[contains(@aria-label, 'Lưu')]"),
                (By.XPATH, "//button[contains(text(), 'Lưu')]"),
                (By.XPATH, "//button[contains(@class, 'VfPpkd-LgbsSe') and contains(., 'Lưu')]")
            ]
            
            save_button = find_element_safely(driver, wait, save_button_strategies, "nút Lưu ảnh")
            
            if save_button:
                # Đảm bảo phần tử nhìn thấy được
                driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", save_button)
                time.sleep(random.uniform(0.8, 1.5))
                
                driver.save_screenshot("before_save_click.png")
                
                # Sử dụng hàm click an toàn
                if safe_click(driver, save_button):
                    logging.info("Đã click nút 'Lưu ảnh'")
                    # Đợi xử lý với thời gian biến thiên
                    time.sleep(random.uniform(3.0, 5.0))
                    driver.save_screenshot("after_save_click.png")
                else:
                    logging.error("Không thể click nút 'Lưu ảnh'")
                    driver.save_screenshot("save_click_failed.png")
            else:
                logging.error("Không tìm thấy nút 'Lưu ảnh'")
                driver.save_screenshot("no_save_button.png")
        
        except Exception as e:
            logging.error(f"Lỗi khi truy cập album: {str(e)}")
            logging.error(traceback.format_exc())
            driver.save_screenshot("album_error.png")
    else:
        logging.warning("Không có URL album. Bỏ qua bước truy cập album.")
    
    # Sau khi hoàn thành
    logging.info("Hoàn thành thao tác!")
    time.sleep(random.uniform(2.0, 4.0))

except Exception as e:
    logging.error(f"Lỗi không xác định: {str(e)}")
    logging.error(traceback.format_exc())
    if 'driver' in locals():
        driver.save_screenshot("error.png")

finally:
    # Đóng browser
    if 'driver' in locals():
        try:
            driver.quit()
            logging.info("Đã đóng WebDriver")
        except Exception as e:
            logging.error(f"Lỗi khi đóng WebDriver: {str(e)}")
    
    # Dọn dẹp tiến trình và thư mục
    try:
        kill_chrome_processes()
        if 'user_data_dir' in locals() and os.path.exists(user_data_dir):
            import shutil
            shutil.rmtree(user_data_dir, ignore_errors=True)
            logging.info(f"Đã xóa thư mục dữ liệu tạm: {user_data_dir}")
    except Exception as e:
        logging.error(f"Lỗi khi dọn dẹp: {str(e)}")