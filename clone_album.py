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
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--window-size=1920,1080")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--disable-notifications")
chrome_options.add_argument("--disable-popup-blocking")

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

# Hàm mô phỏng di chuyển chuột như người dùng
def human_move_and_click(driver, element):
    # Tạo ActionChains để thực hiện di chuyển chuột
    actions = ActionChains(driver)
    
    # Thêm 1-3 điểm di chuyển ngẫu nhiên trước khi đến đích
    viewport_width = driver.execute_script("return window.innerWidth")
    viewport_height = driver.execute_script("return window.innerHeight")
    
    # Lấy vị trí hiện tại của chuột (nếu không có thì lấy vị trí góc)
    current_x = driver.execute_script("return window.mouseX || 0")
    current_y = driver.execute_script("return window.mouseY || 0")
    
    # Tính vị trí đích
    element_rect = element.rect
    target_x = element_rect['x'] + element_rect['width'] / 2
    target_y = element_rect['y'] + element_rect['height'] / 2
    
    # Thêm 1-3 điểm di chuyển ngẫu nhiên
    num_points = random.randint(1, 3)
    for _ in range(num_points):
        # Tạo điểm trung gian ngẫu nhiên nhưng hơi về phía target
        mid_x = current_x + (target_x - current_x) * random.uniform(0.3, 0.7)
        mid_y = current_y + (target_y - current_y) * random.uniform(0.3, 0.7)
        
        # Thêm chút nhiễu ngẫu nhiên
        mid_x += random.uniform(-100, 100)
        mid_y += random.uniform(-100, 100)
        
        # Đảm bảo điểm trung gian nằm trong viewport
        mid_x = max(0, min(mid_x, viewport_width))
        mid_y = max(0, min(mid_y, viewport_height))
        
        # Di chuyển đến điểm trung gian
        actions.move_by_offset(mid_x - current_x, mid_y - current_y)
        actions.pause(random.uniform(0.1, 0.3))
        
        # Cập nhật vị trí hiện tại
        current_x, current_y = mid_x, mid_y
    
    # Di chuyển đến phần tử đích
    actions.move_to_element(element)
    actions.pause(random.uniform(0.1, 0.5))
    
    # Click với độ trễ ngẫu nhiên
    actions.click()
    actions.perform()

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

# Thêm các phím tắt ngẫu nhiên để mô phỏng hành vi người dùng
def simulate_random_actions(driver):
    if random.random() < 0.1:  # 10% cơ hội thực hiện
        actions = ActionChains(driver)
        # Mô phỏng di chuyển chuột ngẫu nhiên
        viewport_width = driver.execute_script("return window.innerWidth")
        viewport_height = driver.execute_script("return window.innerHeight")
        x = random.randint(0, viewport_width)
        y = random.randint(0, viewport_height)
        actions.move_by_offset(x, y)
        actions.perform()
        time.sleep(random.uniform(0.1, 0.5))

