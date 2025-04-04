# BKGGPT

Công cụ backup Google Photos tự động giữa các tài khoản Google.

## Tính năng

- Lấy danh sách album từ Google Photos API
- Tự động đăng nhập và sao chép media từ album được chia sẻ

## Cài đặt

1. Clone repository
```bash
git clone https://github.com/your-username/bkggpt.git
cd bkggpt
```

2. Cài đặt dependencies
```bash
pip install -r requirements.txt
```

3. Tạo file .env từ .env.example
```bash
cp .env.example .env
```

4. Cập nhật thông tin trong file .env
```
GOOGLE_EMAIL=your_backup_email@gmail.com
GOOGLE_PASSWORD=your_backup_password
ALBUM_URL=https://photos.app.goo.gl/your-shared-album-url
```

5. Thiết lập API Google Photos:
   - Truy cập [Google Cloud Console](https://console.cloud.google.com/)
   - Tạo project mới
   - Bật Google Photos Library API
   - Tạo credentials OAuth2
   - Tải credentials.json về thư mục gốc của project

## Sử dụng

### Lấy danh sách album

```bash
python main.py list
```

### Sao chép album được chia sẻ

```bash
# Sử dụng URL từ file .env
python main.py clone

# Hoặc chỉ định URL trực tiếp
python main.py clone --url "https://photos.app.goo.gl/your-shared-album-url"
```

## Cấu trúc project

```
bkggpt/
├── README.md                  # Tài liệu hướng dẫn
├── config/                    # Cấu hình và thông số
│   ├── __init__.py
│   └── settings.py            # Các thông số cấu hình
├── auth/                      # Module xác thực
│   ├── __init__.py
│   └── google_auth.py         # Logic xác thực Google
├── api/                       # Module tương tác API
│   ├── __init__.py
│   └── photos_api.py          # Logic gọi Google Photos API
├── automation/                # Module tự động hóa
│   ├── __init__.py
│   ├── browser.py             # Quản lý trình duyệt Selenium
│   ├── user_simulation.py     # Mô phỏng hành vi người dùng
│   └── selectors.py           # Các selector UI cần tìm
├── utils/                     # Tiện ích
│   ├── __init__.py
│   ├── logging_utils.py       # Cấu hình logging
│   └── file_utils.py          # Xử lý file
├── main.py                    # Entry point chính
├── requirements.txt           # Dependency
└── .env                       # Biến môi trường (không commit)
```