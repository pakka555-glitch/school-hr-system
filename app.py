import os
import base64
import pandas as pd
import streamlit as st

# ==============================
# Settings & Branding
# ==============================
APP_TITLE = "ระบบบริหารงานบุคคลโรงเรียนอนุบาลวัดคลองใหญ่"
CONTACT_EMAIL = "pakka555@gmail.com"  # ครูสุพจน์
BRAND_PRIMARY = "#0a2342"            # น้ำเงินกรมท่า
BRAND_MUTED = "#445b66"              # เทาอมฟ้า

ASSETS_DIR = "assets"
BANNER_PATH = os.path.join(ASSETS_DIR, "banner.jpg")

if "menu" not in st.session_state:
    st.session_state["menu"] = "หน้าแรก"

# ==============================
# Load Google Font + Global CSS
# ==============================
def inject_fonts_and_css():
    st.markdown(
        f"""
        <link rel="preconnect" href="https://fonts.googleapis.com">
        <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
        <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+Thai:wght@300;400;500;700&display=swap" rel="stylesheet">

        <style>
          :root {{
            --brand: {BRAND_PRIMARY};
            --muted: {BRAND_MUTED};
            --bg-card: #ffffff;
            --bg-soft: #f5f8fb;
            --shadow: 0 10px 30px rgba(10,35,66,0.08);
            --radius: 14px;
          }}

          html, body, [class*="css"] {{
            font-family: 'Noto Sans Thai', system-ui, -apple-system, Segoe UI, Roboto, 'Helvetica Neue', Arial, sans-serif;
          }}

          .block-container {{ max-width: 1240px !important; }}

          /* Banner */
          .kys-banner {{
            border-radius: var(--radius);
            overflow: hidden;
            box-shadow: var(--shadow);
            margin: 6px 0 18px 0;
          }}

          /* Title */
          .kys-title h1 {{
            margin: 0;
            font-size: clamp(28px, 2.6vw, 38px);
            color: var(--brand);
            font-weight: 800;
          }}
          .kys-title p {{
            margin: 6px 0 0 0;
            color: var(--muted);
          }}

          /* Grid การ์ด */
          .kys-grid {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 26px;
            margin-top: 14px;
          }}
          @media (max-width: 1100px) {{
            .kys-grid {{ grid-template-columns: repeat(2, 1fr); }}
          }}
          @media (max-width: 760px) {{
            .kys-grid {{ grid-template-columns: 1fr; }}
          }}

          .kys-card {{
            background: var(--bg-card);
            border-radius: var(--radius);
            box-shadow: var(--shadow);
            padding: 24px 22px;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            min-height: 340px;
          }}
          .kys-card h3 {{
            margin: 0 0 6px 0;
            font-weight: 800;
            color: var(--brand);
          }}
          .kys-card h4 {{
            margin: 0 0 10px 0;
            font-weight: 600;
            color: var(--muted);
          }}
          .kys-card ul {{
            margin: 8px 0 0 18px;
            color: #314657;
            line-height: 1.6;
          }}

          /* ปุ่มสวยแบบ custom */
          .kys-actions {{ margin-top: auto; display: flex; }}
          .kys-btn {{
            display: inline-flex;
            align-items: center;
            justify-content: center;
            gap: 10px;
            width: 100%;
            min-height: 52px;
            padding: 12px 18px;
            border-radius: 12px;
            background: var(--brand);
            color: #fff !important;
            text-decoration: none !important;
            font-weight: 700;
            box-shadow: var(--shadow);
            transition: transform .05s ease, filter .15s ease;
          }}
          .kys-btn:hover {{
            filter: brightness(1.06);
            transform: translateY(-1px);
          }}
          /* ปุ่มติดต่อผู้ดูแล */
          .kys-contact {{
            width: 100%;
            display: flex;
            justify-content: flex-end;
            margin-top: 18px;
          }}
          .kys-contact a {{
            display: inline-flex;
            align-items: center;
            gap: 8px;
            padding: 10px 14px;
            border-radius: 999px;
            background: #0f2748;
            color: #fff !important;
            text-decoration: none;
            box-shadow: var(--shadow);
          }}
        </style>
        """,
        unsafe_allow_html=True,
    )

