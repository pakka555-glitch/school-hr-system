import streamlit as st
import os

# -----------------------------
# Settings
# -----------------------------
APP_TITLE = "ระบบบริหารงานบุคคลโรงเรียนอนุบาลวัดคลองใหญ่"
CONTACT_EMAIL = "pakka555@gmail.com"
BRAND_PRIMARY = "#0a2342"  # น้ำเงินกรม
BRAND_MUTED = "#445b66"    # เทาเขียวอมฟ้า

# -----------------------------
# Helper: CSS
# -----------------------------
def inject_fonts_and_css():
    st.markdown(
        f"""
        <style>
            :root {{
                --brand: {BRAND_PRIMARY};
                --muted: {BRAND_MUTED};
                --card-radius: 16px;
            }}

            /* ---------- Base / Background ---------- */
            html, body, [class*="css"] {{
                font-family: 'Noto Sans Thai', system-ui, -apple-system, Segoe UI, Arial, sans-serif;
                color: #14202e;
            }}

            /* พื้นหลังโทนอ่อน + ลายบาง ๆ */
            body {{
                background:
                  radial-gradient(60rem 60rem at 120% -10%, #f3f8ff 0%, transparent 60%),
                  radial-gradient(50rem 50rem at -10% 120%, #f7fbff 0%, transparent 55%),
                  linear-gradient(180deg, #f9fcff 0%, #f7fbff 60%, #f6faff 100%);
            }}
            /* layer ลายจุดบาง ๆ */
            .stApp::before {{
                content: "";
                position: fixed;
                inset: 0;
                pointer-events: none;
                background-image: radial-gradient(rgba(10,35,66,.05) 1px, transparent 1px);
                background-size: 10px 10px;
                opacity: .35;
                z-index: 0;
            }}

            /* Layout */
            .block-container {{
                max-width: 1280px;
                padding-top: 1rem !important;
                padding-bottom: 1.25rem !important;
                position: relative;
                z-index: 1; /* ให้อยู่เหนือพื้นหลังลายจุด */
            }}

            /* ---------- Hero / Banner & Logo ---------- */
            .kys-hero img {{
                width: 100%;
                height: auto;
                border-radius: var(--card-radius);
                box-shadow: 0 10px 30px rgba(10,35,66,.18);
            }}
            .kys-logo img {{
                width: 120px;
                height: auto;
                border-radius: 14px;
                box-shadow: 0 12px 26px rgba(10,35,66,.15);
                border: 6px solid #fff;
            }}

            /* ---------- Cards Grid ---------- */
            .kys-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 1.5rem;
                margin-top: 2rem;
            }}
            .kys-card {{
                background: #fff;
                border: 1px solid #eaf0f6;
                border-radius: var(--card-radius);
                padding: 22px;
                display: flex;
                flex-direction: column;
                justify-content: space-between;
                height: 100%;
                box-shadow: 0 6px 16px rgba(10,35,66,.06);
                transition: transform .18s ease, box-shadow .18s ease;
            }}
            .kys-card:hover {{
                transform: translateY(-2px);
                box-shadow: 0 12px 28px rgba(10,35,66,.12);
            }}
            .kys-card h3 {{
                margin: 0 0 6px 0;
                color: var(--brand);
                font-weight: 800;
            }}
            .kys-card h4 {{
                margin: 0 0 8px 0;
                color: #0e2a47;
                font-weight: 700;
            }}
            .kys-card ul {{
                margin: 0 0 14px 18px;
            }}

            /* ---------- Buttons ---------- */
            .kys-btn {{
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
                box-shadow: 0 8px 18px rgba(10,35,66,.22);
                font-weight: 700;
            }}
            .kys-btn:hover {{ filter: brightness(1.08); }}

            /* ปุ่มติดต่อผู้ดูแลระบบ (ขวาล่าง) */
            .kys-contact {{
                display: flex;
                justify-content: flex-end;
                margin-top: 26px;
            }}

            /* Title ใต้โลโก้ */
            .kys-title h2 {{
                margin: .25rem 0 .15rem 0;
                font-weight: 800;
            }}
            .kys-sub {{
                color: var(--muted);
                margin-top: .15rem;
            }}
        </style>
        """,
        unsafe_allow_html=True,
    )

# -----------------------------
# หน้าแรก
# -----------------------------
def show_home():
    inject_fonts_and_css()

    # Banner (Hero)
    banner_path = "assets/banner.jpg"
    if os.path.exists(banner_path):
        st.markdown('<div class="kys-hero">', unsafe_allow_html=True)
        st.image(banner_path, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # Logo + Title
    col1, col2 = st.columns([1, 4])
    with col1:
        logo_path = "assets/logo.jpg"
        if os.path.exists(logo_path):
            st.markdown(
                f'<div class="kys-logo"><img src="{logo_path}" alt="logo"></div>',
                unsafe_allow_html=True,
            )
    with col2:
        st.markdown(f'<div class="kys-title"><h2>{APP_TITLE}</h2></div>', unsafe_allow_html=True)
        st.markdown('<div class="kys-sub">ช่วยให้ครูและบุคลากรจัดการข้อมูลบุคคลได้อย่างมีระบบ โปร่งใส และตรวจสอบได้</div>',
                    unsafe_allow_html=True)

    st.markdown("---")

   # Grid 3 การ์ด (ปุ่มบรรทัดเดียวเท่ากัน)
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

    # ปุ่มติดต่อผู้ดูแลระบบ (ขวาล่าง)
    st.markdown(
        f"""
        <div class="kys-contact">
            <a class="kys-btn" href="mailto:{CONTACT_EMAIL}">✉️ ติดต่อผู้ดูแลระบบ</a>
        </div>
        """,
        unsafe_allow_html=True,
    )

# -----------------------------
# Sidebar
# -----------------------------
with st.sidebar:
    st.markdown("### เมนู")
    page = st.radio("ไปหน้า:", ["หน้าแรก", "สำหรับผู้ใช้", "สำหรับผู้ดูแล"])

if page == "หน้าแรก":
    show_home()
elif page == "สำหรับผู้ใช้":
    st.info("หน้าสำหรับผู้ใช้ (อยู่ระหว่างพัฒนา)")
else:
    st.info("หน้าสำหรับผู้ดูแลระบบ (อยู่ระหว่างพัฒนา)")
