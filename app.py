import os
from datetime import datetime
import streamlit as st

# ------------------------------------
# Settings & Branding
# ------------------------------------
APP_TITLE = "ระบบบริหารงานบุคคลโรงเรียนอนุบาลวัดคลองใหญ่"
CONTACT_EMAIL = "pakka555@gmail.com"  # ครูสุพจน์
BRAND_PRIMARY = "#0a2342"             # น้ำเงินกรมท่า
BRAND_MUTED = "#4f5b66"               # เทาเข้มอ่านง่าย

# ใช้ session_state เพื่อสลับหน้า (ให้ปุ่มบนการ์ดพาไปเมนูได้)
if "menu" not in st.session_state:
    st.session_state["menu"] = "หน้าแรก"

# ------------------------------------
# Helper: โหลดฟอนต์ Google
# ------------------------------------
# ---------- สีหลักที่ใช้ทั่วเว็บ ----------
BRAND_PRIMARY = "#0a2342"   # น้ำเงินเข้ม
BRAND_MUTED   = "#445b66"   # เทาอมฟ้า

def inject_fonts_and_css():
    st.markdown(
        f"""
        <!-- Google Fonts -->
        <link rel="preconnect" href="https://fonts.googleapis.com">
        <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
        <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+Thai:wght@300;400;600;700&display=swap" rel="stylesheet">

        <style>
          :root {{
            --brand-primary: {BRAND_PRIMARY};
            --brand-muted:   {BRAND_MUTED};
          }}

          html, body, * {{
            font-family: "Noto Sans Thai", system-ui, -apple-system, Segoe UI, Roboto, sans-serif !important;
          }}

          /* ปุ่มหลัก */
          .stButton > button {{
            background: var(--brand-primary);
            color: #fff;
            border: none;
            border-radius: 10px;
            padding: 0.6rem 1.1rem;
            font-weight: 600;
          }}
          .stButton > button:hover {{
            filter: brightness(1.05);
          }}

          /* การ์ด (container) */
          .app-card {{
            border: 1px solid #e7ecef;
            background: #fff;
            border-radius: 16px;
            padding: 18px 22px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.04);
          }}

          /* ตัวอย่างที่มี % ใน CSS จะปลอดภัยเพราะเราใช้ f-string */
          .hero-mask {{
            background: linear-gradient(0deg, rgba(255,255,255,0.92) 0%, rgba(255,255,255,0.92) 100%);
          }}
        </style>
        """,
        unsafe_allow_html=True,
    )

