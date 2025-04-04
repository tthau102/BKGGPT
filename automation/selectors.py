"""
Tập hợp các selector cho việc tự động hóa Google Photos.
Tách ra để dễ bảo trì khi Google thay đổi UI.
"""

# Selectors cho trang đăng nhập
LOGIN_SELECTORS = {
    # Email input selectors
    'email_input': [
        {'by': 'id', 'value': 'identifierId'},
        {'by': 'xpath', 'value': "//input[@type='email']"},
        {'by': 'xpath', 'value': "//input[@aria-label='Email or phone']"}
    ],
    
    # Email next button selectors
    'email_next_button': [
        {'by': 'id', 'value': 'identifierNext'},
        {'by': 'xpath', 'value': "//button[contains(text(), 'Next')]"},
        {'by': 'xpath', 'value': "//span[contains(text(), 'Next')]/ancestor::button"}
    ],
    
    # Password input selectors
    'password_input': [
        {'by': 'name', 'value': 'Passwd'},
        {'by': 'xpath', 'value': "//input[@type='password']"},
        {'by': 'xpath', 'value': "//input[@aria-label='Enter your password']"}
    ],
    
    # Password next button selectors
    'password_next_button': [
        {'by': 'id', 'value': 'passwordNext'},
        {'by': 'xpath', 'value': "//button[contains(text(), 'Next')]"},
        {'by': 'xpath', 'value': "//span[contains(text(), 'Next')]/ancestor::button"}
    ]
}

# Selectors cho trang album
ALBUM_SELECTORS = {
    # Save button selectors
    'save_button': [
        {'by': 'xpath', 'value': "//button[contains(@aria-label, 'Lưu')]"},
        {'by': 'xpath', 'value': "//button[contains(text(), 'Lưu')]"}
    ]
}