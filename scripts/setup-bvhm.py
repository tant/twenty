#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["httpx"]
# ///
"""
BVHM Hospital CRM Setup Script

Transforms a stock Twenty CRM into a fully-configured BVHM hospital CRM
via the API. No code modifications to Twenty required.

Usage:
    # Level 1: Base setup (hospital structure, custom fields, views — no patient data)
    uv run scripts/setup-bvhm.py --url https://bvhmsg.fixpartner.co --email admin@bvhm.vn --password xxx --level base

    # Level 2: Demo data (includes base + 8 patients, 12 tasks, 8 notes)
    uv run scripts/setup-bvhm.py --url https://bvhmsg.fixpartner.co --email admin@bvhm.vn --password xxx --level demo
"""

import argparse
import sys
import json
from datetime import datetime, timedelta

import httpx

# =============================================================================
# BVHM FIELD DEFINITIONS
# =============================================================================

PERSON_FIELDS = [
    {"name": "pid", "label": "PID", "type": "TEXT", "icon": "IconId", "description": "Mã bệnh nhân từ HIS"},
    {"name": "yearOfBirth", "label": "Năm sinh", "type": "NUMBER", "icon": "IconCalendar"},
    {"name": "dateOfBirth", "label": "Ngày sinh", "type": "DATE", "icon": "IconCake"},
    {"name": "gender", "label": "Giới tính", "type": "SELECT", "icon": "IconGenderBigender",
     "options": [{"label": "Nam", "value": "NAM", "position": 0, "color": "blue"},
                 {"label": "Nữ", "value": "NU", "position": 1, "color": "red"}]},
    {"name": "cccd", "label": "CCCD", "type": "TEXT", "icon": "IconIdBadge2"},
    {"name": "patientSource", "label": "Nguồn", "type": "SELECT", "icon": "IconRoute",
     "options": [{"label": "Marketing", "value": "MARKETING", "position": 0, "color": "blue"},
                 {"label": "Bệnh viện", "value": "BENH_VIEN", "position": 1, "color": "green"},
                 {"label": "Bác sĩ hợp tác", "value": "BAC_SI_HOP_TAC", "position": 2, "color": "turquoise"},
                 {"label": "Khác", "value": "KHAC", "position": 3, "color": "sky"}]},
    {"name": "referralPartner", "label": "Đối tác giới thiệu", "type": "TEXT", "icon": "IconUsersGroup"},
    {"name": "diagnosis", "label": "Chẩn đoán", "type": "TEXT", "icon": "IconStethoscope"},
    {"name": "contactPerson", "label": "Người liên hệ", "type": "TEXT", "icon": "IconUser"},
    {"name": "contactPhone", "label": "SĐT liên hệ", "type": "TEXT", "icon": "IconPhone"},
    {"name": "spouseName", "label": "Tên vợ/chồng", "type": "TEXT", "icon": "IconHeart"},
    {"name": "spousePid", "label": "PID vợ/chồng", "type": "TEXT", "icon": "IconId"},
    {"name": "spousePhone", "label": "SĐT vợ/chồng", "type": "TEXT", "icon": "IconPhone"},
    {"name": "medication", "label": "Thuốc đang dùng", "type": "TEXT", "icon": "IconPill"},
    {"name": "currentCycle", "label": "Chu kỳ hiện tại", "type": "TEXT", "icon": "IconRepeat"},
    {"name": "iuiDate", "label": "Ngày bơm IUI", "type": "DATE_TIME", "icon": "IconCalendar"},
    {"name": "embryoTransferDate", "label": "Ngày chuyển phôi", "type": "DATE_TIME", "icon": "IconCalendar"},
    {"name": "betaResult", "label": "Kết quả Beta", "type": "TEXT", "icon": "IconHeartbeat"},
    {"name": "cancelReason", "label": "Lý do hủy chu kỳ", "type": "TEXT", "icon": "IconAlertTriangle"},
    {"name": "clinicRoom", "label": "Phòng khám", "type": "TEXT", "icon": "IconBuilding"},
    {"name": "doctorName", "label": "BS phụ trách", "type": "TEXT", "icon": "IconStethoscope"},
    {"name": "bhyt", "label": "Số BHYT", "type": "TEXT", "icon": "IconShieldCheck"},
    {"name": "nhomMau", "label": "Nhóm máu", "type": "SELECT", "icon": "IconDroplet",
     "options": [{"label": "A", "value": "A", "position": 0, "color": "red"},
                 {"label": "B", "value": "B", "position": 1, "color": "blue"},
                 {"label": "AB", "value": "AB", "position": 2, "color": "purple"},
                 {"label": "O", "value": "O", "position": 3, "color": "green"}]},
    {"name": "ngayDuSinh", "label": "Ngày dự sinh", "type": "DATE", "icon": "IconBabyCarriage"},
    {"name": "tuanThai", "label": "Tuần thai", "type": "NUMBER", "icon": "IconMoodKid"},
    {"name": "treatmentStage", "label": "Giai đoạn điều trị", "type": "SELECT", "icon": "IconProgress",
     "options": [{"label": "Tư vấn", "value": "TU_VAN", "position": 0, "color": "sky"},
                 {"label": "IVF", "value": "IVF", "position": 1, "color": "purple"},
                 {"label": "IUI", "value": "IUI", "position": 2, "color": "blue"},
                 {"label": "Thai kỳ", "value": "THAI_KY", "position": 3, "color": "green"},
                 {"label": "Hoàn thành", "value": "HOAN_THANH", "position": 4, "color": "turquoise"},
                 {"label": "Sảy thai", "value": "SAY_THAI", "position": 5, "color": "red"},
                 {"label": "Lưu thai", "value": "LUU_THAI", "position": 6, "color": "orange"}]},
]

TASK_FIELDS = [
    {"name": "appointmentType", "label": "Loại lịch hẹn", "type": "SELECT", "icon": "IconCalendarEvent",
     "options": [{"label": "Tái khám", "value": "TAI_KHAM", "position": 0, "color": "blue"},
                 {"label": "IUI", "value": "IUI", "position": 1, "color": "green"},
                 {"label": "Lấy trứng", "value": "LAY_TRUNG", "position": 2, "color": "orange"},
                 {"label": "Chuyển phôi", "value": "CHUYEN_PHOI", "position": 3, "color": "purple"},
                 {"label": "Phẫu thuật", "value": "PHAU_THUAT", "position": 4, "color": "red"},
                 {"label": "PRP", "value": "PRP", "position": 5, "color": "turquoise"},
                 {"label": "Sinh nhật", "value": "SINH_NHAT", "position": 6, "color": "yellow"}]},
    {"name": "appointmentTime", "label": "Giờ hẹn", "type": "TEXT", "icon": "IconClock"},
    {"name": "arrivalTime", "label": "Giờ có mặt", "type": "TEXT", "icon": "IconClockHour3"},
    {"name": "reminderDate", "label": "Ngày nhắc lịch", "type": "DATE_TIME", "icon": "IconBell"},
    {"name": "examCode", "label": "Mã khám", "type": "TEXT", "icon": "IconBarcode"},
    {"name": "doctorAdvice", "label": "Lời dặn BS", "type": "TEXT", "icon": "IconMessageDots"},
    {"name": "clinicRoom", "label": "Phòng khám", "type": "TEXT", "icon": "IconBuilding"},
    {"name": "careType", "label": "Loại chăm sóc", "type": "SELECT", "icon": "IconHeartHandshake",
     "options": [{"label": "Nội trú", "value": "NOI_TRU", "position": 0, "color": "blue"},
                 {"label": "CBNM", "value": "CBNM", "position": 1, "color": "green"},
                 {"label": "Thủ thuật", "value": "THU_THUAT", "position": 2, "color": "orange"},
                 {"label": "Tái khám", "value": "TAI_KHAM", "position": 3, "color": "purple"},
                 {"label": "Beta-thai", "value": "BETA_THAI", "position": 4, "color": "red"},
                 {"label": "Thai kỳ", "value": "THAI_KY", "position": 5, "color": "turquoise"}]},
    {"name": "callStatus", "label": "Trạng thái gọi", "type": "SELECT", "icon": "IconPhoneCall",
     "options": [{"label": "Chưa gọi", "value": "CHUA_GOI", "position": 0, "color": "sky"},
                 {"label": "Đã gọi", "value": "DA_GOI", "position": 1, "color": "green"},
                 {"label": "Cần gọi lại", "value": "CAN_GOI_LAI", "position": 2, "color": "orange"},
                 {"label": "Không liên lạc được", "value": "KHONG_LIEN_LAC", "position": 3, "color": "red"}]},
    {"name": "callNote", "label": "Ghi chú cuộc gọi", "type": "TEXT", "icon": "IconNote"},
    {"name": "medication", "label": "Thuốc", "type": "TEXT", "icon": "IconPill"},
    {"name": "doctorName", "label": "BS phụ trách", "type": "TEXT", "icon": "IconStethoscope"},
    {"name": "approvalStatus", "label": "Trạng thái duyệt", "type": "SELECT", "icon": "IconCheck",
     "options": [{"label": "Chưa duyệt", "value": "CHUA_DUYET", "position": 0, "color": "sky"},
                 {"label": "Đã duyệt", "value": "DA_DUYET", "position": 1, "color": "green"},
                 {"label": "Từ chối", "value": "TU_CHOI", "position": 2, "color": "red"}]},
]

