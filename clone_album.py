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

# Hàm chuyên biệt để click nút "Lưu ảnh"
def click_save_button(driver, wait):
    logging.info("Đang cố gắng click nút 'Lưu ảnh' bằng nhiều phương pháp...")
    
    # 1. Phương pháp sử dụng XPath chính xác từ HTML được cung cấp
    xpath_patterns = [
        # XPath rất cụ thể dựa trên cấu trúc đã biết
        "//div[contains(@jscontroller, 'HqNShc')]/span/button[@aria-label='Lưu ảnh']",
        
        # XPath theo jslog
        "//button[contains(@jslog, '14036')]",
        
        # XPath theo SVG icon đặc trưng
        "//button[.//svg[contains(@class, 'aRBEtc')]]",
        
        # XPath kết hợp nhiều thuộc tính
        "//div[contains(@class, 'gsCQqe')]/span/button",
        
        # Tất cả nút có aria-label="Lưu ảnh"
        "//button[@aria-label='Lưu ảnh']"
    ]
    
    save_button = None
    for xpath in xpath_patterns:
        try:
            elements = driver.find_elements(By.XPATH, xpath)
            for element in elements:
                if element.is_displayed():
                    save_button = element
                    logging.info(f"Tìm thấy nút 'Lưu ảnh' bằng XPath: {xpath}")
                    break
            if save_button:
                break
        except Exception as e:
            logging.info(f"Không tìm thấy nút với XPath {xpath}: {str(e)}")
    
    # 2. Nếu không tìm thấy bằng XPath, thử JavaScript với querySelector
    if not save_button:
        logging.info("Thử tìm nút 'Lưu ảnh' bằng JavaScript...")
        try:
            save_button = driver.execute_script("""
                // CSS selector chính xác
                let button = document.querySelector('div[jscontroller="HqNShc"] button[aria-label="Lưu ảnh"]');
                if (!button) {
                    // Thử các selectors khác
                    button = document.querySelector('button[jslog="14036"]');
                }
                if (!button) {
                    // Dựa vào nội dung SVG
                    const buttons = Array.from(document.querySelectorAll('button'));
                    button = buttons.find(btn => {
                        const svg = btn.querySelector('svg.aRBEtc');
                        return svg !== null;
                    });
                }
                return button;
            """)
            if save_button:
                logging.info("Tìm thấy nút 'Lưu ảnh' bằng JavaScript query selector")
        except Exception as e:
            logging.error(f"Lỗi khi tìm nút bằng JavaScript: {str(e)}")
    
    # 3. Nếu vẫn không tìm thấy, thử tạo một element mới từ HTML
    if not save_button:
        logging.info("Thử click nút 'Lưu ảnh' bằng innerHTML và dispatch event...")
        try:
            result = driver.execute_script("""
                // Tìm container
                const container = document.querySelector('.c9yG5b');
                
                if (container) {
                    // Thử tìm nút Lưu ảnh trong container
                    const saveButtonContainer = Array.from(container.querySelectorAll('div')).find(
                        div => div.getAttribute('jscontroller') === 'HqNShc'
                    );
                    
                    if (saveButtonContainer) {
                        const button = saveButtonContainer.querySelector('button');
                        if (button) {
                            // Click bằng cách gọi trực tiếp các event handlers
                            try {
                                // Tạo và dispatch các events
                                const mouseDown = new MouseEvent('mousedown', {
                                    bubbles: true,
                                    cancelable: true,
                                    view: window
                                });
                                button.dispatchEvent(mouseDown);
                                
                                setTimeout(() => {
                                    const mouseUp = new MouseEvent('mouseup', {
                                        bubbles: true,
                                        cancelable: true,
                                        view: window
                                    });
                                    button.dispatchEvent(mouseUp);
                                    
                                    setTimeout(() => {
                                        const click = new MouseEvent('click', {
                                            bubbles: true,
                                            cancelable: true,
                                            view: window
                                        });
                                        button.dispatchEvent(click);
                                    }, 50);
                                }, 50);
                                
                                return true;
                            } catch (e) {
                                console.error('Error dispatching events:', e);
                                return false;
                            }
                        }
                    }
                }
                
                // Nếu không tìm thấy, tạo và click phần tử trực tiếp
                try {
                    // Mô tả chính xác HTML của button từ DOM
                    const buttonHtml = `
                        <button class="pYTkkf-Bz112c-LgbsSe pYTkkf-Bz112c-LgbsSe-OWXEXe-SfQLQb-suEOdc KIqTIe cx6Jyd" jscontroller="PIVayb" jsaction="click:h5M12e; clickmod:h5M12e;" data-idom-class="KIqTIe cx6Jyd" data-use-native-focus-logic="true" jsname="LgbsSe" aria-label="Lưu ảnh" jslog="14036; track:JIbuQc">
                            <span class="OiePBf-zPjgPe pYTkkf-Bz112c-UHGRz"></span>
                            <span class="RBHQF-ksKsZd" jsname="m9ZlFb"></span>
                            <span class="pYTkkf-Bz112c-kBDsod-Rtc0Jf" jsname="S5tZuc" aria-hidden="true">
                                <span class="notranslate" aria-hidden="true">
                                    <svg width="24px" height="24px" class="v1262d aRBEtc" jsname="K38HNd" viewBox="0 0 24 24">
                                        <path d="M17.92 10.02C17.45 7.18 14.97 5 12 5 9.82 5 7.83 6.18 6.78 8.06 4.09 8.41 2 10.74 2 13.5 2 16.53 4.47 19 7.5 19h10c2.48 0 4.5-2.02 4.5-4.5a4.5 4.5 0 0 0-4.08-4.48zM17.5 17h-10C5.57 17 4 15.43 4 13.5a3.51 3.51 0 0 1 3.44-3.49l.64-.01.26-.59A3.975 3.975 0 0 1 12 7c2.21 0 4 1.79 4 4v1h1.5a2.5 2.5 0 0 1 0 5zm-3.41-5.91l1.41 1.41-2.79 2.79L12 16l-.71-.71L8.5 12.5l1.41-1.41L11 12.17V9.5h2v2.67l1.09-1.08z"></path>
                                    </svg>
                                </span>
                            </span>
                        </button>
                    `;
                    
                    // Tìm các event handlers cho nút trong DOM
                    const clickHandlers = (
                        document.querySelector('button[jslog="14036"]')?.getAttribute('jsaction') || 
                        'click:h5M12e'
                    );
                    
                    // Kích hoạt trực tiếp hàm xử lý click được đăng ký
                    const handlerFnName = clickHandlers.split('click:')[1]?.split(';')[0];
                    if (handlerFnName && window[handlerFnName]) {
                        window[handlerFnName]();
                        return true;
                    }
                    
                    return false;
                } catch (e) {
                    console.error('Error creating button:', e);
                    return false;
                }
            """)
            
            if result:
                logging.info("Đã kích hoạt nút 'Lưu ảnh' bằng JavaScript events")
                time.sleep(5)
                return True
        except Exception as e:
            logging.error(f"Lỗi khi tạo và kích hoạt nút bằng JavaScript: {str(e)}")
    
    # 4. Nếu tìm thấy nút, thử các cách click khác nhau
    if save_button:
        try:
            # Thử cuộn đến nút
            driver.execute_script("arguments[0].scrollIntoView({behavior: 'instant', block: 'center'});", save_button)
            time.sleep(2)
            
            # 4.1. Thử click thông thường
            try:
                save_button.click()
                logging.info("Đã click nút 'Lưu ảnh' thông thường")
                time.sleep(3)
                return True
            except Exception as e:
                logging.warning(f"Không thể click thông thường: {str(e)}")
                
                # 4.2. Thử click bằng JavaScript
                try:
                    driver.execute_script("arguments[0].click();", save_button)
                    logging.info("Đã click nút 'Lưu ảnh' bằng JavaScript")
                    time.sleep(3)
                    return True
                except Exception as e:
                    logging.warning(f"Không thể click bằng JavaScript: {str(e)}")
                    
                    # 4.3. Thử click bằng ActionChains
                    try:
                        actions = ActionChains(driver)
                        actions.move_to_element(save_button).pause(1).click().perform()
                        logging.info("Đã click nút 'Lưu ảnh' bằng ActionChains")
                        time.sleep(3)
                        return True
                    except Exception as e:
                        logging.warning(f"Không thể click bằng ActionChains: {str(e)}")
                        
                        # 4.4. Thử với JavaScript cao cấp
                        try:
                            driver.execute_script("""
                                const element = arguments[0];
                                
                                // Tạo các events DOM
                                const mouseOverEvent = new MouseEvent('mouseover', {
                                    'view': window,
                                    'bubbles': true,
                                    'cancelable': true
                                });
                                
                                const mouseDownEvent = new MouseEvent('mousedown', {
                                    'view': window,
                                    'bubbles': true,
                                    'cancelable': true
                                });
                                
                                const mouseUpEvent = new MouseEvent('mouseup', {
                                    'view': window,
                                    'bubbles': true,
                                    'cancelable': true
                                });
                                
                                const clickEvent = new MouseEvent('click', {
                                    'view': window,
                                    'bubbles': true,
                                    'cancelable': true
                                });
                                
                                // Kích hoạt các events
                                element.dispatchEvent(mouseOverEvent);
                                
                                setTimeout(() => {
                                    element.dispatchEvent(mouseDownEvent);
                                    
                                    setTimeout(() => {
                                        element.dispatchEvent(mouseUpEvent);
                                        element.dispatchEvent(clickEvent);
                                    }, 100);
                                }, 100);
                            """, save_button)
                            logging.info("Đã kích hoạt nút 'Lưu ảnh' bằng JavaScript events")
                            time.sleep(3)
                            return True
                        except Exception as e:
                            logging.error(f"Không thể kích hoạt bằng JavaScript events: {str(e)}")
        except Exception as e:
            logging.error(f"Lỗi khi cố gắng click nút 'Lưu ảnh': {str(e)}")
    
    # 5. Phương pháp cuối cùng: Gọi trực tiếp hàm xử lý click của Google
    try:
        result = driver.execute_script("""
            // Tìm controller HqNShc trong DOM
            const controllerElement = document.querySelector('div[jscontroller="HqNShc"]');
            if (controllerElement) {
                // Thử kích hoạt hàm xử lý sự kiện KjsqPd của Google
                if (typeof window.google !== 'undefined' && 
                    window.google.ac && 
                    window.google.ac.KjsqPd) {
                    window.google.ac.KjsqPd(controllerElement);
                    return true;
                }
                
                // Tìm kiếm bất kỳ hàm xử lý nào được gắn vào controller
                const protoHandler = controllerElement.__proto__.KjsqPd;
                if (protoHandler) {
                    protoHandler.call(controllerElement);
                    return true;
                }
            }
            return false;
        """)
        
        if result:
            logging.info("Đã kích hoạt hàm xử lý sự kiện bằng JavaScript")
            time.sleep(3)
            return True
    except Exception as e:
        logging.error(f"Không thể kích hoạt hàm xử lý sự kiện: {str(e)}")
    
    logging.error("Đã thử tất cả các phương pháp nhưng không thể click nút 'Lưu ảnh'")
    return False

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
    
    # Chụp ảnh màn hình ban đầu
    driver.save_screenshot("album_page_before.png")
    
    # Gọi hàm click nút Lưu ảnh
    success = click_save_button(driver, wait)
    
    # Kiểm tra kết quả
    if success:
        # Đợi xử lý hoàn tất
        time.sleep(5)
        driver.save_screenshot("after_save_button_click.png")
        
        # Kiểm tra nếu thành công
        try:
            # Kiểm tra SVG "PRE5" không còn style="display: none"
            saved_state = driver.execute_script("""
                return document.querySelector('svg.PRE5').style.display !== 'none';
            """)
            
            if saved_state:
                logging.info("XÁC NHẬN: Đã lưu ảnh thành công!")
            else:
                logging.warning("Đã click nút nhưng không thể xác nhận trạng thái lưu")
        except Exception as e:
            logging.warning(f"Không thể kiểm tra trạng thái lưu: {str(e)}")
    else:
        logging.error("Không thể click nút 'Lưu ảnh'")
    
except Exception as e:
    logging.error(f"Lỗi không xác định: {str(e)}")
    logging.error(traceback.format_exc())
    if 'driver' in locals():
        driver.save_screenshot("error.png")
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