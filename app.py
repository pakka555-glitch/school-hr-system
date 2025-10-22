# -*- coding: utf-8 -*-
import os
from datetime import datetime
import streamlit as st

# -------------------------------------------------
# ⚙️ ตั้งค่าหน้าจอ (ต้องอยู่ด้านบนสุดก่อนมี UI ใดๆ)
# -------------------------------------------------
st.set_page_config(
    page_title="ระบบบริหารงานบุคคลโรงเรียนอนุบาลวัดคลองใหญ่",
    page_icon="🌸",
    layout="wide",
)

# -------------------------------------------------
# Settings & Branding
# -------------------------------------------------
APP_TITLE      = "ระบบบริหารงานบุคคลโรงเรียนอนุบาลวัดคลองใหญ่"
CONTACT_EMAIL  = "pakka555@gmail.com"  # ครูสุพจน์
BRAND_PRIMARY  = "#0a2342"             # น้ำเงินกรมท่า
BRAND_MUTED    = "#4f5b66"             # เทาน้ำเงิน

# ใช้ session_state เพื่อจำหน้า (ไม่เปลี่ยนเองตอนกลับมา)
if "menu" not in st.session_state:
    st.session_state["menu"] = "หน้าแรก"

# -------------------------------------------------
# Helper: path รูปในโฟลเดอร์ assets
# -------------------------------------------------
def asset(name: str) -> str:
    return os.path.join("assets", name)

# -------------------------------------------------
# โหลดฟอนต์ + CSS (เรียกหนึ่งครั้งทุกหน้า)
# -------------------------------------------------
def inject_fonts_and_css():
    st.markdown(
        f"""
        <link rel="preconnect" href="https://fonts.googleapis.com">
        <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
        <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+Thai:wght@300;400;600;700&display=swap" rel="stylesheet">

       <style>
    :root {
        --brand: {BRAND_PRIMARY};
        --muted: {BRAND_MUTED};
    }

    html, body, [class*="css"] {
        font-family: 'Noto Sans Thai', system-ui, -apple-system, Segoe UI, Roboto, 'Helvetica Neue', Arial, 'Noto Sans', 'Liberation Sans', sans-serif;
        color: #14202e;
    }

    /* โครงกว้างขึ้น */
    .block-container {
        max-width: 1320px;
        padding-top: 1rem !important;
        padding-bottom: 1rem !important;
    }

    /* การ์ด 3 ใบสูงเท่ากัน ปุ่มอยู่ล่าง */
    .kys-card {
        background: #fff;
        border: 1px solid #eaf0f6;
        border-radius: 16px;
        padding: 22px;
        display: flex;
        flex-direction: column;
        justify-content: space-between; /* ปุ่มอยู่ล่าง */
        height: 100%;
        box-shadow: 0 6px 16px rgba(10,35,66,.04);
    }

    .kys-card h3 {
        margin: 0 0 6px 0;
        color: var(--brand);
        font-weight: 800;
    }

    .kys-card h4 {
        margin: 0 0 8px 0;
        color: #0e2a47;
        font-weight: 700;
    }

    .kys-card ul {
        margin: 0 0 14px 16px;
    }

    /* ปุ่มหลัก */
    .kys-btn {
        display: inline-flex;
        align-items: center;
        gap: .6rem;
        justify-content: center;
        width: 100%;
        border: none;
        color: #fff !important;
        background: var(--brand);
        padding: 10px 14px;
        border-radius: 10px;
        text-decoration: none !important;
        box-shadow: 0 6px 14px rgba(10,35,66,.18);
        font-weight: 700;
    }

    .kys-btn:hover {
        filter: brightness(1.08);
    }

    /* ปุ่มรอง */
    .kys-btn.secondary {
        background: #1b3b6f;
    }

    /* ปุ่มติดต่อผู้ดูแลระบบ - ชิดขวา */
    .kys-contact {
        display: flex;
        justify-content: flex-end;
        margin-top: 20px;
    }

    /* footer ขวาล่าง */
    .kys-footer {
        display: flex;
        justify-content: flex-end;
        color: #6b7785;
        font-size: 14px;
        margin-top: 8px;
    }
</style>
        """,
        unsafe_allow_html=True,
    )


