# E-Course Management

Hệ thống quản lý khóa học trực tuyến được xây dựng bằng Flask, giúp quản lý người dùng, khóa học, chương học, bài học, bài kiểm tra, thanh toán và tương tác học tập trực tuyến. Dự án tích hợp AI để gợi ý khóa học phù hợp, đồng thời hỗ trợ lưu trữ file qua Google Drive và Cloudinary.

## Tác giả

- BeAFA
- DinhNguyen9404
- HuySaBo

## Giới thiệu

E-Course Management là một nền tảng học trực tuyến cho phép:

- Quản lý học viên, giáo viên và quản trị viên
- Tạo và quản lý khóa học theo danh mục và tag
- Quản lý chương học, bài giảng, video, tài liệu
- Tạo bài kiểm tra và theo dõi điểm số
- Phê duyệt/đánh giá khóa học
- Chat trực tiếp giữa học viên và giáo viên
- Tích hợp AI để gợi ý khóa học theo nhu cầu người dùng
- Cấp chứng chỉ sau khi hoàn thành khóa học
- Hỗ trợ thanh toán với VNPAY

## Tính năng chính

- Quản lý tài khoản và phân quyền
  - Admin
  - Teacher
  - Student

- Quản lý khóa học
  - Thêm, sửa, xóa khóa học
  - Chọn danh mục và tag
  - Cập nhật hình ảnh khóa học
  - Tìm kiếm và lọc khóa học

- Quản lý nội dung học tập
  - Tạo chương học
  - Thêm bài giảng
  - Tải lên video, hình ảnh và tài liệu PDF
  - Xem bài giảng chi tiết

- Hệ thống kiểm tra
  - Tạo bài thi
  - Thêm câu hỏi và đáp án
  - Chấm điểm và hiển thị kết quả
  - Hỗ trợ chứng chỉ sau khi hoàn thành

- Chat và tương tác
  - Chat trực tiếp giữa học viên và giáo viên
  - Chat AI để hỗ trợ tư vấn và đề xuất khóa học

- AI Recommendation
  - Tích hợp Gemini API
  - Gợi ý khóa học phù hợp dựa trên ngữ cảnh và lịch sử tương tác

- Thanh toán
  - Tích hợp VNPAY sandbox
  - Đăng ký khóa học có phí hoặc miễn phí

- Lưu trữ file
  - Cloudinary cho ảnh/video/tài liệu
  - Google Drive cho các file dạng lưu trữ

## Công nghệ sử dụng

- Python
- Flask
- Flask-SQLAlchemy
- Flask-Login
- Flask-SocketIO
- MySQL
- HTML / CSS / JavaScript
- Google Gemini API
- Google Drive API
- Cloudinary
- VNPAY

## Cấu trúc dự án

```text
E-Course-Management/
├── .github/
├── ecourseapp/
│   ├── __init__.py
│   ├── admin.py
│   ├── ai_chat_routes.py
│   ├── app.py
│   ├── dao.py
│   ├── get_token.py
│   ├── models.py
│   ├── seed_data.py
│   ├── test.py
│   ├── vnpay.py
│   ├── credentials/
│   │   ├── ai_api_key.json
│   │   ├── client_secret.json
│   │   ├── drive_key.json
│   │   └── Test_User.txt
│   ├── services/
│   │   ├── cloudinary_service.py
│   │   └── drive_service.py
│   ├── static/
│   │   ├── css/
│   │   ├── img/
│   │   └── js/
│   └── templates/
│       ├── admin/
│       ├── layout/
│       └── ...
├── .gitignore
├── LICENSE
├── README.md
├── requirements.txt
└── ...
```

## Yêu cầu hệ thống

- Python 3.10+
- MySQL
- Pip
- Tài khoản Google Cloud (nếu dùng Gemini/Drive)
- Tài khoản Cloudinary
- Tài khoản VNPAY (nếu tích hợp thanh toán)

## Cài đặt

### 1. Clone repository

```bash
git clone https://github.com/BeAFA/E-Course-Management.git
cd E-Course-Management
```

### 2. Tạo môi trường ảo

```bash
python -m venv venv
```