# ==============================
# Home Page
# ==============================
def show_home():
    inject_fonts_and_css()

    # Banner
    if os.path.exists(BANNER_PATH):
        st.markdown('<div class="kys-banner">', unsafe_allow_html=True)
        st.image(BANNER_PATH, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # Title
    st.markdown(
        f"""
        <div class="kys-title" style="text-align:center; margin-top:10px;">
          <h1>{APP_TITLE}</h1>
          <p style="color:{BRAND_MUTED}; font-size:18px;">
            ช่วยให้ครูและบุคลากรทางการศึกษาจัดการข้อมูลบุคคลง่าย โปร่งใส และตรวจสอบได้
          </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Grid การ์ด
    st.markdown('<div class="kys-grid">', unsafe_allow_html=True)

    st.markdown("""
      <div class="kys-card">
        <div>
          <h3>👩‍🏫 สำหรับครูผู้สอน</h3>
          <h4>Teacher</h4>
          <ul>
            <li>จัดการ/ปรับปรุงข้อมูลส่วนบุคคล</li>
            <li>ส่งคำขอ (ลา/ไปราชการ/อบรม ฯลฯ) และตรวจสอบสถานะ</li>
            <li>อัปโหลดเอกสารงานบุคคล (ฟอร์ม/ใบอนุญาต/แฟ้มสะสมงาน)</li>
          </ul>
        </div>
        <div class="kys-actions">
          <a class="kys-btn" href="?route=login_teacher">🔐 เข้าสู่ระบบครู</a>
        </div>
      </div>
    """, unsafe_allow_html=True)

    st.markdown("""
      <div class="kys-card">
        <div>
          <h3>⚙️ ผู้ดูแลโมดูล</h3>
          <h4>Module Admin</h4>
          <ul>
            <li>ตรวจสอบ/อนุมัติคำขอในโมดูลที่รับผิดชอบ</li>
            <li>ติดตามเอกสาร ปรับแก้ข้อมูลที่จำเป็น</li>
            <li>ดูสรุปสถิติและรายงานในโมดูล</li>
          </ul>
        </div>
        <div class="kys-actions">
          <a class="kys-btn" href="?route=login_module_admin">🔐 เข้าสู่ระบบผู้ดูแลโมดูล</a>
        </div>
      </div>
    """, unsafe_allow_html=True)

    st.markdown("""
      <div class="kys-card">
        <div>
          <h3>🛡️ แอดมินใหญ่</h3>
          <h4>Superadmin</h4>
          <ul>
            <li>กำกับดูแลภาพรวมของระบบทั้งหมด</li>
            <li>จัดการข้อมูลบุคลากร/สิทธิ์การเข้าใช้</li>
            <li>ออกรายงานภาพรวมเพื่อการบริหาร</li>
          </ul>
        </div>
        <div class="kys-actions">
          <a class="kys-btn" href="?route=login_superadmin">🔐 เข้าสู่ระบบแอดมินใหญ่</a>
        </div>
      </div>
    """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

    # Footer
    st.markdown(f"""
      <div class="kys-contact">
        <a href="mailto:{CONTACT_EMAIL}">📧 ติดต่อผู้ดูแลระบบ</a>
      </div>
      <hr style="margin-top:32px;margin-bottom:12px;border:1px solid #e0e6ec;">
      <div style='text-align:center; color:#445b66; font-size:15px;'>
          พัฒนาโดย <b>กลุ่มบริหารงานบุคคล โรงเรียนอนุบาลวัดคลองใหญ่ จังหวัดตราด</b><br>
          เพื่อยกระดับการบริหารจัดการงานบุคคลให้ทันสมัย โปร่งใส และตรวจสอบได้
      </div>
    """, unsafe_allow_html=True)

# ==============================
# Main App
# ==============================
def main():
    st.set_page_config(page_title=APP_TITLE, page_icon="🏫", layout="wide")
    show_home()

if __name__ == "__main__":
    main()
