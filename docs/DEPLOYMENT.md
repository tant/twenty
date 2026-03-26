# Hướng dẫn Triển khai BVHM CRM

## Tổng quan

BVHM CRM là hệ thống Twenty CRM nguyên bản, được tuỳ biến hoàn toàn qua API bằng script Python. Không sửa dòng code nào của Twenty.

**Thời gian triển khai:** ~25 phút
**Yêu cầu:** Docker, domain, Python 3.10+ với `uv`

---

## Bước 1: Deploy Twenty nguyên bản

### Trên Dokploy (Production)

1. Tạo project mới trên Dokploy
2. Chọn **Compose** → Git → repo `https://github.com/tant/twenty.git`, branch `staging`
3. Compose path: `./docker-compose.yml`
4. Thêm env vars:
   ```
   APP_SECRET=<random-secret-32-chars>
   PG_DATABASE_PASSWORD=<random-password>
   SERVER_URL=https://your-domain.com
   ```
5. Cấu hình domain + HTTPS trong tab Domains
6. Deploy → chờ ~20 phút build

### Trên máy local (Testing)

```bash
export PG_DATABASE_PASSWORD=localtest123
export APP_SECRET=local-test-secret
export SERVER_URL=http://localhost:3000
docker compose up -d
# Chờ ~5 phút cho migrations
```

---

## Bước 2: Tạo tài khoản admin

1. Mở browser → vào URL đã deploy (VD: `https://bvhmsg.fixpartner.co`)
2. Click **"Continue with Email"**
3. Nhập email + password cho tài khoản admin
4. Hoàn tất onboarding (đặt tên workspace, skip phần còn lại)

> Twenty sẽ tự tạo workspace với data mẫu mặc định (Anthropic, Google...).
> Script ở bước 3 sẽ xoá hết và thay bằng data bệnh viện.

---

## Bước 3: Chạy script setup

### Yêu cầu
- Python 3.10+
- `uv` (cài bằng `curl -LsSf https://astral.sh/uv/install.sh | sh`)
- Kết nối mạng tới server Twenty

### 3.1 — Chỉ kiến trúc (cho production, nhập liệu thật)

```bash
uv run scripts/setup-bvhm.py \
  --url https://bvhmsg.fixpartner.co \
  --email admin@bvhm.vn \
  --password <password> \
  --level base
```

**Tạo ra:**
- 22 custom fields trên Bệnh nhân (PID, giới tính, chẩn đoán, thuốc...)
- 13 custom fields trên Công việc CS (loại chăm sóc, trạng thái gọi...)
- 7 views chuyên biệt (CS nội trú, CBNM, thủ thuật, tái khám, beta-thai, thai kỳ, kanban)
- 2 custom objects: Chu kỳ điều trị, Lần nhập viện (có relation với Bệnh nhân)
- 11 Khoa/Phòng khám bệnh viện
- 3 workflows draft (Thai kỳ Auto-Create, Recurring, Cảnh báo quá hạn)
- Dashboard "Báo cáo CSKH" với 6 biểu đồ
- Sidebar tiếng Việt (Các Khoa, Bệnh nhân, Công việc CS, Ghi chú, Báo cáo...)
- Ẩn Opportunities, Workflow Runs, Workflow Versions
- Xoá Quick Lead workflow mặc định
- Xoá data mẫu mặc định (Anthropic, Google, Facebook...)

### 3.2 — Kiến trúc + demo data 3 tháng (cho staging/demo)

```bash
uv run scripts/setup-bvhm.py \
  --url https://bvhmsg.fixpartner.co \
  --email admin@bvhm.vn \
  --password <password> \
  --level demo
```

**Bao gồm tất cả ở 3.1, cộng thêm:**
- 50 bệnh nhân mẫu (tên tiếng Việt, đa dạng giai đoạn điều trị)
- 260 công việc CS trải đều 3 tháng (~3 task/ngày)
- 60 ghi chú lâm sàng (siêu âm, xét nghiệm, tư vấn)
- 35 chu kỳ điều trị (IVF, IUI, CBNM)
- 25 lần nhập viện (HTSS, PT-TT, Sản)
- Tất cả records có link với nhau (task↔bệnh nhân, note↔bệnh nhân...)

---

## Chạy lại script

Script **idempotent** — chạy lại an toàn bất kỳ lúc nào:
- Fields/views/custom objects đã tồn tại → skip
- Data cũ bị xoá → tạo lại từ đầu
- Dashboard cũ bị xoá → tạo mới

```bash
# Reset toàn bộ data và tạo lại
uv run scripts/setup-bvhm.py --url https://... --email ... --password ... --level demo
```

---

## Cấu trúc file

```
neon-bvhm/
├── docker-compose.yml       # Deploy config (chỉ file này + scripts/ khác upstream)
├── scripts/
│   └── setup-bvhm.py       # Script tuỳ biến CRM (~900 lines Python)
└── docs/
    ├── DEPLOYMENT.md        # File này
    └── PRD-BVHM-CRM.md     # Yêu cầu sản phẩm
```

**Chỉ 2 file khác upstream Twenty.** Upgrade Twenty: `git pull upstream/main` → không bao giờ conflict.

---

## Troubleshooting

| Vấn đề | Giải pháp |
|--------|-----------|
| Script lỗi "Workspace not found" | Tạo tài khoản ở Bước 2 trước, đảm bảo đã hoàn tất onboarding |
| Script lỗi "already exists" | Bình thường — field/object đã tồn tại, script tự skip |
| Browser hiện data cũ sau khi chạy script | Hard refresh (`Ctrl+Shift+R`) hoặc mở incognito |
| Build fail trên Dokploy | Check env vars (APP_SECRET, PG_DATABASE_PASSWORD phải có) |
| Dashboard trống | Chạy script lại — dashboard sẽ được tạo mới |

---

## Thông tin Staging hiện tại

- **URL:** https://bvhmsg.fixpartner.co
- **Account:** me@tantran.dev / 2026-Jan
- **Branch:** staging
- **Dokploy:** https://wedeploy.carp.vn → project BVHMSG
- **Auto-deploy:** Bật — push to staging tự deploy
