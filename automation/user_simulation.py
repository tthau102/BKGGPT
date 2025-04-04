import time
import random
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

class UserSimulation:
    """
    Cung cấp các phương thức để mô phỏng hành vi người dùng thực trong browser.
    """
    
    @staticmethod
    def human_type(element, text, min_delay=0.05, max_delay=0.25):
        """
        Mô phỏng việc gõ phím như người dùng thực.
        
        Args:
            element: Phần tử web để nhập text
            text: Chuỗi để nhập
            min_delay: Độ trễ tối thiểu giữa các phím
            max_delay: Độ trễ tối đa giữa các phím
        """
        for char in text:
            element.send_keys(char)
            # Thời gian delay ngẫu nhiên giữa các phím
            time.sleep(random.uniform(min_delay, max_delay))
        
        # Đôi khi dừng lại lâu hơn (mô phỏng người dùng suy nghĩ)
        if random.random() < 0.2:  # 20% cơ hội dừng lại lâu hơn
            time.sleep(random.uniform(0.5, 1.5))

    @staticmethod
    def human_move_and_click(driver, element):
        """
        Mô phỏng di chuyển chuột và click như người dùng thực.
        
        Args:
            driver: WebDriver đang sử dụng
            element: Phần tử web để click
        """
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

    @staticmethod
    def human_scroll(driver, direction='down', pixels=None, smooth=True):
        """
        Mô phỏng việc cuộn trang như người dùng thực.
        
        Args:
            driver: WebDriver đang sử dụng
            direction: Hướng cuộn ('up' hoặc 'down')
            pixels: Số pixel để cuộn
            smooth: Có cuộn mượt hay không
        """
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

    @staticmethod
    def simulate_random_actions(driver):
        """
        Mô phỏng các hành động ngẫu nhiên của người dùng thực.
        
        Args:
            driver: WebDriver đang sử dụng
        """
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