# View definitions: (name, icon, type, filter_value, columns[(fieldName, size)])
CS_VIEWS = [
    ("CS nội trú", "IconBuildingHospital", "TABLE", "NOI_TRU",
     [("title", 220), ("taskTargets", 180), ("doctorName", 120), ("clinicRoom", 100), ("callStatus", 130), ("dueAt", 120), ("callNote", 200), ("medication", 150)]),
    ("CS CBNM", "IconStethoscope", "TABLE", "CBNM",
     [("title", 220), ("taskTargets", 180), ("doctorName", 120), ("medication", 150), ("callStatus", 130), ("callNote", 200)]),
    ("CS thủ thuật", "IconNeedle", "TABLE", "THU_THUAT",
     [("title", 220), ("taskTargets", 180), ("appointmentType", 120), ("dueAt", 120), ("callStatus", 130), ("callNote", 200)]),
    ("CS tái khám", "IconCalendar", "TABLE", "TAI_KHAM",
     [("title", 220), ("taskTargets", 180), ("doctorName", 120), ("medication", 150), ("callStatus", 130), ("callNote", 200), ("dueAt", 120)]),
    ("CS beta-thai", "IconHeartbeat", "TABLE", "BETA_THAI",
     [("title", 220), ("taskTargets", 180), ("appointmentType", 100), ("dueAt", 120), ("approvalStatus", 120), ("callStatus", 130), ("callNote", 200)]),
    ("CS thai kỳ", "IconMoodKid", "TABLE", "THAI_KY",
     [("title", 220), ("taskTargets", 180), ("dueAt", 120), ("medication", 130), ("callStatus", 130), ("callNote", 200)]),
    ("CS theo trạng thái", "IconLayoutKanban", "KANBAN", None, []),
]

# =============================================================================
# OBJECT RENAMES (Vietnamese labels)
# =============================================================================

OBJECT_RENAMES = {
    "company": ("Khoa", "Các Khoa"),
    "person": ("Bệnh nhân", "Bệnh nhân"),
    "task": ("Công việc CS", "Công việc CS"),
    "note": ("Ghi chú", "Ghi chú"),
    "dashboard": ("Báo cáo", "Báo cáo"),
    "workflow": ("Quy trình", "Quy trình"),
}

# =============================================================================
# CUSTOM OBJECTS
# =============================================================================

CUSTOM_OBJECTS = [
    {
        "nameSingular": "treatmentCycle",
        "namePlural": "treatmentCycles",
        "labelSingular": "Chu kỳ điều trị",
        "labelPlural": "Chu kỳ điều trị",
        "icon": "IconHeartbeat",
        "description": "Chu kỳ điều trị IUI/IVF/CBNM của bệnh nhân",
        "fields": [
            {"name": "cycleType", "label": "Loại chu kỳ", "type": "SELECT", "icon": "IconList",
             "options": [{"label": "IUI", "value": "IUI", "position": 0, "color": "blue"},
                         {"label": "IVF", "value": "IVF", "position": 1, "color": "purple"},
                         {"label": "CBNM", "value": "CBNM", "position": 2, "color": "green"},
                         {"label": "PRP", "value": "PRP", "position": 3, "color": "turquoise"}]},
            {"name": "status", "label": "Trạng thái", "type": "SELECT", "icon": "IconCircleCheck",
             "options": [{"label": "Đang điều trị", "value": "DANG_DIEU_TRI", "position": 0, "color": "blue"},
                         {"label": "Hoàn thành", "value": "HOAN_THANH", "position": 1, "color": "green"},
                         {"label": "Đã hủy", "value": "DA_HUY", "position": 2, "color": "red"}]},
            {"name": "doctor", "label": "Bác sĩ", "type": "TEXT", "icon": "IconStethoscope"},
            {"name": "startDate", "label": "Ngày bắt đầu", "type": "DATE", "icon": "IconCalendar"},
            {"name": "procedureDate", "label": "Ngày thủ thuật", "type": "DATE", "icon": "IconCalendar"},
            {"name": "betaTestDate", "label": "Ngày xét nghiệm Beta", "type": "DATE", "icon": "IconCalendar"},
            {"name": "betaResult", "label": "Kết quả Beta", "type": "TEXT", "icon": "IconHeartbeat"},
            {"name": "cancelReason", "label": "Lý do hủy", "type": "TEXT", "icon": "IconAlertTriangle"},
            {"name": "generalNotes", "label": "Ghi chú chung", "type": "TEXT", "icon": "IconNote"},
        ],
        "relation_to_person": {"targetFieldLabel": "Chu kỳ điều trị", "targetFieldIcon": "IconHeartbeat"},
    },
    {
        "nameSingular": "inpatientStay",
        "namePlural": "inpatientStays",
        "labelSingular": "Lần nhập viện",
        "labelPlural": "Lần nhập viện",
        "icon": "IconBuildingHospital",
        "description": "Lần nhập viện nội trú (HTSS, TT/PT, Phụ sản)",
        "fields": [
            {"name": "stayType", "label": "Loại nhập viện", "type": "SELECT", "icon": "IconList",
             "options": [{"label": "HTSS", "value": "HTSS", "position": 0, "color": "blue"},
                         {"label": "PT-TT", "value": "PT_TT", "position": 1, "color": "orange"},
                         {"label": "Sản", "value": "SAN", "position": 2, "color": "green"}]},
            {"name": "admissionDate", "label": "Ngày nhập viện", "type": "DATE", "icon": "IconCalendar"},
            {"name": "dischargeDate", "label": "Ngày xuất viện", "type": "DATE", "icon": "IconCalendar"},
            {"name": "procedureType", "label": "Loại thủ thuật", "type": "SELECT", "icon": "IconList",
             "options": [{"label": "OR (lấy trứng)", "value": "OR", "position": 0, "color": "blue"},
                         {"label": "ET (chuyển phôi)", "value": "ET", "position": 1, "color": "purple"},
                         {"label": "FET", "value": "FET", "position": 2, "color": "turquoise"},
                         {"label": "Mổ lấy thai", "value": "C_SECTION", "position": 3, "color": "red"},
                         {"label": "Khác", "value": "KHAC", "position": 4, "color": "sky"}]},
            {"name": "doctor", "label": "Bác sĩ", "type": "TEXT", "icon": "IconStethoscope"},
            {"name": "room", "label": "Phòng", "type": "TEXT", "icon": "IconBuilding"},
            {"name": "satisfaction", "label": "Hài lòng", "type": "SELECT", "icon": "IconMoodSmile",
             "options": [{"label": "Hài lòng", "value": "HAI_LONG", "position": 0, "color": "green"},
                         {"label": "Tiêu cực", "value": "TIEU_CUC", "position": 1, "color": "red"},
                         {"label": "Chưa khảo sát", "value": "CHUA_KHAO_SAT", "position": 2, "color": "sky"}]},
            {"name": "generalNotes", "label": "Ghi chú chung", "type": "TEXT", "icon": "IconNote"},
        ],
        "relation_to_person": {"targetFieldLabel": "Lần nhập viện", "targetFieldIcon": "IconBuildingHospital"},
    },
]