try:
    # Khởi tạo WebDriver
    logging.info("Đang khởi tạo WebDriver...")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    wait = WebDriverWait(driver, 30)  # Tăng timeout lên 30s
    
    # Tùy chỉnh WebDriver để tránh phát hiện
    driver.execute_cdp_cmd("Network.setUserAgentOverride", {
        "userAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
    })
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    # Mở trình duyệt toàn màn hình
    driver.maximize_window()
    time.sleep(random.uniform(1.0, 2.0))
    
    # Đăng nhập vào Google
    logging.info("Đang đăng nhập vào Google...")
    driver.get("https://accounts.google.com/signin")
    
    # Đợi trang tải với thời gian biến đổi
    time.sleep(random.uniform(2.0, 4.0))
    
    # Chụp ảnh màn hình để debug
    driver.save_screenshot("login_page.png")
    
    # Mô phỏng việc nhấp vào trang
    actions = ActionChains(driver)
    actions.move_by_offset(random.randint(50, 300), random.randint(50, 300)).click().perform()
    time.sleep(random.uniform(0.5, 1.5))
    
    # Cập nhật selector để nhập email dựa trên hình ảnh bạn cung cấp
    try:
        logging.info("Đang tìm trường nhập email...")
        # Thử nhiều cách để tìm input email
        email_input = None
        
        # Cách 1: Tìm theo ID
        try:
            email_input = wait.until(EC.presence_of_element_located((By.ID, "identifierId")))
            logging.info("Tìm thấy input email bằng ID")
        except:
            logging.info("Không tìm thấy input email bằng ID, thử cách khác...")
        
        # Cách 2: Tìm theo XPath
        if not email_input:
            try:
                email_input = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@type='email']")))
                logging.info("Tìm thấy input email bằng XPath type='email'")
            except:
                logging.info("Không tìm thấy input email bằng XPath type='email', thử cách khác...")
        
        # Cách 3: Tìm theo placeholder/aria-label
        if not email_input:
            try:
                email_input = wait.until(EC.presence_of_element_located(
                    (By.XPATH, "//input[@aria-label='Email or phone']")))
                logging.info("Tìm thấy input email bằng aria-label")
            except:
                logging.info("Không tìm thấy input email bằng aria-label")
        
        if not email_input:
            # Lấy và log tất cả input trên trang
            all_inputs = driver.find_elements(By.TAG_NAME, "input")
            logging.info(f"Tìm thấy {len(all_inputs)} input elements trên trang")
            for i, inp in enumerate(all_inputs):
                attr_list = {}
                for attr in ["id", "name", "type", "aria-label", "placeholder"]:
                    attr_list[attr] = inp.get_attribute(attr)
                logging.info(f"Input #{i}: {attr_list}")
            
            # Thử lại với input đầu tiên có type là email hoặc text
            for inp in all_inputs:
                if inp.get_attribute("type") in ["email", "text"]:
                    email_input = inp
                    logging.info(f"Sử dụng input có type={inp.get_attribute('type')}")
                    break
        
        if email_input:
            # Mô phỏng người dùng click vào trường nhập
            human_move_and_click(driver, email_input)
            time.sleep(random.uniform(0.5, 1.0))
            
            # Xóa giá trị hiện tại nếu có
            current_value = email_input.get_attribute("value")
            if current_value:
                for _ in range(len(current_value)):
                    email_input.send_keys(Keys.BACKSPACE)
                    time.sleep(random.uniform(0.05, 0.15))
            
            # Nhập email giống người dùng thật
            logging.info(f"Đang nhập email: {EMAIL}")
            human_type(email_input, EMAIL)
            
            # Đôi khi pauses sau khi nhập
            time.sleep(random.uniform(0.5, 1.5))
            
            driver.save_screenshot("after_email_input.png")
            
            # Mô phỏng thao tác ngẫu nhiên
            simulate_random_actions(driver)
            
            # Tìm nút Next/Tiếp theo
            try:
                next_button = None
                
                # Thử nhiều cách để tìm nút Next
                try:
                    next_button = wait.until(EC.element_to_be_clickable((By.ID, "identifierNext")))
                except:
                    logging.info("Không tìm thấy nút Next bằng ID")
                
                if not next_button:
                    try:
                        next_button = wait.until(EC.element_to_be_clickable(
                            (By.XPATH, "//button[contains(text(), 'Next')]")))
                    except:
                        logging.info("Không tìm thấy nút Next bằng text")
                
                if not next_button:
                    try:
                        next_button = wait.until(EC.element_to_be_clickable(
                            (By.XPATH, "//span[contains(text(), 'Next')]/ancestor::button")))
                    except:
                        logging.info("Không tìm thấy nút Next bằng span text")
                
                if not next_button:
                    # Tìm tất cả các button
                    buttons = driver.find_elements(By.TAG_NAME, "button")
                    logging.info(f"Tìm thấy {len(buttons)} buttons trên trang")
                    for btn in buttons:
                        if btn.is_displayed() and btn.is_enabled():
                            logging.info(f"Button text: {btn.text}, aria-label: {btn.get_attribute('aria-label')}")
                            if btn.text.lower() in ["next", "tiếp theo", "tiếp tục"] or \
                               (btn.get_attribute('aria-label') and 
                                btn.get_attribute('aria-label').lower() in ["next", "tiếp theo", "tiếp tục"]):
                                next_button = btn
                                break
                
                if next_button:
                    # Click vào nút Next như người dùng thật
                    logging.info("Đã tìm thấy nút Next, chuẩn bị click...")
                    human_move_and_click(driver, next_button)
                    logging.info("Đã click nút Next sau khi nhập email")
                else:
                    logging.error("Không tìm thấy nút Next sau khi nhập email")
                    driver.save_screenshot("no_next_button.png")
            except Exception as e:
                logging.error(f"Lỗi khi tìm hoặc click nút Next: {str(e)}")
                driver.save_screenshot("next_button_error.png")
        else:
            logging.error("Không tìm thấy trường nhập email")
            driver.save_screenshot("no_email_field.png")
    
    except Exception as e:
        logging.error(f"Lỗi khi nhập email: {str(e)}")
        driver.save_screenshot("email_input_error.png")
    
    # Đợi một lúc với thời gian biến thiên để mô phỏng thời gian tải trang
    time.sleep(random.uniform(3.0, 5.0))
    
    # Nhập mật khẩu
    try:
        logging.info("Đang chờ màn hình nhập mật khẩu...")
        driver.save_screenshot("password_page.png")
        
        # Thử nhiều cách để tìm trường nhập mật khẩu
        password_input = None
        
        try:
            password_input = wait.until(EC.presence_of_element_located((By.NAME, "Passwd")))
            logging.info("Tìm thấy input password bằng Name")
        except:
            logging.info("Không tìm thấy input password bằng Name, thử cách khác...")
        
        if not password_input:
            try:
                password_input = wait.until(EC.presence_of_element_located(
                    (By.XPATH, "//input[@type='password']")))
                logging.info("Tìm thấy input password bằng XPath type")
            except:
                logging.info("Không tìm thấy input password bằng XPath type")
        
        if not password_input:
            try:
                password_input = wait.until(EC.presence_of_element_located(
                    (By.XPATH, "//input[@aria-label='Enter your password']")))
                logging.info("Tìm thấy input password bằng aria-label")
            except:
                logging.info("Không tìm thấy input password bằng aria-label")
        
        if not password_input:
            # Lấy và log tất cả input trên trang
            all_inputs = driver.find_elements(By.TAG_NAME, "input")
            logging.info(f"Tìm thấy {len(all_inputs)} input elements trên trang")
            for i, inp in enumerate(all_inputs):
                attr_list = {}
                for attr in ["id", "name", "type", "aria-label", "placeholder"]:
                    attr_list[attr] = inp.get_attribute(attr)
                logging.info(f"Input #{i}: {attr_list}")
            
            # Thử lại với input đầu tiên có type là password
            for inp in all_inputs:
                if inp.get_attribute("type") == "password":
                    password_input = inp
                    logging.info("Sử dụng input có type=password")
                    break
        
        if password_input:
            # Mô phỏng người dùng click vào trường nhập
            human_move_and_click(driver, password_input)
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
            
            # Đôi khi pauses sau khi nhập
            time.sleep(random.uniform(0.5, 1.5))
            
            driver.save_screenshot("after_password_input.png")
            
            # Mô phỏng thao tác ngẫu nhiên
            simulate_random_actions(driver)
            
            # Tìm nút passwordNext
            try:
                next_button = None
                
                # Thử nhiều cách để tìm nút Next sau mật khẩu
                try:
                    next_button = wait.until(EC.element_to_be_clickable((By.ID, "passwordNext")))
                except:
                    logging.info("Không tìm thấy nút passwordNext bằng ID")
                
                if not next_button:
                    buttons = driver.find_elements(By.TAG_NAME, "button")
                    for btn in buttons:
                        if btn.is_displayed() and btn.is_enabled():
                            if btn.text.lower() in ["next", "tiếp theo", "tiếp tục"] or \
                               (btn.get_attribute('aria-label') and 
                                btn.get_attribute('aria-label').lower() in ["next", "tiếp theo", "tiếp tục"]):
                                next_button = btn
                                break
                
                if next_button:
                    # Click vào nút Next như người dùng thật
                    logging.info("Đã tìm thấy nút Next sau password, chuẩn bị click...")
                    human_move_and_click(driver, next_button)
                    logging.info("Đã click nút Next sau khi nhập mật khẩu")
                else:
                    logging.error("Không tìm thấy nút Next sau khi nhập mật khẩu")
                    driver.save_screenshot("no_password_next_button.png")
            except Exception as e:
                logging.error(f"Lỗi khi tìm hoặc click nút passwordNext: {str(e)}")
                driver.save_screenshot("password_next_button_error.png")
        else:
            logging.error("Không tìm thấy trường nhập mật khẩu")
            driver.save_screenshot("no_password_field.png")
    
    except Exception as e:
        logging.error(f"Lỗi khi nhập mật khẩu: {str(e)}")
        driver.save_screenshot("password_input_error.png")
    
    # Chờ đăng nhập thành công với thời gian biến thiên
    logging.info("Chờ đăng nhập hoàn tất...")
    time.sleep(random.uniform(7.0, 12.0))
    driver.save_screenshot("after_login.png")
    
    # Mô phỏng việc xem trang chủ trước khi đi đến album
    if random.random() < 0.7:  # 70% cơ hội ghé thăm trang chủ
        logging.info("Ghé thăm trang chủ Google Photos trước khi đi đến album...")
        driver.get("https://photos.google.com")
        time.sleep(random.uniform(3.0, 6.0))
        
        # Mô phỏng scroll
        human_scroll(driver, 'down', random.randint(300, 700))
        time.sleep(random.uniform(1.0, 3.0))
        
        # Đôi khi scroll lên lại
        if random.random() < 0.5:
            human_scroll(driver, 'up', random.randint(100, 300))
        
        # Chụp ảnh màn hình trang chủ
        driver.save_screenshot("photos_homepage.png")
    
    # Truy cập album chia sẻ
    try:
        logging.info(f"Đang truy cập album: {ALBUM_URL}")
        driver.get(ALBUM_URL)
        
        # Đợi trang tải với thời gian biến thiên
        time.sleep(random.uniform(5.0, 10.0))
        
        # Mô phỏng di chuyển chuột trên trang
        actions = ActionChains(driver)
        actions.move_by_offset(random.randint(50, 300), random.randint(50, 300)).perform()
        time.sleep(random.uniform(0.5, 1.5))
        
        # Chụp ảnh màn hình để debug
        driver.save_screenshot("album_page.png")
        logging.info("Đã chụp ảnh màn hình trang album")
        
        # Mô phỏng việc xem album
        human_scroll(driver, 'down', random.randint(200, 500))
        time.sleep(random.uniform(1.0, 3.0))
        
        if random.random() < 0.5:
            human_scroll(driver, 'up', random.randint(100, 300))
        
        # Tìm nút "Lưu ảnh" 
        logging.info("Tìm nút 'Lưu ảnh'...")
        
        # Tìm tất cả buttons trên trang để debug
        all_buttons = driver.find_elements(By.TAG_NAME, "button")
        logging.info(f"Tìm thấy {len(all_buttons)} buttons trên trang album")
        for i, btn in enumerate(all_buttons):
            if btn.is_displayed():
                logging.info(f"Button #{i}: text='{btn.text}', aria-label='{btn.get_attribute('aria-label')}'")
        
        # Tìm nút 'Lưu ảnh' bằng nhiều cách
        save_button = None
        
        # Cách 1: Tìm theo aria-label
        try:
            save_buttons = driver.find_elements(By.XPATH, "//button[contains(@aria-label, 'Lưu')]")
            if save_buttons:
                save_button = save_buttons[0]
                logging.info(f"Tìm thấy nút Lưu ảnh qua aria-label: {save_button.get_attribute('aria-label')}")
        except:
            logging.info("Không tìm thấy nút Lưu ảnh qua aria-label")
        
        # Cách 2: Tìm theo text
        if not save_button:
            try:
                save_buttons = driver.find_elements(By.XPATH, "//button[contains(text(), 'Lưu')]")
                if save_buttons:
                    save_button = save_buttons[0]
                    logging.info(f"Tìm thấy nút Lưu ảnh qua text: {save_button.text}")
            except:
                logging.info("Không tìm thấy nút Lưu ảnh qua text")
        
        # Cách 3: Tìm theo vị trí trong DOM
        if not save_button:
            try:
                for btn in all_buttons:
                    if btn.is_displayed() and ('Lưu' in btn.text or (btn.get_attribute('aria-label') and 'Lưu' in btn.get_attribute('aria-label'))):
                        save_button = btn
                        logging.info(f"Tìm thấy nút Lưu qua text hoặc aria-label")
                        break
            except:
                logging.info("Không tìm thấy nút Lưu qua DOM")
        
        if save_button:
            logging.info("Đã tìm thấy nút 'Lưu ảnh', chuẩn bị click...")
            
            # Mô phỏng người dùng cuộn đến nút Lưu
            driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", save_button)
            time.sleep(random.uniform(0.8, 1.5))
            
            driver.save_screenshot("before_save_click.png")
            
            # Mô phỏng việc di chuyển chuột và click vào nút Lưu
            human_move_and_click(driver, save_button)
            logging.info("Đã click nút 'Lưu ảnh'")
            
            # Đợi xử lý với thời gian biến thiên
            time.sleep(random.uniform(3.0, 5.0))
            driver.save_screenshot("after_save_click.png")
            
            # Đôi khi di chuyển chuột sau khi click để mô phỏng hành vi người dùng
            actions = ActionChains(driver)
            actions.move_by_offset(random.randint(-100, 100), random.randint(-50, 50)).perform()
        else:
            logging.error("Không tìm thấy nút 'Lưu ảnh'")
            
            # Thử cách khác: Tìm nút trong container cụ thể
            try:
                # Sử dụng JavaScript để tìm và click nút lưu
                result = driver.execute_script("""
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
                driver.save_screenshot("after_js_save_click.png")
               
                if result:
                    logging.info("Đã tìm và click nút 'Lưu ảnh' bằng JavaScript")
                    # Đợi xử lý với thời gian biến thiên
                    time.sleep(random.uniform(3.0, 5.0))
                else:
                    logging.error("Không tìm thấy nút 'Lưu ảnh' bằng JavaScript")
            except Exception as e:
                logging.error(f"Lỗi khi tìm nút 'Lưu ảnh' bằng JavaScript: {str(e)}")
   
    except Exception as e:
        logging.error(f"Lỗi khi truy cập album: {str(e)}")
        logging.error(traceback.format_exc())
        driver.save_screenshot("album_error.png")

    # Sau khi hoàn thành, mô phỏng hành vi người dùng đóng trang
    logging.info("Hoàn thành thao tác!")
    time.sleep(random.uniform(2.0, 4.0))
   
    # Đôi khi truy cập một trang khác trước khi thoát
    if random.random() < 0.3:  # 30% cơ hội
        driver.get("https://photos.google.com")
        time.sleep(random.uniform(2.0, 4.0))

except Exception as e:
    logging.error(f"Lỗi không xác định: {str(e)}")
    logging.error(traceback.format_exc())
    if 'driver' in locals():
        driver.save_screenshot("error.png")

finally:
    # Đóng browser
    if 'driver' in locals():
        driver.quit()
        logging.info("Đã đóng WebDriver")