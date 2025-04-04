import requests
from auth.google_auth import GoogleAuth

class GooglePhotosAPI:
    """Lớp tương tác với Google Photos API."""
    
    def __init__(self, auth=None):
        """
        Khởi tạo đối tượng Google Photos API.
        
        Args:
            auth: Đối tượng GoogleAuth đã được xác thực
        """
        if auth is None:
            auth = GoogleAuth()
            auth.authenticate()
        
        self.auth = auth
        self.base_url = 'https://photoslibrary.googleapis.com/v1'
    
    def get_albums(self, page_size=50, exclude_non_app_created_data=False):
        """
        Lấy danh sách album từ tài khoản.
        
        Args:
            page_size: Số lượng album mỗi trang
            exclude_non_app_created_data: Có loại trừ album không được tạo bởi ứng dụng hay không
            
        Returns:
            list: Danh sách album
        """
        headers = self.auth.get_auth_headers()
        
        print("Đang lấy danh sách tất cả album...")
        response = requests.get(
            f'{self.base_url}/albums',
            headers=headers,
            params={
                'pageSize': page_size,
                'excludeNonAppCreatedData': exclude_non_app_created_data
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            albums = data.get('albums', [])
            
            if not albums:
                print("Không tìm thấy album nào.")
            else:
                print(f"Tìm thấy {len(albums)} album.")
                for album in albums:
                    # Hiển thị thêm thông tin chi tiết
                    shared = album.get('shareInfo', {}).get('isShared', False)
                    shared_info = " (Được chia sẻ)" if shared else ""
                    media_count = album.get('mediaItemsCount', 'N/A')
                    
                    print(f"{album['title']}{shared_info} - {media_count} mục (ID: {album['id']})")
            
            # Kiểm tra nếu có nextPageToken
            if 'nextPageToken' in data:
                print("\nCòn nhiều album khác. Sử dụng nextPageToken để lấy trang tiếp theo.")
                
            return albums, data.get('nextPageToken')
        else:
            print(f"Lỗi khi gọi API: {response.status_code}")
            print(response.text)
            return [], None
    
    def get_shared_albums(self, page_size=50):
        """
        Lấy danh sách album được chia sẻ.
        
        Args:
            page_size: Số lượng album mỗi trang
            
        Returns:
            list: Danh sách album được chia sẻ
        """
        headers = self.auth.get_auth_headers()
        
        print("\nĐang lấy danh sách shared albums...")
        response = requests.get(
            f'{self.base_url}/sharedAlbums',
            headers=headers,
            params={'pageSize': page_size}
        )
        
        if response.status_code == 200:
            data = response.json()
            shared_albums = data.get('sharedAlbums', [])
            
            if not shared_albums:
                print("Không tìm thấy shared album nào.")
            else:
                print(f"Tìm thấy {len(shared_albums)} shared album:")
                for album in shared_albums:
                    media_count = album.get('mediaItemsCount', 'N/A')
                    print(f"{album['title']} - {media_count} mục (ID: {album['id']})")
                    
            return shared_albums, data.get('nextPageToken')
        else:
            print(f"Lỗi khi gọi API shared albums: {response.status_code}")
            print(response.text)
            return [], None