# =============================================================================
# BVHM HOSPITAL DEPARTMENTS (Base data — always seeded)
# =============================================================================

BVHM_COMPANIES = [
    {"name": "Khoa HTSS", "domainName": {"primaryLinkUrl": "https://benhvienhiemmuonsaigon.vn/khoa-htss"}, "employees": 30,
     "address": {"addressStreet1": "87 Ly Chieu Hoang", "addressCity": "TP Ho Chi Minh", "addressState": "Phuong Binh Phu", "addressCountry": "Viet Nam"}},
    {"name": "Khoa Phu san", "domainName": {"primaryLinkUrl": "https://benhvienhiemmuonsaigon.vn/khoa-phu-san"}, "employees": 20,
     "address": {"addressStreet1": "87 Ly Chieu Hoang", "addressCity": "TP Ho Chi Minh", "addressState": "Phuong Binh Phu", "addressCountry": "Viet Nam"}},
    {"name": "Khoa Nam khoa", "domainName": {"primaryLinkUrl": "https://benhvienhiemmuonsaigon.vn/khoa-nam-khoa"}, "employees": 10,
     "address": {"addressStreet1": "87 Ly Chieu Hoang", "addressCity": "TP Ho Chi Minh", "addressState": "Phuong Binh Phu", "addressCountry": "Viet Nam"}},
    {"name": "Phong kham hanh chinh", "domainName": {"primaryLinkUrl": "https://benhvienhiemmuonsaigon.vn/pk-hanh-chinh"}, "employees": 15,
     "address": {"addressStreet1": "87 Ly Chieu Hoang", "addressCity": "TP Ho Chi Minh", "addressState": "Phuong Binh Phu", "addressCountry": "Viet Nam"}},
    {"name": "PK BS Ho Cao Cuong", "domainName": {"primaryLinkUrl": "https://benhvienhiemmuonsaigon.vn/pk-ho-cao-cuong"}, "employees": 5,
     "address": {"addressStreet1": "87 Ly Chieu Hoang", "addressCity": "TP Ho Chi Minh", "addressState": "Phuong Binh Phu", "addressCountry": "Viet Nam"}},
    {"name": "PK BS Ly Thai Loc", "domainName": {"primaryLinkUrl": "https://benhvienhiemmuonsaigon.vn/pk-ly-thai-loc"}, "employees": 5,
     "address": {"addressStreet1": "87 Ly Chieu Hoang", "addressCity": "TP Ho Chi Minh", "addressState": "Phuong Binh Phu", "addressCountry": "Viet Nam"}},
    {"name": "PK BS Le Huy Binh", "domainName": {"primaryLinkUrl": "https://benhvienhiemmuonsaigon.vn/pk-le-huy-binh"}, "employees": 5,
     "address": {"addressStreet1": "87 Ly Chieu Hoang", "addressCity": "TP Ho Chi Minh", "addressState": "Phuong Binh Phu", "addressCountry": "Viet Nam"}},
    {"name": "PK BS Minh Tam", "domainName": {"primaryLinkUrl": "https://benhvienhiemmuonsaigon.vn/pk-minh-tam"}, "employees": 5,
     "address": {"addressStreet1": "87 Ly Chieu Hoang", "addressCity": "TP Ho Chi Minh", "addressState": "Phuong Binh Phu", "addressCountry": "Viet Nam"}},
    {"name": "PK BS Vu Minh Ngoc", "domainName": {"primaryLinkUrl": "https://benhvienhiemmuonsaigon.vn/pk-vu-minh-ngoc"}, "employees": 5,
     "address": {"addressStreet1": "87 Ly Chieu Hoang", "addressCity": "TP Ho Chi Minh", "addressState": "Phuong Binh Phu", "addressCountry": "Viet Nam"}},
    {"name": "PK BS Nam Khoa", "domainName": {"primaryLinkUrl": "https://benhvienhiemmuonsaigon.vn/pk-nam-khoa"}, "employees": 3,
     "address": {"addressStreet1": "87 Ly Chieu Hoang", "addressCity": "TP Ho Chi Minh", "addressState": "Phuong Binh Phu", "addressCountry": "Viet Nam"}},
    {"name": "PK BS Nhan Quoc Thu", "domainName": {"primaryLinkUrl": "https://benhvienhiemmuonsaigon.vn/pk-nhan-quoc-thu"}, "employees": 5,
     "address": {"addressStreet1": "87 Ly Chieu Hoang", "addressCity": "TP Ho Chi Minh", "addressState": "Phuong Binh Phu", "addressCountry": "Viet Nam"}},
]

# =============================================================================
# DEMO DATA (only seeded with --level demo)
# =============================================================================

# =============================================================================
# DEMO DATA GENERATOR — 3 months of realistic hospital operation
# =============================================================================
import random

_FIRST_NAMES_F = ["Lan", "Hoa", "Mai", "Hồng", "Ngọc", "Yến", "Thanh", "Thảo", "Linh", "Trang",
                  "Hạnh", "Phương", "Vy", "Trâm", "Uyên", "Diệu", "Châu", "Nhung", "Ánh", "Tuyết",
                  "Huệ", "Cúc", "Thu", "Xuân", "Hiền", "Bích", "Dung", "Quỳnh", "Nga", "Vân"]
_FIRST_NAMES_M = ["Minh", "Hùng", "Tuấn", "Đức", "Long", "Nam", "Bình", "Phong", "Khoa", "Thắng"]
_LAST_NAMES = ["Nguyễn Thị", "Trần Thị", "Lê Thị", "Phạm Thị", "Hoàng Thị", "Võ Thị", "Đặng Thị",
               "Bùi Thị", "Đỗ Thị", "Ngô Thị", "Nguyễn Văn", "Trần Văn", "Lê Văn", "Phạm Văn"]
_CITIES = ["TP Hồ Chí Minh", "Bình Dương", "Đồng Nai", "Long An", "Tây Ninh", "Bà Rịa - Vũng Tàu", "Cần Thơ"]
_DOCTORS = ["BS Hồ Cao Cường", "BS Lý Thái Lộc", "BS Lê Huy Bình", "BS Minh Tâm",
            "BS Vũ Minh Ngọc", "BS Nam Khoa", "BS Nhân Quốc Thư"]
_COMPANIES = ["Khoa HTSS", "Khoa Phu san", "Khoa Nam khoa", "PK BS Ho Cao Cuong",
              "PK BS Ly Thai Loc", "PK BS Le Huy Binh", "PK BS Minh Tam"]
_CARE_TYPES = ["NOI_TRU", "CBNM", "THU_THUAT", "TAI_KHAM", "BETA_THAI", "THAI_KY"]
_CALL_STATUSES = ["CHUA_GOI", "DA_GOI", "DA_GOI", "DA_GOI", "CAN_GOI_LAI", "KHONG_LIEN_LAC"]  # weighted: 70% đã gọi for past tasks
_MEDICATIONS = [None, None, "Progesterone 400mg x2/ngày", "Clomiphene 50mg", "Acid folic 5mg/ngày",
                "Ovitrelle 250mcg", "Duphaston 10mg x2/ngày", "Estradiol 2mg x3/ngày"]
