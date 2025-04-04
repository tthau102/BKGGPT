import time
import random
import traceback
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from automation.user_simulation import UserSimulation
from automation.selectors import ALBUM_SELECTORS

class AlbumHandler:
    """Xử lý thao tác với album Google Photos."""
    
    def __init__(self, browser):
        """
        Khởi tạo đối tượng xử lý album.
        
        Args:
            browser: Đối tượng Browser đã khởi tạo
        """
        self.browser = browser
        self.driver = browser.driver
        self.wait = browser.wait
        self.logger = browser.logger
    
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
            self.browser.screenshot("photos_homepage.png")
    
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
            self.browser.screenshot("album_page.png")
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
            self.browser.screenshot("album_error.png")
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
            save_button = self.browser.find_element_from_candidates(ALBUM_SELECTORS['save_button'])
            
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
                
                self.browser.screenshot("before_save_click.png")
                
                # Mô phỏng việc di chuyển chuột và click vào nút Lưu
                UserSimulation.human_move_and_click(self.driver, save_button)
                self.logger.info("Đã click nút 'Lưu ảnh'")
                
                # Đợi xử lý với thời gian biến thiên
                time.sleep(random.uniform(3.0, 5.0))
                self.browser.screenshot("after_save_click.png")
                
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
                    self.browser.screenshot("after_js_save_click.png")
                    
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
            self.browser.screenshot("save_photos_error.png")
            return False