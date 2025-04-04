import requests
import json
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
import os

# Cập nhật scope để có thể đọc tất cả album, bao gồm được chia sẻ
SCOPES = [
    'https://www.googleapis.com/auth/photoslibrary.readonly',
    'https://www.googleapis.com/auth/photoslibrary.readonly.appcreateddata',
    'https://www.googleapis.com/auth/photoslibrary.sharing'
]

# Kiểm tra token đã lưu
creds = None
if os.path.exists('token.json'):
    with open('token.json', 'r') as token_file:
        creds = Credentials.from_authorized_user_info(json.loads(token_file.read()), SCOPES)

# Nếu không có token hoặc token hết hạn
if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        print("Token hết hạn, đang refresh...")
        creds.refresh(Request())
    else:
        print("Đang lấy token mới...")
        # Xóa file token.json cũ nếu có
        if os.path.exists('token.json'):
            os.remove('token.json')
            
        # Tạo flow đăng nhập OAuth với redirect_uri rõ ràng
        flow = InstalledAppFlow.from_client_secrets_file(
            'credentials.json', 
            SCOPES,
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
        creds = flow.credentials
    
    # Lưu token để dùng lại
    with open("token.json", "w") as token:
        token.write(creds.to_json())
    print("Đã lưu token thành công!")

# Sử dụng requests để gọi API trực tiếp
print("Đang kết nối với Google Photos API...")
headers = {
    'Authorization': f'Bearer {creds.token}',
    'Content-type': 'application/json',
}

# Gọi API liệt kê tất cả album
print("Đang lấy danh sách tất cả album...")
response = requests.get(
    'https://photoslibrary.googleapis.com/v1/albums',
    headers=headers,
    params={
        'pageSize': 50,
        'excludeNonAppCreatedData': False  # Quan trọng: bao gồm album không phải do ứng dụng tạo
    }
)

if response.status_code == 200:
    data = response.json()
    albums = data.get('albums', [])
    
    if not albums:
        print("Không tìm thấy album nào.")
    else:
        print(f"Tìm thấy {len(albums)} album:")
        for album in albums:
            # Hiển thị thêm thông tin chi tiết
            shared = album.get('shareInfo', {}).get('isShared', False)
            shared_info = " (Được chia sẻ)" if shared else ""
            media_count = album.get('mediaItemsCount', 'N/A')
            
            print(f"{album['title']}{shared_info} - {media_count} mục (ID: {album['id']})")
            
    # Kiểm tra nếu có nextPageToken
    if 'nextPageToken' in data:
        print("\nCòn nhiều album khác. Sử dụng nextPageToken để lấy trang tiếp theo.")
else:
    print(f"Lỗi khi gọi API: {response.status_code}")
    print(response.text)

# Thêm phần liệt kê album được chia sẻ
print("\nĐang lấy danh sách shared albums...")
shared_response = requests.get(
    'https://photoslibrary.googleapis.com/v1/sharedAlbums',
    headers=headers,
    params={'pageSize': 50}
)

if shared_response.status_code == 200:
    shared_data = shared_response.json()
    shared_albums = shared_data.get('sharedAlbums', [])
    
    if not shared_albums:
        print("Không tìm thấy shared album nào.")
    else:
        print(f"Tìm thấy {len(shared_albums)} shared album:")
        for album in shared_albums:
            media_count = album.get('mediaItemsCount', 'N/A')
            print(f"{album['title']} - {media_count} mục (ID: {album['id']})")
else:
    print(f"Lỗi khi gọi API shared albums: {shared_response.status_code}")
    print(shared_response.text)