Trên Linux/macOS:

```bash
source venv/bin/activate
```

Trên Windows:

```bash
venv\Scripts\activate
```

### 3. Cài đặt dependency

```bash
pip install -r requirements.txt
```

## Cấu hình môi trường

Tạo file `.env` hoặc cấu hình các biến môi trường cần thiết:

```env
DATABASE_URL=mysql+pymysql://root:your_password@localhost/ecoursedb?charset=utf8mb4
VNPAY_TMN_CODE=your_vnpay_tmn_code
VNPAY_HASH_SECRET=your_vnpay_hash_secret
VNPAY_URL=https://sandbox.vnpayment.vn/paymentv2/vpcpay.html
VNPAY_RETURN_URL=http://localhost:5000/payment/vnpay_return
CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_api_key
CLOUDINARY_API_SECRET=your_api_secret
```

Ngoài ra, dự án có các file cấu hình AI và credentials trong thư mục:

```text
ecourseapp/credentials/
```

Ví dụ:
- `ai_api_key.json`
- `drive_key.json`

## Tạo database

Tạo database MySQL:

```sql
CREATE DATABASE ecoursedb;
```

Sau đó tạo schema:

```bash
python
from ecourseapp import app, db
with app.app_context():
    db.create_all()
```

## Chạy ứng dụng

```bash
python ecourseapp/app.py
```

Ứng dụng sẽ chạy tại:

```text
http://localhost:5000
```

## Hướng dẫn sử dụng

1. Đăng ký tài khoản
   - Học viên
   - Giáo viên
   - Quản trị viên

2. Quản lý khóa học
   - Tạo khóa học mới
   - Chọn thể loại và tag
   - Tải ảnh bìa

3. Quản lý bài học
   - Thêm chương học
   - Thêm bài giảng
   - Upload video và tài liệu

4. Kiểm tra
   - Tạo bài thi
   - Thêm câu hỏi và đáp án
   - Theo dõi điểm số của học viên

5. Tương tác và AI
   - Gửi câu hỏi qua AI chat
   - Nhận đề xuất khóa học phù hợp

6. Thanh toán
   - Đăng ký khóa học có phí qua VNPAY

7. Chứng chỉ
   - Học viên nhận chứng chỉ sau khi hoàn thành yêu cầu

## Tích hợp AI

Dự án tích hợp Google Gemini để hỗ trợ:

- Trả lời câu hỏi của người dùng
- Gợi ý khóa học
- Tương tác trên giao diện AI Chat
- Lưu lịch sử cuộc trò chuyện và khóa học được đề xuất

## Tích hợp lưu trữ dữ liệu

### Cloudinary
Dùng để lưu trữ:
- Hình ảnh khóa học
- Hình ảnh người dùng
- Video
- Tài liệu PDF

### Google Drive
Dùng để upload và quản lý file liên quan đến bài giảng và tài liệu học tập.

## Hạn chế và lưu ý

- Một số cấu hình như API key, secret key và database connection cần được cấu hình đúng trước khi chạy.
- Nếu dùng VNPAY và Google API, cần đảm bảo môi trường chạy có quyền truy cập và cấu hình hợp lệ.
- Một số file credentials có thể cần được giữ riêng do chứa thông tin nhạy cảm.

## Giấy phép

Dự án này được phân phối theo giấy phép MIT. Xem file `LICENSE` để biết chi tiết.

## Đóng góp

Mọi đóng góp đều được hoan nghênh. Nếu bạn muốn phát triển thêm dự án, vui lòng:

1. Fork repository
2. Tạo branch mới
3. Commit thay đổi
4. Mở Pull Request

## Liên hệ

- GitHub: https://github.com/BeAFA
- GitHub: https://github.com/DinhNguyen9404
- GitHub: https://github.com/letrieuhuysabo

## Kết luận

E-Course Management là một dự án quản lý học trực tuyến đầy đủ tính năng, tích hợp AI, thanh toán, chat và hệ thống khóa học. Đây là một sản phẩm phù hợp cho việc học tập, phát triển hệ thống web và tạo nền tảng giáo dục trực tuyến hiện đại.