_CYCLE_TYPES = ["IVF", "IVF", "IUI", "IUI", "IUI", "CBNM", "PRP"]  # weighted
_STAY_TYPES = ["HTSS", "HTSS", "HTSS", "PT_TT", "SAN"]
_PROCEDURE_TYPES = ["OR", "ET", "FET", "C_SECTION", "KHAC"]
_STAGES = ["TU_VAN", "IVF", "IVF", "IUI", "IUI", "THAI_KY", "THAI_KY", "HOAN_THANH", "SAY_THAI", None]
_BLOOD_TYPES = ["A", "B", "AB", "O", None, None]
_TASK_TITLES = {
    "NOI_TRU": ["CS nội trú - {name} - xuất viện sau {proc}", "CS nội trú - {name} - theo dõi sau mổ"],
    "CBNM": ["CS CBNM - {name} - bệnh nhân mới", "CS CBNM - {name} - tư vấn điều trị"],
    "THU_THUAT": ["Nhắc hẹn thủ thuật - {name} - {proc} ngày mai", "CS thủ thuật - {name} - chuẩn bị {proc}"],
    "TAI_KHAM": ["Gọi tái khám - {name} - PK {doctor}", "Nhắc lịch tái khám - {name}"],
    "BETA_THAI": ["CS beta - {name} - {days} ngày sau {proc}", "Theo dõi beta - {name}"],
    "THAI_KY": ["CS thai kỳ - {name} - Tuần {week}", "Theo dõi thai - {name} - tháng {month}"],
}
_NOTE_TEMPLATES = [
    ("{name} - Kết quả siêu âm", "Siêu âm ngày {date}: Nội mạc tử cung {r}mm, nang noãn {r2}mm. {action}"),
    ("{name} - Tư vấn điều trị", "BN được tư vấn quy trình {proc}. Lịch hẹn: xét nghiệm hormone, siêu âm theo dõi."),
    ("{name} - Kết quả xét nghiệm", "Kết quả XN hormone: FSH {r} mIU/mL, AMH {r2} ng/mL. Chỉ định: {action}"),
    ("{name} - Ghi chú xuất viện", "BN xuất viện ngày {date}. Dặn dò: tái khám sau 1 tuần, uống thuốc đều."),
    ("{name} - Theo dõi thai kỳ", "Siêu âm thai tuần {week}: Thai phát triển bình thường, cân nặng ước tính {r}g."),
]


def _rand_phone():
    return f"9{random.randint(10000000, 99999999)}"


def _date_str(d):
    return d.strftime("%Y-%m-%d")


def generate_demo_data():
    """Generate 3 months of realistic hospital data."""
    random.seed(42)  # reproducible
    today = datetime.utcnow().date()
    start = today - timedelta(days=90)

    # --- 50 patients ---
    patients = []
    for i in range(50):
        is_female = i < 40  # 80% nữ (bệnh viện HTSS)
        first = random.choice(_FIRST_NAMES_F if is_female else _FIRST_NAMES_M)
        last = random.choice([ln for ln in _LAST_NAMES if ("Thị" in ln) == is_female])
        email = f"{first.lower()}.{last.lower().replace(' ', '')}.{i}@example.com"
        stage = random.choice(_STAGES)
        blood = random.choice(_BLOOD_TYPES)
        p_data = {
            "name": {"firstName": first, "lastName": last},
            "emails": {"primaryEmail": email},
            "phones": {"primaryPhoneNumber": _rand_phone(), "primaryPhoneCountryCode": "VN", "primaryPhoneCallingCode": "+84"},
            "city": random.choice(_CITIES),
            "jobTitle": random.choice(["IVF", "IUI", "Tư vấn", "Mang thai", "Tái khám", "Khám phụ khoa"]),
            "companyName": random.choice(_COMPANIES),
            "treatmentStage": stage,
            "_email": email,
        }
        if blood:
            p_data["nhomMau"] = blood
        if is_female and random.random() < 0.3:
            p_data["bhyt"] = f"HS4{random.randint(10000000, 99999999)}"
        if stage == "THAI_KY":
            p_data["tuanThai"] = random.randint(6, 36)
            due = today + timedelta(days=random.randint(30, 200))
            p_data["ngayDuSinh"] = _date_str(due)
        patients.append(p_data)

    # --- 250 tasks (spread over 90 days, ~3/day recent, more past) ---
    tasks = []
    for day_offset in range(-90, 5):
        d = today + timedelta(days=day_offset)
        # More tasks per day for recent weeks
        n_tasks = random.randint(2, 5) if day_offset > -30 else random.randint(1, 3)
        for _ in range(n_tasks):
            p = random.choice(patients)
            care = random.choice(_CARE_TYPES)
            # Past tasks mostly "đã gọi", future/recent tasks "chưa gọi"
            if day_offset < -7:
                status = random.choice(["DA_GOI", "DA_GOI", "DA_GOI", "KHONG_LIEN_LAC"])
            elif day_offset < 0:
                status = random.choice(["DA_GOI", "DA_GOI", "CAN_GOI_LAI", "CHUA_GOI"])
            else:
                status = random.choice(["CHUA_GOI", "CHUA_GOI", "CHUA_GOI", "DA_GOI"])
            name = p["name"]["firstName"]
            title_tpl = random.choice(_TASK_TITLES[care])
            title = title_tpl.format(name=name, proc=random.choice(["ET", "OR", "IUI", "FET"]),
                                     doctor=random.choice(_DOCTORS).replace("BS ", ""),
                                     days=random.randint(7, 21), week=random.randint(8, 36),
                                     month=random.randint(1, 9))
            task = {
                "title": title, "careType": care, "callStatus": status,
                "medication": random.choice(_MEDICATIONS),
                "daysFromNow": day_offset, "patientEmail": p["_email"],
            }
            if status in ("CAN_GOI_LAI", "KHONG_LIEN_LAC"):
                task["callNote"] = random.choice(["Gọi 3 lần không nghe máy", "BN bận, hẹn gọi lại chiều",
                                                   "SĐT sai, cần xác nhận lại", "Gọi lại sau 14h"])
            tasks.append(task)

    # --- 60 notes ---
    notes = []
    for i in range(60):
        p = random.choice(patients)
        tpl = random.choice(_NOTE_TEMPLATES)
        d = start + timedelta(days=random.randint(0, 90))
        title = tpl[0].format(name=p["name"]["firstName"])
        body = tpl[1].format(name=p["name"]["firstName"], date=_date_str(d),
                             r=random.randint(5, 20), r2=random.randint(8, 25),
                             action=random.choice(["Tiếp tục theo dõi", "Chỉ định IUI", "Chuyển IVF",
                                                    "Hẹn tái khám 2 tuần", "Siêu âm lại sau 1 tuần"]),
                             proc=random.choice(["IUI", "IVF", "FET"]),
                             week=random.randint(8, 36))
        notes.append({"title": title, "body": body, "patientEmail": p["_email"]})

    # --- 35 treatment cycles ---
    cycles = []
    for i in range(35):
        p = random.choice(patients)
        d = start + timedelta(days=random.randint(0, 80))
        ct = random.choice(_CYCLE_TYPES)
        s = random.choice(["DANG_DIEU_TRI", "DANG_DIEU_TRI", "HOAN_THANH", "DA_HUY"])
        cycle = {
            "cycleType": ct, "status": s, "doctor": random.choice(_DOCTORS),
            "startDate": _date_str(d), "patientEmail": p["_email"],
        }
        if ct in ("IVF", "IUI") and s != "DA_HUY":
            cycle["procedureDate"] = _date_str(d + timedelta(days=random.randint(14, 30)))
        if s == "HOAN_THANH":
            cycle["betaResult"] = f"hCG {random.randint(200, 2500)} mIU/mL - {'Dương tính' if random.random() > 0.3 else 'Âm tính'}"
        if s == "DA_HUY":
            cycle["cancelReason"] = random.choice(["Nang noãn không đáp ứng", "BN xin hoãn", "Chỉ số hormone không đạt"])
        cycles.append(cycle)

    # --- 25 inpatient stays ---
    stays = []
    for i in range(25):
        p = random.choice(patients)
        d = start + timedelta(days=random.randint(0, 85))
        stay = {
            "stayType": random.choice(_STAY_TYPES),
            "admissionDate": _date_str(d),
            "dischargeDate": _date_str(d + timedelta(days=random.randint(1, 3))),
            "procedureType": random.choice(_PROCEDURE_TYPES),
            "doctor": random.choice(_DOCTORS),
            "room": str(random.randint(101, 310)),
            "satisfaction": random.choice(["HAI_LONG", "HAI_LONG", "HAI_LONG", "TIEU_CUC", "CHUA_KHAO_SAT"]),
            "patientEmail": p["_email"],
        }
        stays.append(stay)

    return patients, tasks, notes, cycles, stays

