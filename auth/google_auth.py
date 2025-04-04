import os
import json
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow

class GoogleAuth:
    """Xác thực với Google Photos API."""
    
    def __init__(self, scopes=None, credentials_file='credentials.json', token_file='token.json'):
        """
        Khởi tạo đối tượng xác thực Google.
        
        Args:
            scopes: Danh sách các phạm vi xác thực
            credentials_file: Đường dẫn đến file credentials.json
            token_file: Đường dẫn để lưu token
        """
        # Mặc định scopes nếu không được cung cấp
        if scopes is None:
            self.scopes = [
                'https://www.googleapis.com/auth/photoslibrary.readonly',
                'https://www.googleapis.com/auth/photoslibrary.readonly.appcreateddata',
                'https://www.googleapis.com/auth/photoslibrary.sharing'
            ]
        else:
            self.scopes = scopes
        
        self.credentials_file = credentials_file
        self.token_file = token_file
        self.creds = None
    
    def authenticate(self):
        """
        Xác thực với Google API.
        
        Returns:
            Credentials: Thông tin xác thực Google
        """
        # Kiểm tra token đã lưu
        if os.path.exists(self.token_file):
            with open(self.token_file, 'r') as token_file:
                self.creds = Credentials.from_authorized_user_info(
                    json.loads(token_file.read()), self.scopes)
        
        # Nếu không có token hoặc token hết hạn
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                print("Token hết hạn, đang refresh...")
                self.creds.refresh(Request())
            else:
                print("Đang lấy token mới...")
                # Xóa file token.json cũ nếu có
                if os.path.exists(self.token_file):
                    os.remove(self.token_file)
                
                # Tạo flow đăng nhập OAuth với redirect_uri rõ ràng
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_file, 
                    self.scopes,
                    redirect_uri='http://localhost:8080'
                )
                
                # Lấy URL xác thực với tham số cụ thể
                auth_url, _ = flow.authorization_url(
                    prompt='consent',
                    access_type='offline',
                    include_granted_scopes='true'
                )
                print(f"\nVui lòng truy cập URL này để xác thực:\n{auth_url}\n")
                
                # Yêu cầu nhập mã xác thực
                authorization_code = input('Nhập mã xác thực (phần code=... trong URL redirect): ')
                
                # Đổi code lấy token
                flow.fetch_token(code=authorization_code)
                self.creds = flow.credentials
            
            # Lưu token để dùng lại
            with open(self.token_file, "w") as token:
                token.write(self.creds.to_json())
            print("Đã lưu token thành công!")
        
        return self.creds
    
    def get_auth_headers(self):
        """
        Lấy headers xác thực cho API requests.
        
        Returns:
            dict: Headers chứa token xác thực
        """
        if not self.creds:
            self.authenticate()
            
        return {
            'Authorization': f'Bearer {self.creds.token}',
            'Content-type': 'application/json',
        }