# ------------------------------------
# หน้าแรก
# ------------------------------------
def show_home():
    inject_fonts_and_css()

    # 1) Banner (ถ้ามีไฟล์)
    if os.path.exists("banner.jpg"):
        st.markdown('<div class="kys-banner">', unsafe_allow_html=True)
        st.image("banner.jpg", use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # 2) Logo + Title
    col1, col2 = st.columns([1, 4])
    with col1:
        if os.path.exists("logo.png"):
            st.image("logo.png", width=180)  # ปรับขนาดโลโก้ได้
    with col2:
        st.markdown(
            """
            <h1 style='font-size:42px; font-weight:700; color:#0a2342; margin-bottom:0'>
                ระบบบริหารงานบุคคลโรงเรียนอนุบาลวัดคลองใหญ่
            </h1>
            <p style='color:#445b66; margin-top:4px; font-size:17px'>
                ช่วยให้ครูและบุคลากรทางการศึกษาจัดการข้อมูลบุคคลได้อย่างมีระบบ โปร่งใส และตรวจสอบได้
            </p>
            """,
            unsafe_allow_html=True
        )

    st.markdown("---")


    # 3) การ์ด 3 ใบ (สูงเท่ากัน + ปุ่มชิดล่าง)
    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown(
            """
            <div class="kys-card">
              <h3>👩‍🏫 สำหรับครูผู้สอน <span class="kys-badge">Teacher</span></h3>
              <ul class="kys-muted">
                <li>จัดการ/ปรับปรุงข้อมูลส่วนบุคคล</li>
                <li>ส่งคำขอ (ลา/ไปราชการ/อบรม ฯลฯ) และตรวจสอบสถานะ</li>
                <li>อัปโหลดเอกสารงานบุคคล (ฟอร์ม/ใบอนุญาต/แฟ้มสะสมงาน)</li>
              </ul>
              <div class="kys-push"></div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("➡️ เข้าสู่ระบบครู", use_container_width=True, key="go_teacher"):
            st.session_state["menu"] = "สำหรับผู้ใช้"
            st.rerun()

    with c2:
        st.markdown(
            """
            <div class="kys-card">
              <h3>✴️ ผู้ดูแลโมดูล <span class="kys-badge">Module Admin</span></h3>
              <ul class="kys-muted">
                <li>ตรวจสอบ/อนุมัติคำขอในโมดูลที่รับผิดชอบ</li>
                <li>ติดตามเอกสาร ปรับแก้ข้อมูลที่จำเป็น</li>
                <li>ดูสรุปสถิติและรายงานในโมดูล</li>
              </ul>
              <div class="kys-push"></div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("➡️ เข้าสู่ระบบผู้ดูแลโมดูล", use_container_width=True, key="go_module_admin"):
            st.session_state["menu"] = "สำหรับผู้ดูแล"
            st.rerun()

    with c3:
        st.markdown(
            """
            <div class="kys-card">
              <h3>🛡️ แอดมินใหญ่ <span class="kys-badge">Superadmin</span></h3>
              <ul class="kys-muted">
                <li>กำกับดูแลงานภาพรวมของระบบทั้งหมด</li>
                <li>จัดการข้อมูลบุคลากร/สิทธิ์การเข้าใช้</li>
                <li>ออกรายงานภาพรวมเพื่อการบริหาร</li>
              </ul>
              <div class="kys-push"></div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("➡️ เข้าสู่ระบบแอดมินใหญ่", use_container_width=True, key="go_superadmin"):
            st.session_state["menu"] = "สำหรับผู้ดูแล"
            st.rerun()

    # 4) เครดิต (ชิดขวา) — ไม่มีบล็อกลิงก์ด่วนแล้ว
    st.markdown(
        """
        <div class="kys-footer">
            พัฒนาโดย กลุ่มบริหารงานบุคคล โรงเรียนอนุบาลวัดคลองใหญ่ จังหวัดตราด
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 5) ปุ่มลอย ติดต่อผู้ดูแล
    st.markdown(
        f"""
        <div class="kys-fab">
            <a href="mailto:{CONTACT_EMAIL}">
                <button style="
                    background:{BRAND_PRIMARY};
                    color:#fff; border:0; border-radius:999px;
                    padding:12px 16px; box-shadow:0 4px 14px rgba(10,35,66,.18);
                    cursor:pointer;">
                    ✉️ ติดต่อผู้ดูแลระบบ
                </button>
            </a>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ------------------------------------
# Placeholder สำหรับหน้าอื่น
# ------------------------------------
def show_teacher_portal():
    st.subheader("เข้าสู่ระบบผู้ใช้ (ครู)")
    st.info("ใส่ฟอร์มล็อกอิน (Teacher ID + PIN) หรือเมนูย่อยต่าง ๆ ได้ที่นี่")
    st.markdown("- ตัวอย่าง: แบบฟอร์มคำขอลา, อัปโหลดเอกสาร, ตรวจสอบสถานะ ฯลฯ")

def show_admin_portal():
    st.subheader("เข้าสู่ระบบผู้ดูแล")
    st.info("ใส่ฟอร์มล็อกอิน/เมนูของ module_admin / superadmin ได้ที่นี่")
    st.markdown("- ตัวอย่าง: อนุมัติคำขอ, จัดการสิทธิ์, รายงานภาพรวม ฯลฯ")


# ------------------------------------
# Layout: Sidebar + Routing
# ------------------------------------
inject_fonts_and_css()  # ให้ฟอนต์ใช้ได้ทุกหน้า

with st.sidebar:
    st.markdown("### เมนู")
    st.session_state["menu"] = st.radio(
        "ไปหน้า:",
        ["หน้าแรก", "สำหรับผู้ใช้", "สำหรับผู้ดูแล"],
        index=["หน้าแรก", "สำหรับผู้ใช้", "สำหรับผู้ดูแล"].index(st.session_state["menu"])
    )

if st.session_state["menu"] == "หน้าแรก":
    show_home()
elif st.session_state["menu"] == "สำหรับผู้ใช้":
    show_teacher_portal()
elif st.session_state["menu"] == "สำหรับผู้ดูแล":
    show_admin_portal()