# Navigation items to remove (by view name pattern)
NAV_ITEMS_TO_REMOVE = ["Opportunities", "Workflow Runs", "Workflow Versions"]


# =============================================================================
# API CLIENT
# =============================================================================

class TwentyAPI:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")
        self.client = httpx.Client(timeout=60)
        self.token = None

    # -- Auth --

    def signup_and_activate(self, email: str, password: str, workspace_name: str = "BVHM"):
        """Sign up a new user and activate the workspace."""
        print(f"   Signing up {email}...")
        r = self._gql_unauth(
            'mutation($email: String!, $password: String!) { signUpWithPassword(email: $email, password: $password) '
            '{ tokens { accessToken { token } } } }',
            {"email": email, "password": password},
        )
        self.token = r["data"]["signUpWithPassword"]["tokens"]["accessToken"]["token"]

        print(f"   Activating workspace '{workspace_name}'...")
        self._gql(
            'mutation($name: String!) { activateWorkspace(data: { displayName: $name }) { id } }',
            {"name": workspace_name},
        )

    def login(self, email: str, password: str):
        """Two-step auth: getLoginToken -> getAuthTokens. Account must exist."""
        origin = self.base_url
        r = self._gql_unauth(
            'mutation($email: String!, $password: String!, $origin: String!) '
            '{ getLoginTokenFromCredentials(email: $email, password: $password, origin: $origin) '
            '{ loginToken { token } } }',
            {"email": email, "password": password, "origin": origin},
        )
        login_token = r["data"]["getLoginTokenFromCredentials"]["loginToken"]["token"]

        r = self._gql_unauth(
            'mutation($loginToken: String!, $origin: String!) '
            '{ getAuthTokensFromLoginToken(loginToken: $loginToken, origin: $origin) '
            '{ tokens { accessOrWorkspaceAgnosticToken { token } } } }',
            {"loginToken": login_token, "origin": origin},
        )
        self.token = r["data"]["getAuthTokensFromLoginToken"]["tokens"]["accessOrWorkspaceAgnosticToken"]["token"]

    def ensure_auth(self, email: str, password: str):
        """Login to existing workspace. Account must be created via UI first."""
        self.login(email, password)
        print("   Logged in OK")

    # -- Low-level --

    def _headers(self, auth: bool = True):
        h = {"Content-Type": "application/json"}
        if auth and self.token:
            h["Authorization"] = f"Bearer {self.token}"
        return h

    def _gql_unauth(self, query: str, variables: dict = None):
        body = {"query": query}
        if variables:
            body["variables"] = variables
        r = self.client.post(f"{self.base_url}/metadata", json=body, headers=self._headers(auth=False))
        data = r.json()
        if "errors" in data and data.get("data") is None:
            raise Exception(data["errors"][0].get("message", str(data["errors"])))
        return data

    def _gql(self, query: str, variables: dict = None):
        body = {"query": query}
        if variables:
            body["variables"] = variables
        r = self.client.post(f"{self.base_url}/metadata", json=body, headers=self._headers())
        data = r.json()
        if "errors" in data and data.get("data") is None:
            raise Exception(data["errors"][0].get("message", str(data["errors"])))
        return data

    def _core_gql(self, query: str, variables: dict = None):
        body = {"query": query}
        if variables:
            body["variables"] = variables
        r = self.client.post(f"{self.base_url}/graphql", json=body, headers=self._headers())
        data = r.json()
        if "errors" in data and data.get("data") is None:
            raise Exception(data["errors"][0].get("message", str(data["errors"])))
        return data

    def rest(self, method: str, path: str, data: dict = None) -> dict:
        url = f"{self.base_url}/rest/{path}"
        r = self.client.request(method, url, json=data, headers=self._headers())
        if r.status_code >= 400:
            raise Exception(f"REST {method} {path} -> {r.status_code}: {r.text[:200]}")
        return r.json() if r.text else {}

    # -- Metadata helpers --

    def get_object_id(self, name: str) -> str:
        r = self._gql('query { objects(paging: { first: 100 }) { edges { node { id nameSingular } } } }')
        for edge in r["data"]["objects"]["edges"]:
            if edge["node"]["nameSingular"] == name:
                return edge["node"]["id"]
        raise Exception(f"Object '{name}' not found")

    def get_fields(self, object_id: str) -> dict[str, str]:
        r = self._gql(f'query {{ object(id: "{object_id}") {{ fields(paging: {{ first: 200 }}) {{ edges {{ node {{ id name }} }} }} }} }}')
        return {e["node"]["name"]: e["node"]["id"] for e in r["data"]["object"]["fields"]["edges"]}

    def create_field(self, object_id: str, field: dict) -> str | None:
        field_input = {
            "objectMetadataId": object_id,
            "name": field["name"],
            "label": field["label"],
            "type": field["type"],
            "icon": field.get("icon", "IconList"),
            "isNullable": True,
            "isLabelSyncedWithName": False,
        }
        if "options" in field:
            field_input["options"] = field["options"]
        if "description" in field:
            field_input["description"] = field["description"]
        try:
            r = self._gql(
                "mutation CreateField($input: CreateOneFieldMetadataInput!) { createOneField(input: $input) { id name } }",
                {"input": {"field": field_input}},
            )
            return r["data"]["createOneField"]["id"]
        except Exception as e:
            if "already exists" in str(e).lower() or "duplicate" in str(e).lower():
                return None
            raise

    def deactivate_object(self, object_id: str):
        self._gql(f'mutation {{ updateOneObject(input: {{ id: "{object_id}", update: {{ isActive: false }} }}) {{ id }} }}')

    def create_view(self, object_id: str, name: str, icon: str, vtype: str = "TABLE", group_by_field_id: str = None) -> str | None:
        extra = ""
        if group_by_field_id:
            extra = f', mainGroupByFieldMetadataId: "{group_by_field_id}"'
        try:
            r = self._gql(f'mutation {{ createView(input: {{ name: "{name}", objectMetadataId: "{object_id}", type: {vtype}, icon: "{icon}"{extra} }}) {{ id }} }}')
            return r["data"]["createView"]["id"]
        except Exception as e:
            if "already exists" in str(e).lower():
                return None
            raise

    def create_view_filter(self, view_id: str, field_id: str, value: str):
        self._gql(
            "mutation($input: CreateViewFilterInput!) { createViewFilter(input: $input) { id } }",
            {"input": {"viewId": view_id, "fieldMetadataId": field_id, "operand": "IS", "value": value}},
        )

    def create_view_field(self, view_id: str, field_id: str, position: int, size: int):
        self._gql(
            "mutation($input: CreateViewFieldInput!) { createViewField(input: $input) { id } }",
            {"input": {"viewId": view_id, "fieldMetadataId": field_id, "position": position, "size": size, "isVisible": True}},
        )

    def get_nav_items(self) -> list[dict]:
        r = self._gql('query { navigationMenuItems { id name type targetObjectMetadataId } }')
        return r["data"]["navigationMenuItems"]

    def get_object_name_map(self) -> dict[str, str]:
        """Returns {objectMetadataId: nameSingular} including inactive objects."""
        r = self._gql('query { objects(paging: { first: 100 }) { edges { node { id nameSingular } } } }')
        return {e["node"]["id"]: e["node"]["nameSingular"] for e in r["data"]["objects"]["edges"]}

    def delete_nav_item(self, item_id: str):
        self._gql(f'mutation {{ deleteNavigationMenuItem(id: "{item_id}") {{ id }} }}')


