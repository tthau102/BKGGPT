import os
from dotenv import load_dotenv

# Tải biến môi trường từ file .env
load_dotenv()

# Thiết lập đường dẫn
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOGS_DIR = os.path.join(BASE_DIR, "logs")
SCREENSHOTS_DIR = os.path.join(BASE_DIR, "screenshots")

# Thiết lập tài khoản Google
GOOGLE_EMAIL = os.environ.get('GOOGLE_EMAIL')
GOOGLE_PASSWORD = os.environ.get('GOOGLE_PASSWORD')

# Thiết lập API và xác thực
CREDENTIALS_FILE = os.environ.get('CREDENTIALS_FILE', 'credentials.json')
TOKEN_FILE = os.environ.get('TOKEN_FILE', 'token.json')

# Thiết lập Album
ALBUM_URL = os.environ.get('ALBUM_URL')

# Thiết lập Selenium
HEADLESS_MODE = os.environ.get('HEADLESS_MODE', 'True').lower() in ('true', '1', 't')
CHROME_DRIVER_PATH = os.environ.get('CHROME_DRIVER_PATH', None)

# Thiết lập logging
LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')

# OAuth2 scopes
SCOPES = [
    'https://www.googleapis.com/auth/photoslibrary.readonly',
    'https://www.googleapis.com/auth/photoslibrary.readonly.appcreateddata',
    'https://www.googleapis.com/auth/photoslibrary.sharing'
]