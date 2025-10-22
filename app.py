import os
import base64
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
LOGO_PATH   = os.path.join(ASSETS_DIR, "logo.jpg")

# init session_state for routing (เปิดครั้งแรกให้ไปหน้าแรก)
if "menu" not in st.session_state:
    st.session_state["menu"] = "หน้าแรก"


# ==============================
# Load Google Font + Global CSS
# ==============================
def inject_fonts_and_css():
    st.markdown(
        """
        <link rel="preconnect" href="https://fonts.googleapis.com">
        <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
        <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+Thai:wght@300;400;500;700&display=swap" rel="stylesheet">

        <style>
          :root{
            --brand: """ + BRAND_PRIMARY + """;
            --muted: """ + BRAND_MUTED + """;
            --bg-card: #ffffff;
            --bg-soft: #f5f8fb;
            --shadow: 0 10px 30px rgba(10,35,66,0.08);
            --radius: 14px;
          }
          html, body, [class*="css"] {
            font-family: 'Noto Sans Thai', system-ui, -apple-system, Segoe UI, Roboto, 'Helvetica Neue', Arial, sans-serif;
          }
          .block-container { max-width: 1240px !important; }

          /* Banner */
          .kys-banner {
            border-radius: var(--radius);
            overflow: hidden;
            box-shadow: var(--shadow);
            margin: 6px 0 18px 0;
          }

          /* ส่วนหัว Title/Subtitle & โลโก้ */
          .kys-titlerow{
            display:flex; gap:18px; align-items:center; margin: 8px 0 8px 0;
          }
          .kys-logo{
            width: 68px; height: 68px; border-radius: 16px; box-shadow: var(--shadow); object-fit:cover;
            background:#fff;
          }
          .kys-title h1{
            margin:0; font-size: clamp(28px, 2.6vw, 38px); color: var(--brand); font-weight:800;
          }
          .kys-title p{ margin:6px 0 0 0; color: var(--muted); }

          /* Grid 3 การ์ด */
          .kys-grid{
            display:grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 26px;
            margin-top:14px;
          }
          @media (max-width: 1100px){ .kys-grid{ grid-template-columns: repeat(2, 1fr); } }
          @media (max-width: 760px){ .kys-grid{ grid-template-columns: 1fr; } }

          .kys-card{
            background: var(--bg-card);
            border-radius: var(--radius);
            box-shadow: var(--shadow);
            padding: 24px 22px;
            display:flex;
            flex-direction: column;
            min-height: 320px;
          }
          .kys-card > div { flex:1; }
          .kys-card h3{ margin:0 0 6px 0; font-weight:800; color: var(--brand); }
          .kys-card h4{ margin:0 0 10px 0; font-weight:600; color: var(--muted); }
          .kys-card ul{ margin: 8px 0 0 18px; color:#314657; line-height:1.6; }

          /* ปุ่มอยู่ด้านล่างให้เสมอกันทุกใบ */
          .kys-btn{
            display:inline-flex; align-items:center; justify-content:center;
            gap:8px; padding: 12px 16px; border-radius: 12px;
            background: var(--brand); color:#fff !important; text-decoration:none !important;
            box-shadow: var(--shadow); margin-top: 14px; min-height: 48px;
          }
          .kys-btn:hover{ filter:brightness(1.06); }

          /* ปุ่มติดต่อผู้ดูแล (ลอยอยู่ขวาล่างหน้าแรก) */
          .kys-contact{ width:100%; display:flex; justify-content:flex-end; margin-top:18px; }
          .kys-contact a{
            display:inline-flex; align-items:center; gap:8px; padding: 10px 14px;
            border-radius: 999px; background: #0f2748; color: #fff !important;
            text-decoration:none; box-shadow: var(--shadow);
          }
        </style>
        """,
        unsafe_allow_html=True,
    )


# ==============================
# Pages
# ==============================
def show_home():
    inject_fonts_and_css()

    # 1) Banner (ถ้ามี)
    if os.path.exists(BANNER_PATH):
        st.markdown('<div class="kys-banner">', unsafe_allow_html=True)
        st.image(BANNER_PATH, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # 2) Title + Subtitle (ไม่มีโลโก้)
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

    # 3) การ์ด 3 ใบ
    st.markdown(
        """
        <div class="kys-grid">

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
            <a class="kys-btn" href="#">🔐 เข้าสู่ระบบครู</a>
          </div>

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
            <a class="kys-btn" href="#">🔐 เข้าสู่ระบบผู้ดูแลโมดูล</a>
          </div>

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
            <a class="kys-btn" href="#">🔐 เข้าสู่ระบบแอดมินใหญ่</a>
          </div>

        </div>
        """,
        unsafe_allow_html=True,
    )

    # 4) ปุ่มติดต่อผู้ดูแลระบบ
    st.markdown(
        f"""
        <div class="kys-contact">
          <a href="mailto:{CONTACT_EMAIL}">📧 ติดต่อผู้ดูแลระบบ</a>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 5) Footer – ข้อความเครดิต
    st.markdown(
        """
        <hr style="margin-top:32px;margin-bottom:12px;border:1px solid #e0e6ec;">
        <div style='text-align:center; color:#445b66; font-size:15px;'>
            พัฒนาโดย <b>กลุ่มบริหารงานบุคคล โรงเรียนอนุบาลวัดคลองใหญ่ จังหวัดตราด</b><br>
            เพื่อยกระดับการบริหารจัดการงานบุคคลให้ทันสมัย โปร่งใส และตรวจสอบได้
        </div>
        """,
        unsafe_allow_html=True,
    )



def show_teacher_portal():
    inject_fonts_and_css()
    st.title("พื้นที่สำหรับผู้ใช้ (ครู)")
    st.info("หน้านี้ไว้ต่อยอดฟอร์ม/เมนูย่อยสำหรับครูในอนาคตครับ")


def show_admin_portal():
    inject_fonts_and_css()
    st.title("พื้นที่สำหรับผู้ดูแล")
    st.info("หน้านี้ไว้ต่อยอดเมนูย่อยสำหรับผู้ดูแล/แอดมินในอนาคตครับ")


# ==============================
# App — Sidebar & Routing
# ==============================
def main():
    st.set_page_config(page_title=APP_TITLE, page_icon="🏫", layout="wide")
    with st.sidebar:
        st.markdown("### เมนู")
        st.session_state["menu"] = st.radio(
            "ไปหน้า:",
            ["หน้าแรก", "สำหรับผู้ใช้", "สำหรับผู้ดูแล"],
            index=["หน้าแรก", "สำหรับผู้ใช้", "สำหรับผู้ดูแล"].index(st.session_state["menu"]),
            label_visibility="collapsed",
        )

    if st.session_state["menu"] == "หน้าแรก":
        show_home()
    elif st.session_state["menu"] == "สำหรับผู้ใช้":
        show_teacher_portal()
    else:
        show_admin_portal()


if __name__ == "__main__":
    main()