# =============================================================================
# SETUP FUNCTIONS
# =============================================================================

def cleanup_defaults(api: TwentyAPI):
    """Delete ALL existing companies, people, opportunities, tasks, notes."""
    print("\n2. Cleaning up all existing data...")

    for obj_name in ("taskTargets", "noteTargets", "tasks", "notes", "treatmentCycles", "inpatientStays", "opportunities", "people", "companies"):
        total = 0
        while True:
            try:
                resp = api.rest("GET", f"{obj_name}?limit=60")
                records = resp.get("data", {}).get(obj_name, [])
                if not records:
                    break
                for r in records:
                    try:
                        api.rest("DELETE", f"{obj_name}/{r['id']}")
                        total += 1
                    except Exception:
                        pass
                if len(records) < 60:
                    break
            except Exception:
                break
        if total:
            print(f"   Deleted {total} {obj_name}")
        else:
            print(f"   No {obj_name} to delete")


def deactivate_opportunity(api: TwentyAPI):
    """Deactivate the Opportunity object."""
    print("\n3. Deactivating Opportunities...")
    try:
        opp_id = api.get_object_id("opportunity")
        api.deactivate_object(opp_id)
        print("   OK")
    except Exception as e:
        print(f"   Skip: {e}")


def cleanup_navigation(api: TwentyAPI):
    """Remove unwanted navigation menu items."""
    print("\n4. Cleaning up navigation...")
    hide_objects = {"opportunity", "workflowRun", "workflowVersion"}
    removed = 0
    try:
        obj_map = api.get_object_name_map()
        items = api.get_nav_items()
        for item in items:
            obj_name = obj_map.get(item.get("targetObjectMetadataId"), "")
            if obj_name in hide_objects:
                try:
                    api.delete_nav_item(item["id"])
                    removed += 1
                    print(f"   Removed: {obj_name}")
                except Exception as e:
                    print(f"   Failed to remove {obj_name}: {e}")
    except Exception as e:
        print(f"   Navigation cleanup: {e}")
    if not removed:
        print("   No items to remove")


def cleanup_workflows(api: TwentyAPI):
    """Delete default Quick Lead workflow."""
    print("\n4b. Removing default workflows...")
    try:
        resp = api.rest("GET", "workflows?limit=20")
        workflows = resp.get("data", {}).get("workflows", [])
        for wf in workflows:
            if wf.get("name") == "Quick Lead":
                api.rest("DELETE", f"workflows/{wf['id']}")
                print(f"   Removed: Quick Lead")
                return
        print("   No Quick Lead workflow found")
    except Exception as e:
        print(f"   Workflow cleanup: {e}")


def rename_objects(api: TwentyAPI):
    """Rename standard objects to Vietnamese labels."""
    print("\n4c. Renaming objects to Vietnamese...")
    for obj_name, (label_s, label_p) in OBJECT_RENAMES.items():
        try:
            obj_id = api.get_object_id(obj_name)
            api._gql(
                'mutation($input: UpdateOneObjectInput!) { updateOneObject(input: $input) { id } }',
                {"input": {"id": obj_id, "update": {"labelSingular": label_s, "labelPlural": label_p}}},
            )
            print(f"   {obj_name} → {label_s}")
        except Exception as e:
            print(f"   {obj_name}: {e}")


def create_custom_objects(api: TwentyAPI):
    """Create Treatment Cycle and Inpatient Stay custom objects with fields and relations."""
    print(f"\n5b. Creating custom objects ({len(CUSTOM_OBJECTS)})...")
    person_id = api.get_object_id("person")

    for obj_def in CUSTOM_OBJECTS:
        # Create object
        try:
            r = api._gql(
                'mutation($input: CreateOneObjectInput!) { createOneObject(input: $input) { id nameSingular } }',
                {"input": {"object": {
                    "nameSingular": obj_def["nameSingular"],
                    "namePlural": obj_def["namePlural"],
                    "labelSingular": obj_def["labelSingular"],
                    "labelPlural": obj_def["labelPlural"],
                    "icon": obj_def.get("icon", "IconList"),
                    "description": obj_def.get("description", ""),
                }}},
            )
            obj_id = r["data"]["createOneObject"]["id"]
            print(f"   Created: {obj_def['labelSingular']} ({obj_id[:12]}..)")
        except Exception as e:
            err = str(e).lower()
            if "already exists" in err or "duplicate" in err or "validation error" in err:
                try:
                    obj_id = api.get_object_id(obj_def["nameSingular"])
                    print(f"   Exists: {obj_def['labelSingular']}")
                except Exception:
                    print(f"   FAIL creating {obj_def['labelSingular']}: {e}")
                    continue
            else:
                print(f"   FAIL creating {obj_def['labelSingular']}: {e}")
                continue

        # Create fields
        existing = api.get_fields(obj_id)
        created = 0
        for f in obj_def.get("fields", []):
            if f["name"] not in existing:
                if api.create_field(obj_id, f):
                    created += 1
        if created:
            print(f"      + {created} fields")

        # Create relation to Person
        rel = obj_def.get("relation_to_person")
        if rel:
            existing = api.get_fields(obj_id)
            if "person" not in existing:
                try:
                    api._gql(
                        'mutation($input: CreateOneFieldMetadataInput!) { createOneField(input: $input) { id } }',
                        {"input": {"field": {
                            "name": "person",
                            "label": "Bệnh nhân",
                            "type": "RELATION",
                            "objectMetadataId": obj_id,
                            "icon": "IconUser",
                            "relationCreationPayload": {
                                "type": "MANY_TO_ONE",
                                "targetObjectMetadataId": person_id,
                                "targetFieldLabel": rel["targetFieldLabel"],
                                "targetFieldIcon": rel["targetFieldIcon"],
                            },
                        }}},
                    )
                    print(f"      + relation → Bệnh nhân")
                except Exception as e:
                    if "already exists" not in str(e).lower():
                        print(f"      Relation fail: {e}")


def create_workflows(api: TwentyAPI):
    """Create BVHM draft workflows."""
    print("\n8b. Creating BVHM workflows...")
    workflow_defs = [
        ("Thai kỳ Auto-Create", "Tự tạo task CS thai kỳ khi BN chuyển giai đoạn"),
        ("Thai kỳ Recurring", "Tự tạo task mới khi hoàn thành gọi CS thai kỳ"),
        ("Cảnh báo task quá hạn", "Tìm task quá hạn chưa xử lý mỗi ngày"),
    ]

    try:
        existing = api.rest("GET", "workflows?limit=20")
        existing_names = {wf["name"] for wf in existing.get("data", {}).get("workflows", [])}
    except Exception:
        existing_names = set()

    for name, desc in workflow_defs:
        if name in existing_names:
            print(f"   Exists: {name}")
            continue
        try:
            api.rest("POST", "workflows", {"name": name})
            print(f"   Created (draft): {name}")
        except Exception as e:
            print(f"   FAIL: {name} — {e}")


