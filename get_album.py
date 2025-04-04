from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import os

# Khai báo scope bạn muốn dùng. Có thể đổi thành 'photoslibrary' nếu cần quyền ghi.
SCOPES = ['https://www.googleapis.com/auth/photoslibrary.readonly']

# Tạo flow đăng nhập OAuth
flow = InstalledAppFlow.from_client_secrets_file(
    'credentials.json', SCOPES)

# Chạy local server để đăng nhập và cấp quyền
creds = flow.run_local_server(port=0)

# Lưu token để dùng lại nếu muốn (tùy chọn)
with open("token.json", "w") as token:
    token.write(creds.to_json())

# Tạo đối tượng dịch vụ để gọi API
service = build('photoslibrary', 'v1', credentials=creds)

# Gọi thử API liệt kê album
results = service.albums().list(
    pageSize=10, fields="albums(id,title),nextPageToken").execute()
albums = results.get('albums', [])

if not albums:
    print("Không tìm thấy album nào.")
else:
    print("Danh sách album:")
    for album in albums:
        print(f"{album['title']} (ID: {album['id']})")
