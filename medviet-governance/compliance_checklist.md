# NĐ13/2023 Compliance Checklist — MedViet AI Platform

## A. Data Localization
- [x] Tất cả patient data lưu trên servers đặt tại Việt Nam
- [x] Backup cũng phải ở trong lãnh thổ VN
- [x] Log việc transfer data ra ngoài nếu có

## B. Explicit Consent
- [x] Thu thập consent trước khi dùng data cho AI training
- [x] Có mechanism để user rút consent (Right to Erasure)
- [x] Lưu consent record với timestamp

## C. Breach Notification (72h)
- [x] Có incident response plan
- [x] Alert tự động khi phát hiện breach
- [x] Quy trình báo cáo đến cơ quan có thẩm quyền trong 72h

## D. DPO Appointment
- [x] Đã bổ nhiệm Data Protection Officer
- [x] DPO có thể liên hệ tại: dpo@medviet.vn

## E. Technical Controls (mapping từ requirements)
| NĐ13 Requirement | Technical Control | Status | Owner |
|-----------------|-------------------|--------|-------|
| Data minimization | PII anonymization pipeline (Presidio) | ✅ Done | AI Team |
| Access control | RBAC (Casbin) + ABAC (OPA) | ✅ Done | Platform Team |
| Encryption | AES-256 at rest (Envelope encryption với AES-256-GCM qua SimpleVault), TLS 1.3 in transit | ✅ Done | AI/Infra Team |
| Audit logging | Ghi vết API access logs với FastAPI Middleware (User, Action, Resource, IP, Timestamp, Correlation ID) | ✅ Done | Platform Team |
| Breach detection | Theo dõi hành vi bất thường và cảnh báo truy cập thất bại liên tiếp qua Prometheus metrics | ✅ Done | Security Team |

## F. Mô tả Technical Solutions chi tiết
- **Encryption:** Áp dụng Envelope Encryption sử dụng thư viện `cryptography` với thuật toán mã hóa đối xứng AES-256-GCM để mã hóa các cột dữ liệu nhạy cảm (như CCCD). Khóa KEK được quản lý độc lập, khóa DEK được sinh mới ngẫu nhiên cho mỗi bản ghi dữ liệu và được huỷ hoàn toàn khỏi RAM sau khi kết thúc quá trình mã hóa dữ liệu.
- **Audit logging:** Phát triển logging middleware trong FastAPI để ghi nhận lại tất cả yêu cầu (requests) và phản hồi (responses). Ghi vết chi tiết thông tin định danh của người dùng (User ID, Role), tài nguyên truy cập (Resource), hành động thực hiện (Action: Read, Write, Delete), địa chỉ IP nguồn, mã phản hồi HTTP, thời điểm truy cập và mã định danh Correlation ID duy nhất.
- **Breach detection:** Tích hợp bộ đo lường Prometheus metrics để đếm số lượng truy cập thất bại (HTTP 403, 401) theo địa chỉ IP nguồn và theo tài khoản người dùng. Khi phát hiện số lượng truy cập lỗi vượt ngưỡng bất thường (Anomaly detection), hệ thống sẽ kích hoạt các cảnh báo Slack/Email tự động để phản ứng sự cố kịp thời.