def create_custom_fields(api: TwentyAPI):
    """Create custom fields on Person and Task objects."""
    print(f"\n5. Creating Person fields ({len(PERSON_FIELDS)})...")
    person_id = api.get_object_id("person")
    existing = api.get_fields(person_id)
    created = sum(1 for f in PERSON_FIELDS if f["name"] not in existing and api.create_field(person_id, f))
    print(f"   Created {created}, skipped {len(PERSON_FIELDS) - created}")

    print(f"\n6. Creating Task fields ({len(TASK_FIELDS)})...")
    task_id = api.get_object_id("task")
    existing = api.get_fields(task_id)
    created = sum(1 for f in TASK_FIELDS if f["name"] not in existing and api.create_field(task_id, f))
    print(f"   Created {created}, skipped {len(TASK_FIELDS) - created}")


def create_views(api: TwentyAPI):
    """Create the 7 CS views with filters and columns."""
    print(f"\n7. Creating CS views ({len(CS_VIEWS)})...")
    task_id = api.get_object_id("task")
    task_fields = api.get_fields(task_id)

    for name, icon, vtype, filter_val, columns in CS_VIEWS:
        group_by = task_fields.get("callStatus") if vtype == "KANBAN" else None

        try:
            vid = api.create_view(task_id, name, icon, vtype, group_by)
        except Exception as e:
            print(f"   FAIL: {name} - {e}")
            continue

        if not vid:
            print(f"   SKIP: {name} (exists)")
            continue

        print(f"   OK: {name}")

        if filter_val and "careType" in task_fields:
            try:
                api.create_view_filter(vid, task_fields["careType"], f'["{filter_val}"]')
            except Exception as e:
                print(f"      Filter fail: {e}")

        for pos, (field_name, size) in enumerate(columns):
            fid = task_fields.get(field_name)
            if fid:
                try:
                    api.create_view_field(vid, fid, pos, size)
                except Exception as e:
                    print(f"      Column {field_name} fail: {e}")


def seed_companies(api: TwentyAPI):
    """Seed BVHM hospital departments."""
    print(f"\n8. Seeding BVHM departments ({len(BVHM_COMPANIES)})...")
    created = 0
    for company in BVHM_COMPANIES:
        try:
            api.rest("POST", "companies", company)
            created += 1
        except Exception as e:
            if "duplicate" in str(e).lower() or "already" in str(e).lower():
                continue
            print(f"   FAIL: {company['name']} - {e}")
    print(f"   Created {created} departments")


def seed_demo_data(api: TwentyAPI):
    """Seed 3 months of realistic hospital demo data."""
    patients, tasks_data, notes_data, cycles_data, stays_data = generate_demo_data()

    # Build company name -> id map
    companies_resp = api.rest("GET", "companies?limit=50")
    company_map = {c["name"]: c["id"] for c in companies_resp.get("data", {}).get("companies", [])}

    # --- Patients ---
    print(f"\n9. Seeding {len(patients)} demo patients...")
    patient_map = {}
    for p in patients:
        data = {"name": p["name"], "emails": p["emails"], "phones": p["phones"],
                "city": p["city"], "jobTitle": p["jobTitle"]}
        cid = company_map.get(p["companyName"])
        if cid:
            data["companyId"] = cid
        for extra in ("treatmentStage", "nhomMau", "bhyt", "tuanThai", "ngayDuSinh"):
            if p.get(extra):
                data[extra] = p[extra]
        try:
            result = api.rest("POST", "people", data)
            pid = result.get("data", {}).get("createPerson", {}).get("id") or result.get("id")
            if pid:
                patient_map[p["_email"]] = pid
        except Exception:
            pass
    print(f"   Created {len(patient_map)} patients")

    # --- Tasks ---
    print(f"\n10. Seeding {len(tasks_data)} demo tasks...")
    now = datetime.utcnow()
    task_ids = []
    for t in tasks_data:
        due = now + timedelta(days=t["daysFromNow"])
        data = {"title": t["title"], "status": "TODO", "dueAt": due.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "careType": t["careType"], "callStatus": t["callStatus"]}
        if t.get("callNote"):
            data["callNote"] = t["callNote"]
        if t.get("medication"):
            data["medication"] = t["medication"]
        try:
            result = api.rest("POST", "tasks", data)
            tid = result.get("data", {}).get("createTask", {}).get("id") or result.get("id")
            if tid:
                task_ids.append((tid, t.get("patientEmail")))
        except Exception:
            pass
    print(f"   Created {len(task_ids)} tasks")

    # --- Link tasks ---
    print(f"\n11. Linking tasks to patients...")
    linked = sum(1 for tid, email in task_ids if email in patient_map and
                 _try_link(api, "taskTargets", {"taskId": tid, "targetPersonId": patient_map[email]}))
    print(f"   Linked {linked}/{len(task_ids)}")

    # --- Notes ---
    print(f"\n12. Seeding {len(notes_data)} demo notes...")
    note_ids = []
    for n in notes_data:
        try:
            result = api.rest("POST", "notes", {"title": n["title"], "bodyV2": {"markdown": n["body"]}})
            nid = result.get("data", {}).get("createNote", {}).get("id") or result.get("id")
            if nid:
                note_ids.append((nid, n["patientEmail"]))
        except Exception:
            pass
    print(f"   Created {len(note_ids)} notes")

    # --- Link notes ---
    print(f"\n13. Linking notes to patients...")
    linked = sum(1 for nid, email in note_ids if email in patient_map and
                 _try_link(api, "noteTargets", {"noteId": nid, "targetPersonId": patient_map[email]}))
    print(f"   Linked {linked}/{len(note_ids)}")

    # --- Treatment cycles ---
    print(f"\n14. Seeding {len(cycles_data)} treatment cycles...")
    created = 0
    for tc in cycles_data:
        pid = patient_map.get(tc["patientEmail"])
        data = {k: v for k, v in tc.items() if k != "patientEmail" and v is not None}
        if pid:
            data["personId"] = pid
        try:
            api.rest("POST", "treatmentCycles", data)
            created += 1
        except Exception:
            pass
    print(f"   Created {created} treatment cycles")

    # --- Inpatient stays ---
    print(f"\n15. Seeding {len(stays_data)} inpatient stays...")
    created = 0
    for stay in stays_data:
        pid = patient_map.get(stay["patientEmail"])
        data = {k: v for k, v in stay.items() if k != "patientEmail" and v is not None}
        if pid:
            data["personId"] = pid
        try:
            api.rest("POST", "inpatientStays", data)
            created += 1
        except Exception:
            pass
    print(f"   Created {created} inpatient stays")


def _try_link(api, endpoint, data):
    try:
        api.rest("POST", endpoint, data)
        return True
    except Exception:
        return False


