# BÁO CÁO KẾT QUẢ LAB 24: DATA GOVERNANCE & SECURITY

## 1. Giới thiệu Dự án (Scenario)
Dự án nhằm xây dựng pipeline quản trị dữ liệu (data governance pipeline) cho **MedViet**, xử lý thông tin nhạy cảm của bệnh nhân phục vụ huấn luyện mô hình chẩn đoán bệnh bảo đảm tuân thủ Nghị định 13/2023/NĐ-CP (NĐ13) và tiêu chuẩn bảo mật dữ liệu y tế.

---

## 2. Các thành phần đã triển khai (Implemented Architectures)

### 2.1. Chuẩn bị Dữ liệu & Nhận diện PII (PII Detection & Anonymization)
- **PII Detection:** Tích hợp `Presidio Analyzer` kết hợp mô hình NLP spaCy Vietnamese (`vi_core_news_lg`). Đăng ký custom recognizers cho các trường dữ liệu Việt Nam đặc thù:
  - **CCCD (Căn cước công dân):** Nhận diện định dạng chuẩn 12 số của Việt Nam.
  - **Số điện thoại:** Nhận diện số điện thoại với các đầu số Việt Nam di động phổ biến (`03`, `05`, `07`, `08`, `09`).
  - **PERSON & EMAIL:** Sử dụng bộ recognizers mặc định tối ưu cho tiếng Việt.