# -------------------------------------------------
# หน้า: หน้าแรก (Home)
# -------------------------------------------------
def show_home():
    inject_fonts_and_css()

    # 1) Banner (ถ้ามีไฟล์)
    if os.path.exists(asset("banner.jpg")):
        st.markdown('<div class="kys-banner">', unsafe_allow_html=True)
        st.image(asset("banner.jpg"), use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
        st.write("")  # spacing

    # 2) Logo + Title
    col_logo, col_title = st.columns([1, 4], vertical_alignment="center")
    with col_logo:
        if os.path.exists(asset("logo.jpg")):
            st.image(asset("logo.jpg"), use_container_width=True)
    with col_title:
        st.markdown(
            f"""
            <div class="kys-hero">
                <h1>{APP_TITLE}</h1>
                <p>ช่วยให้ครูและบุคลากรทางการศึกษาจัดการข้อมูลบุคคลได้อย่างมีระบบ โปร่งใส และตรวจสอบได้</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("---")

    # 3) บทบาท 3 การ์ด
    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown(
            """
            <div class="kys-card">
                <h3>👩‍🏫 สำหรับครูผู้สอน</h3>
                <h4>Teacher</h4>
                <ul>
                    <li>จัดการ/ปรับปรุงข้อมูลส่วนบุคคล</li>
                    <li>ส่งคำขอ (ลา/ไปราชการ/อบรม ฯลฯ) และตรวจสอบสถานะ</li>
                    <li>อัปโหลดเอกสารงานบุคคล (ฟอร์ม/ใบอนุญาต/แฟ้มสะสม)</li>
                </ul>
                <div class="kys-spacer"></div>
                <a class="kys-btn" href="#ครูเข้าสู่ระบบ">🔐 เข้าสู่ระบบครู</a>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with c2:
        st.markdown(
            """
            <div class="kys-card">
                <h3>⚙️ ผู้ดูแลโมดูล</h3>
                <h4>Module Admin</h4>
                <ul>
                    <li>ตรวจสอบ/อนุมัติคำขอในโมดูลที่รับผิดชอบ</li>
                    <li>ติดตามเอกสาร ปรับแก้ข้อมูลที่จำเป็น</li>
                    <li>ดูสรุปสถิติและรายงานในโมดูล</li>
                </ul>
                <div class="kys-spacer"></div>
                <a class="kys-btn secondary" href="#ผู้ดูแลโมดูลเข้าสู่ระบบ">🔐 เข้าสู่ระบบผู้ดูแลโมดูล</a>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with c3:
        st.markdown(
            """
            <div class="kys-card">
                <h3>🛡️ แอดมินใหญ่</h3>
                <h4>Superadmin</h4>
                <ul>
                    <li>กำกับดูแลภาพรวมของระบบทั้งหมด</li>
                    <li>จัดการข้อมูลบุคลากร/สิทธิ์การเข้าใช้</li>
                    <li>ออกรายงานภาพรวมเพื่อการบริหาร</li>
                </ul>
                <div class="kys-spacer"></div>
                <a class="kys-btn" href="#แอดมินใหญ่เข้าสู่ระบบ">🔐 เข้าสู่ระบบแอดมินใหญ่</a>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.write("")
    # ปุ่มติดต่อผู้ดูแลระบบ
   st.markdown(
    f"""
    <div class="kys-contact">
        <a class="kys-btn" href="mailto:{CONTACT_EMAIL}">✉️ ติดต่อผู้ดูแลระบบ</a>
    </div>
    """,
    unsafe_allow_html=True,
)

    # Footer ขวา
    st.markdown(
        """
        <div class="kys-footer">
          พัฒนาโดย กลุ่มบริหารงานบุคคล โรงเรียนอนุบาลวัดคลองใหญ่ จังหวัดตราด
        </div>
        """,
        unsafe_allow_html=True,
    )


# -------------------------------------------------
# ตัวอย่างหน้า: สำหรับผู้ใช้ (ครู)
# -------------------------------------------------
def show_teacher_portal():
    inject_fonts_and_css()
    st.markdown("### 👩‍🏫 เข้าสู่ระบบผู้ใช้ (ครู)")
    tid = st.text_input("Teacher ID")
    pin = st.text_input("PIN", type="password")
    if st.button("เข้าสู่ระบบ"):
        st.success("เข้าสู่ระบบสำเร็จ (ตัวอย่างหน้า)")

# -------------------------------------------------
# ตัวอย่างหน้า: สำหรับผู้ดูแล (module / superadmin)
# -------------------------------------------------
def show_admin_portal():
    inject_fonts_and_css()
    st.markdown("### 🛡️ เข้าสู่ระบบผู้ดูแล")
    uid = st.text_input("Admin ID")
    pin = st.text_input("PIN", type="password")
    if st.button("เข้าสู่ระบบผู้ดูแล"):
        st.success("เข้าสู่ระบบผู้ดูแลสำเร็จ (ตัวอย่างหน้า)")


# -------------------------------------------------
# Sidebar + Routing
# -------------------------------------------------
inject_fonts_and_css()  # ให้ฟอนต์/ธีมใช้ได้ทุกหน้า

with st.sidebar:
    st.markdown("### เมนู")
    st.session_state["menu"] = st.radio(
        "ไปหน้า:",
        ["หน้าแรก", "สำหรับผู้ใช้", "สำหรับผู้ดูแล"],
        index=["หน้าแรก", "สำหรับผู้ใช้", "สำหรับผู้ดูแล"].index(st.session_state["menu"])
    )

# Router
if st.session_state["menu"] == "หน้าแรก":
    show_home()
elif st.session_state["menu"] == "สำหรับผู้ใช้":
    show_teacher_portal()
elif st.session_state["menu"] == "สำหรับผู้ดูแล":
    show_admin_portal()