def create_dashboard(api: TwentyAPI):
    """Create BVHM CSKH Dashboard with charts."""
    print("\n16. Creating BVHM Dashboard...")

    # Get field IDs we need for charts
    task_obj_id = api.get_object_id("task")
    person_obj_id = api.get_object_id("person")
    task_fields = api.get_fields(task_obj_id)
    person_fields = api.get_fields(person_obj_id)

    care_type_field = task_fields.get("careType")
    call_status_field = task_fields.get("callStatus")
    due_at_field = task_fields.get("dueAt")
    task_id_field = task_fields.get("id")
    person_id_field = person_fields.get("id")
    treatment_stage_field = person_fields.get("treatmentStage")

    if not all([care_type_field, call_status_field, task_id_field, person_id_field]):
        print("   Missing required fields for dashboard, skipping")
        return

    # Delete existing BVHM dashboards + default dashboard
    try:
        existing = api.rest("GET", "dashboards?limit=10")
        dashboards = existing.get("data", {}).get("dashboards", [])
        for d in dashboards:
            try:
                api.rest("DELETE", f"dashboards/{d['id']}")
            except Exception:
                pass
        if dashboards:
            print(f"   Cleaned {len(dashboards)} existing dashboards")
    except Exception:
        pass

    # Step 1: Create PageLayout via metadata API
    try:
        layout_r = api._gql(
            'mutation($input: CreatePageLayoutInput!) { createPageLayout(input: $input) { id } }',
            {"input": {
                "name": "Báo cáo CSKH",
                "type": "DASHBOARD",
            }},
        )
        layout_id = layout_r["data"]["createPageLayout"]["id"]
    except Exception as e:
        print(f"   Failed to create page layout: {e}")
        return

    # Step 2: Create tab
    try:
        tab_r = api._gql(
            'mutation($input: CreatePageLayoutTabInput!) { createPageLayoutTab(input: $input) { id } }',
            {"input": {
                "pageLayoutId": layout_id,
                "title": "Tổng quan",
                "position": 0,
            }},
        )
        tab_id = tab_r["data"]["createPageLayoutTab"]["id"]
    except Exception as e:
        print(f"   Failed to create tab: {e}")
        return

    # Step 3: Create widgets
    widgets = [
        # Row 0: KPI cards
        {
            "title": "Tổng bệnh nhân",
            "type": "GRAPH",
            "objectMetadataId": person_obj_id,
            "gridPosition": {"row": 0, "column": 0, "rowSpan": 2, "columnSpan": 3},
            "configuration": {
                "configurationType": "AGGREGATE_CHART",
                "aggregateFieldMetadataId": person_id_field,
                "aggregateOperation": "COUNT",
                "displayDataLabel": True,
            },
        },
        {
            "title": "Tổng công việc CS",
            "type": "GRAPH",
            "objectMetadataId": task_obj_id,
            "gridPosition": {"row": 0, "column": 3, "rowSpan": 2, "columnSpan": 3},
            "configuration": {
                "configurationType": "AGGREGATE_CHART",
                "aggregateFieldMetadataId": task_id_field,
                "aggregateOperation": "COUNT",
                "displayDataLabel": True,
            },
        },
        {
            "title": "Chưa gọi",
            "type": "GRAPH",
            "objectMetadataId": task_obj_id,
            "gridPosition": {"row": 0, "column": 6, "rowSpan": 2, "columnSpan": 3},
            "configuration": {
                "configurationType": "AGGREGATE_CHART",
                "aggregateFieldMetadataId": call_status_field,
                "aggregateOperation": "COUNT_EMPTY",
                "displayDataLabel": True,
                "label": "Chưa gọi",
            },
        },
        # Row 2: Charts
        {
            "title": "Công việc theo loại chăm sóc",
            "type": "GRAPH",
            "objectMetadataId": task_obj_id,
            "gridPosition": {"row": 2, "column": 0, "rowSpan": 6, "columnSpan": 6},
            "configuration": {
                "configurationType": "PIE_CHART",
                "aggregateFieldMetadataId": task_id_field,
                "aggregateOperation": "COUNT",
                "groupByFieldMetadataId": care_type_field,
                "displayDataLabel": True,
                "displayLegend": True,
                "showCenterMetric": True,
            },
        },
        {
            "title": "Trạng thái cuộc gọi",
            "type": "GRAPH",
            "objectMetadataId": task_obj_id,
            "gridPosition": {"row": 2, "column": 6, "rowSpan": 6, "columnSpan": 6},
            "configuration": {
                "configurationType": "BAR_CHART",
                "aggregateFieldMetadataId": task_id_field,
                "aggregateOperation": "COUNT",
                "primaryAxisGroupByFieldMetadataId": call_status_field,
                "layout": "VERTICAL",
                "displayDataLabel": True,
                "displayLegend": False,
            },
        },
    ]

    # Add treatmentStage chart if field exists
    if treatment_stage_field:
        widgets.append({
            "title": "Bệnh nhân theo giai đoạn điều trị",
            "type": "GRAPH",
            "objectMetadataId": person_obj_id,
            "gridPosition": {"row": 8, "column": 0, "rowSpan": 6, "columnSpan": 6},
            "configuration": {
                "configurationType": "PIE_CHART",
                "aggregateFieldMetadataId": person_id_field,
                "aggregateOperation": "COUNT",
                "groupByFieldMetadataId": treatment_stage_field,
                "displayDataLabel": True,
                "displayLegend": True,
                "showCenterMetric": True,
            },
        })

    # Công việc CS theo thời gian (line chart)
    if due_at_field:
        widgets.append({
            "title": "Công việc CS theo thời gian",
            "type": "GRAPH",
            "objectMetadataId": task_obj_id,
            "gridPosition": {"row": 8, "column": 6, "rowSpan": 6, "columnSpan": 6},
            "configuration": {
                "configurationType": "LINE_CHART",
                "aggregateFieldMetadataId": task_id_field,
                "aggregateOperation": "COUNT",
                "primaryAxisGroupByFieldMetadataId": due_at_field,
                "primaryAxisDateGranularity": "WEEK",
                "displayDataLabel": False,
                "displayLegend": False,
                "isCumulative": False,
            },
        })

    # Công việc theo nhân viên (bar chart by createdBy)
    created_by_field = task_fields.get("createdBy")
    if created_by_field:
        widgets.append({
            "title": "Khối lượng CS theo nhân viên",
            "type": "GRAPH",
            "objectMetadataId": task_obj_id,
            "gridPosition": {"row": 14, "column": 0, "rowSpan": 6, "columnSpan": 12},
            "configuration": {
                "configurationType": "BAR_CHART",
                "aggregateFieldMetadataId": task_id_field,
                "aggregateOperation": "COUNT",
                "primaryAxisGroupByFieldMetadataId": created_by_field,
                "primaryAxisGroupBySubFieldName": "name",
                "layout": "VERTICAL",
                "displayDataLabel": True,
                "displayLegend": False,
            },
        })

    created_widgets = 0
    for w in widgets:
        try:
            widget_input = {
                "pageLayoutTabId": tab_id,
                "title": w["title"],
                "type": w["type"],
                "gridPosition": w["gridPosition"],
                "configuration": w["configuration"],
            }
            if w.get("objectMetadataId"):
                widget_input["objectMetadataId"] = w["objectMetadataId"]
            api._gql(
                'mutation($input: CreatePageLayoutWidgetInput!) { createPageLayoutWidget(input: $input) { id } }',
                {"input": widget_input},
            )
            created_widgets += 1
        except Exception as e:
            print(f"   Widget '{w['title']}': {e}")

    # Step 4: Create dashboard record linking to page layout
    try:
        api.rest("POST", "dashboards", {"title": "Báo cáo CSKH", "pageLayoutId": layout_id})
        print(f"   Created dashboard with {created_widgets} widgets")
    except Exception as e:
        print(f"   Dashboard record: {e}")


# =============================================================================
# MAIN
# =============================================================================

def main():
    parser = argparse.ArgumentParser(description="BVHM Hospital CRM Setup")
    parser.add_argument("--url", default="http://localhost:3000", help="Twenty server URL")
    parser.add_argument("--email", default="admin@bvhm.vn", help="Admin email")
    parser.add_argument("--password", default=None, help="Admin password (default: same as email)")
    parser.add_argument("--level", choices=["base", "demo"], default="demo", help="Setup level: base (no patient data) or demo (with sample data)")
    args = parser.parse_args()

    password = args.password or args.email
    api = TwentyAPI(args.url)

    print("=" * 50)
    print("BVHM Hospital CRM Setup")
    print("=" * 50)
    print(f"Server: {args.url}")
    print(f"Level:  {args.level}")

    # 1. Auth
    print("\n1. Authenticating...")
    api.ensure_auth(args.email, password)

    # Base setup (always runs)
    cleanup_defaults(api)
    cleanup_workflows(api)
    deactivate_opportunity(api)
    cleanup_navigation(api)
    rename_objects(api)
    create_custom_fields(api)
    create_custom_objects(api)
    create_views(api)
    seed_companies(api)
    create_workflows(api)

    # Demo data (only with --level demo)
    if args.level == "demo":
        seed_demo_data(api)

    # Dashboard (always)
    create_dashboard(api)

    print("\n" + "=" * 50)
    print(f"Setup complete! Level: {args.level}")
    print(f"Open: {args.url}")
    print("=" * 50)


if __name__ == "__main__":
    main()