- **Anonymization Strategies:** Hỗ trợ linh hoạt các chiến lược ẩn danh tại [anonymizer.py](file:///d:/vinai/Day24-2A202600926-MaiVanThuyen/medviet-governance/src/pii/anonymizer.py):
  - `replace`: Thay thế các giá trị PII nhạy cảm (Tên, Email, CCCD, SĐT) bằng dữ liệu giả lập từ thư viện `Faker` phù hợp với Việt Nam.
  - `mask`: Che giấu ký tự nhạy cảm (ví dụ: `Nguyen Van A` -> `N****** V** A`).
  - `hash`: Băm bảo mật một chiều SHA-256 đối với các dữ liệu cần định danh gián tiếp.
- **Kết quả đạt được:** Tỷ lệ nhận dạng PII thực tế đạt **100% (vượt mức tối thiểu 95% của Lab)**.

### 2.2. Kiểm soát Truy cập (RBAC & ABAC Access Control)
- **Role-Based Access Control (RBAC):** Tích hợp công cụ `Casbin` quản lý chính sách kế thừa quyền (`admin` -> `ml_engineer` -> `data_analyst` -> `intern`) tại [policy.csv](file:///d:/vinai/Day24-2A202600926-MaiVanThuyen/medviet-governance/src/access/policy.csv).
- **FastAPI Integration:** Bảo vệ các API endpoint nhạy cảm bằng Decorator kiểm tra quyền (`require_permission`) và cơ chế xác thực Mock Bearer Tokens:
  - `/api/patients/raw`: Chỉ `admin` được phép đọc dữ liệu gốc.
  - `/api/patients/anonymized`: `ml_engineer` và `admin` được đọc để huấn luyện mô hình.
  - `/api/metrics/aggregated`: `data_analyst`, `ml_engineer` và `admin` được phép đọc thống kê tổng hợp.
  - `/api/patients/{patient_id}` [DELETE]: Chỉ duy nhất `admin` được quyền xóa.
- **Attribute-Based Access Control (ABAC - OPA):** Xây dựng chính sách OPA tại [opa_policy.rego](file:///d:/vinai/Day24-2A202600926-MaiVanThuyen/medviet-governance/policies/opa_policy.rego) tăng cường kiểm soát ranh giới dữ liệu nhạy cảm (Không xuất khẩu dữ liệu restricted ra ngoài máy chủ Việt Nam).

### 2.3. Mã hóa Dữ liệu (Encryption Vault)
- **Envelope Encryption Pattern:** Hiện thực cơ chế mã hóa phong bì bằng thuật toán đối xứng **AES-256-GCM** bảo mật tại [vault.py](file:///d:/vinai/Day24-2A202600926-MaiVanThuyen/medviet-governance/src/encryption/vault.py):
  - Khóa chính **KEK (Key Encryption Key)** được lưu độc lập tại `.vault_key`.
  - Khóa dữ liệu **DEK (Data Encryption Key)** được sinh mới ngẫu nhiên cho mỗi bản ghi dữ liệu, mã hóa bằng KEK và lưu cùng với ciphertext.
  - Đảm bảo huỷ hoàn toàn khoá thô DEK khỏi bộ nhớ RAM ngay khi hoàn tất tác vụ mã hóa.

### 2.4. Kiểm định Chất lượng (Data Quality Validation)
- Cấu hình bộ quy tắc kiểm định **Great Expectations 1.x** đối với dữ liệu bệnh nhân tại [validation.py](file:///d:/vinai/Day24-2A202600926-MaiVanThuyen/medviet-governance/src/quality/validation.py):
  - Đảm bảo `patient_id` không Null và là duy nhất.
  - Đảm bảo cột `cccd` có độ dài đúng 12 ký tự.
  - Đảm bảo `ket_qua_xet_nghiem` nằm trong dải đo an toàn `[0, 50]`.
  - Đảm bảo cột `benh` và `email` hợp lệ.

### 2.5. Bảo mật & Quét Tĩnh (Security Audit)
- Tích hợp công cụ quét lỗ hổng tĩnh **Bandit** ghi nhận báo cáo sạch [bandit_report.json](file:///d:/vinai/Day24-2A202600926-MaiVanThuyen/medviet-governance/reports/bandit_report.json).
- Tích hợp **git-secrets** chặn lộ mật khẩu/CCCD/AWS keys trước khi commit code.
- Quét lịch sử mã nguồn bằng **TruffleHog** ghi nhận báo cáo an toàn [trufflehog_report.txt](file:///d:/vinai/Day24-2A202600926-MaiVanThuyen/medviet-governance/reports/trufflehog_report.txt).

---

## 3. Kết quả Kiểm thử (Verification Test Suite Results)
Hệ thống kiểm thử tự động với 16 ca kiểm thử bao phủ toàn bộ chức năng đã chạy thành công tốt đẹp:

```
tests/test_api.py::test_health PASSED
tests/test_api.py::test_admin_access PASSED
tests/test_api.py::test_ml_engineer_access PASSED
tests/test_api.py::test_data_analyst_access PASSED
tests/test_api.py::test_intern_access PASSED
tests/test_api.py::test_unauthorized_access PASSED
tests/test_pii.py::TestPIIDetection::test_cccd_detected PASSED
tests/test_pii.py::TestPIIDetection::test_phone_detected PASSED
tests/test_pii.py::TestPIIDetection::test_email_detected PASSED
tests/test_pii.py::TestPIIDetection::test_detection_rate_above_95_percent PASSED
tests/test_pii.py::TestAnonymization::test_pii_not_in_output PASSED
tests/test_pii.py::TestAnonymization::test_non_pii_columns_unchanged PASSED
tests/test_validation.py::test_validation_suite PASSED
tests/test_validation.py::test_validate_anonymized_data PASSED
tests/test_vault.py::test_vault_roundtrip PASSED
tests/test_vault.py::test_vault_encrypt_column PASSED

===> 16 passed in 27.71s <===
```
Báo cáo kiểm thử tự động chi tiết được lưu trữ tại [test_results.txt](file:///d:/vinai/Day24-2A202600926-MaiVanThuyen/medviet-governance/reports/test_results.txt).

---

## 4. Đánh giá tính tuân thủ Nghị định 13/2023/NĐ-CP
- **Lưu trữ nội địa:** Toàn bộ dữ liệu thô và bản sao lưu được lưu trữ trên hạ tầng máy chủ của công ty đặt tại Việt Nam.
- **Đồng ý tường minh (Consent):** MedViet thu thập sự đồng ý rõ ràng của người bệnh trước khi xử lý dữ liệu và cung cấp quyền rút đồng ý (Right to Erasure).
- **Phản ứng sự cố:** Có quy trình thông báo vi phạm dữ liệu cá nhân trong vòng 72 giờ và bộ phận DPO chuyên trách (`dpo@medviet.vn`).
- **An toàn kỹ thuật:** Ẩn danh hóa dữ liệu triệt để trước khi huấn luyện mô hình AI, áp dụng mã hóa tĩnh cấp độ mạnh và ghi nhật ký kiểm toán (Audit Logs) hoàn chỉnh.
