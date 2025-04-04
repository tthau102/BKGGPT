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
import json

# Thiết lập logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler("save_photos.log"), logging.StreamHandler()]
)

# URL album cần truy cập
ALBUM_URL = os.environ.get('ALBUM_URL', 'https://photos.google.com/share/AF1QipOKWu2czu4s1cKLCJAXVf2RQAE8Q19LvMBvFZxnqkryXxXCB3uxWzg8krnIQf1QRw?key=MWpqQTc1TEo0aWZhVGNZSXhlR0NCajZZdUZidXl3')
EMAIL = os.environ.get('GOOGLE_EMAIL')
PASSWORD = os.environ.get('GOOGLE_PASSWORD')

# Thiết lập Chrome options
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--window-size=1920,1080")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--disable-notifications")
chrome_options.add_argument("--disable-popup-blocking")
chrome_options.add_argument("--disable-blink-features=AutomationControlled")
chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36")
chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
chrome_options.add_experimental_option("useAutomationExtension", False)

try:
    # Khởi tạo WebDriver
    logging.info("Đang khởi tạo WebDriver...")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    wait = WebDriverWait(driver, 30)
    
    # Ẩn dấu hiệu WebDriver
    driver.execute_cdp_cmd("Network.setUserAgentOverride", {
        "userAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
    })
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    # Đăng nhập vào Google
    if EMAIL and PASSWORD:
        logging.info("Thực hiện đăng nhập...")
        driver.get("https://accounts.google.com/signin")
        time.sleep(5)
        
        # Nhập email
        try:
            email_input = wait.until(EC.element_to_be_clickable((By.ID, "identifierId")))
            email_input.clear()
            for char in EMAIL:
                email_input.send_keys(char)
                time.sleep(random.uniform(0.05, 0.2))
            time.sleep(1)
            next_button = wait.until(EC.element_to_be_clickable((By.ID, "identifierNext")))
            next_button.click()
            time.sleep(3)
        except Exception as e:
            logging.error(f"Lỗi khi nhập email: {str(e)}")
            driver.save_screenshot("email_error.png")
        
        # Nhập password
        try:
            password_input = wait.until(EC.element_to_be_clickable((By.NAME, "Passwd")))
            password_input.clear()
            for char in PASSWORD:
                password_input.send_keys(char)
                time.sleep(random.uniform(0.05, 0.2))
            time.sleep(1)
            password_next = wait.until(EC.element_to_be_clickable((By.ID, "passwordNext")))
            password_next.click()
            time.sleep(5)
        except Exception as e:
            logging.error(f"Lỗi khi nhập password: {str(e)}")
            driver.save_screenshot("password_error.png")
    
    # Truy cập trực tiếp đến URL album
    logging.info(f"Đang truy cập album: {ALBUM_URL}")
    driver.get(ALBUM_URL)
    
    # Đợi trang tải với thời gian đủ lớn
    logging.info("Đợi trang album tải hoàn tất...")
    time.sleep(10)
    driver.save_screenshot("album_page.png")
    
    # Tìm nút "Lưu ảnh" - thử nhiều cách
    logging.info("Đang tìm nút 'Lưu ảnh'...")
    
    # XPaths phức tạp để tìm nút chính xác
    save_button_xpaths = [
        "//button[@aria-label='Lưu ảnh']",
        "//button[contains(@jslog, '14036')]",
        "//button[contains(@class, 'pYTkkf-Bz112c-LgbsSe') and @aria-label='Lưu ảnh']",
        "//span[contains(@class, 'notranslate')]/svg[@class='v1262d aRBEtc']/ancestor::button",
        "//div[contains(@jscontroller, 'HqNShc')]/span/button",
        "//div[@class='DNAsC G6iPcb gsCQqe']/span/button"
    ]
    
    save_button = None
    for xpath in save_button_xpaths:
        try:
            elements = driver.find_elements(By.XPATH, xpath)
            if elements:
                for element in elements:
                    if element.is_displayed():
                        save_button = element
                        logging.info(f"Tìm thấy nút Lưu ảnh với XPath: {xpath}")
                        break
            if save_button:
                break
        except Exception as e:
            logging.info(f"Không tìm thấy nút bằng XPath {xpath}: {str(e)}")
    
    if not save_button:
        # Tìm tất cả buttons hiển thị trên trang và log thông tin
        logging.info("Không tìm thấy nút Lưu ảnh bằng XPath, tìm tất cả buttons hiển thị...")
        buttons = driver.find_elements(By.TAG_NAME, "button")
        visible_buttons = []
        
        for i, btn in enumerate(buttons):
            if btn.is_displayed():
                text = btn.text.strip() if btn.text else ""
                aria_label = btn.get_attribute("aria-label") or ""
                jslog = btn.get_attribute("jslog") or ""
                class_name = btn.get_attribute("class") or ""
                
                button_info = {
                    "index": i,
                    "text": text,
                    "aria_label": aria_label,
                    "jslog": jslog,
                    "class": class_name
                }
                
                visible_buttons.append(button_info)
                logging.info(f"Button #{i}: {json.dumps(button_info, ensure_ascii=False)}")
                
                # Tìm nút có aria-label là "Lưu ảnh"
                if "lưu ảnh" in aria_label.lower():
                    save_button = btn
                    logging.info(f"Tìm thấy nút Lưu ảnh bằng aria-label: {aria_label}")
                    break
                # Hoặc tìm theo jslog
                elif "14036" in jslog:
                    save_button = btn
                    logging.info(f"Tìm thấy nút Lưu ảnh bằng jslog: {jslog}")
                    break
    
    # Nếu vẫn không tìm thấy, thử JavaScript
    if not save_button:
        logging.info("Thử tìm và click nút Lưu ảnh bằng JavaScript...")
        try:
            driver.execute_script("""
                const buttons = Array.from(document.querySelectorAll('button'));
                const saveButton = buttons.find(btn => {
                    const ariaLabel = btn.getAttribute('aria-label');
                    const jslog = btn.getAttribute('jslog');
                    return (ariaLabel && ariaLabel.includes('Lưu ảnh')) || 
                           (jslog && jslog.includes('14036'));
                });
                
                if (saveButton) {
                    console.log('Tìm thấy nút Lưu ảnh bằng JavaScript');
                    // Scroll đến nút
                    saveButton.scrollIntoView({behavior: 'smooth', block: 'center'});
                    
                    // Chờ một chút và click
                    setTimeout(() => {
                        try {
                            saveButton.click();
                            console.log('Đã click nút Lưu ảnh');
                            return true;
                        } catch(e) {
                            console.error('Lỗi khi click:', e);
                            return false;
                        }
                    }, 1000);
                } else {
                    console.log('Không tìm thấy nút Lưu ảnh bằng JavaScript');
                    return false;
                }
            """)
            logging.info("Đã thực thi JavaScript để tìm và click nút Lưu ảnh")
            time.sleep(5)  # Đợi để JavaScript thực thi
            driver.save_screenshot("after_js_click.png")
        except Exception as e:
            logging.error(f"Lỗi khi thực thi JavaScript: {str(e)}")
    
    # Nếu tìm thấy nút bằng Selenium, thử click
    if save_button:
        logging.info("Đang chuẩn bị click nút Lưu ảnh...")
        
        # Cuộn đến nút
        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", save_button)
        time.sleep(2)
        
        # Chụp ảnh trước khi click
        driver.save_screenshot("before_save_click.png")
        
        # Thử các cách click khác nhau
        try:
            # Cách 1: Click thông thường
            save_button.click()
            logging.info("Đã click nút Lưu ảnh (cách 1)")
        except Exception as e:
            logging.warning(f"Lỗi khi click cách 1: {str(e)}")
            try:
                # Cách 2: Click bằng JavaScript
                driver.execute_script("arguments[0].click();", save_button)
                logging.info("Đã click nút Lưu ảnh (cách 2)")
            except Exception as e:
                logging.warning(f"Lỗi khi click cách 2: {str(e)}")
                try:
                    # Cách 3: Actions chains
                    actions = ActionChains(driver)
                    actions.move_to_element(save_button).pause(1).click().perform()
                    logging.info("Đã click nút Lưu ảnh (cách 3)")
                except Exception as e:
                    logging.error(f"Lỗi khi click nút Lưu ảnh: {str(e)}")
        
        # Đợi xử lý sau khi click
        time.sleep(5)
        driver.save_screenshot("after_save_click.png")
        
        # Kiểm tra kết quả
        try:
            # Thử tìm hiện thị xác nhận đã lưu
            save_confirm = driver.find_elements(By.XPATH, "//span[contains(text(), 'Đã lưu')]")
            if save_confirm:
                logging.info("Xác nhận đã lưu ảnh thành công!")
            
            # Kiểm tra trạng thái nút sau khi click
            try:
                svg_saved = driver.find_elements(By.XPATH, "//svg[contains(@class, 'PRE5') and not(contains(@style, 'display: none'))]")
                if svg_saved:
                    logging.info("Đã tìm thấy biểu tượng svg đã lưu!")
            except:
                pass
        except Exception as e:
            logging.warning(f"Không thể xác nhận trạng thái lưu: {str(e)}")
    
    # Thêm thời gian đợi cuối để hoàn tất xử lý
    logging.info("Chờ xử lý hoàn tất...")
    time.sleep(5)

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