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
LOGO_PATH   = os.path.join(ASSETS_DIR, "logo.jpg")

# init session_state
if "menu" not in st.session_state:
    st.session_state["menu"] = "หน้าแรก"
if "route" not in st.session_state:
    st.session_state["route"] = "home"   # เส้นทางย่อย (ใช้สำหรับหน้า login)
if "user" not in st.session_state:
    st.session_state["user"] = None

# ------------------------------
# Auth helpers (load users, check pin)
# ------------------------------
DATA_PATH = "teachers.csv"   # ไฟล์บัญชีผู้ใช้

def load_users():
    """อ่าน users จาก teachers.csv -> DataFrame"""
    try:
        df = pd.read_csv(DATA_PATH, dtype=str).fillna("")
        required = {"teacher_id","name","email","department","pin","role","admin_modules"}
        missing = required - set(df.columns)
        if missing:
            st.error(f"teachers.csv ไม่มีคอลัมน์: {', '.join(missing)}")
        return df
    except Exception as e:
        st.error(f"อ่านไฟล์ users ไม่ได้: {e}")
        return pd.DataFrame(columns=["teacher_id","name","email","department","pin","role","admin_modules"])

def get_user(tid: str):
    df = load_users()
    m = df[df["teacher_id"].astype(str).str.strip() == str(tid).strip()]
    return m.iloc[0].to_dict() if not m.empty else None

def check_login(tid: str, pin: str):
    """คืน (bool,user_dict|None, error_text|None)"""
    if not tid or not pin:
        return False, None, "กรุณากรอกให้ครบ"

    u = get_user(tid)
    if not u:
        return False, None, "ไม่พบรหัสผู้ใช้"
    if str(u["pin"]).strip() != str(pin).strip():
        return False, None, "PIN ไม่ถูกต้อง"
    return True, u, None

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

          /* Title */
          .kys-title h1{ margin:0; font-size: clamp(28px, 2.6vw, 38px); color: var(--brand); font-weight:800; }
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

          .kys-btn{ display:inline-flex; align-items:center; justify-content:center; gap:8px; padding:12px 16px; border-radius:12px; background:var(--brand); color:#fff !important; text-decoration:none !important; box-shadow:var(--shadow); margin-top:14px; min-height:48px; }
          .kys-btn:hover{ filter:brightness(1.06); }

          .kys-contact{ width:100%; display:flex; justify-content:flex-end; margin-top:18px; }
          .kys-contact a{ display:inline-flex; align-items:center; gap:8px; padding: 10px 14px; border-radius: 999px; background: #0f2748; color: #fff !important; text-decoration:none; box-shadow: var(--shadow); }
        </style>
        """,
        unsafe_allow_html=True,
    )

# ==============================
# Login page (new)
# ==============================
def show_login(required_role: str):
    """
    required_role: 'teacher' | 'module_admin' | 'superadmin'
    """
    inject_fonts_and_css()

    role_name = {
        "teacher": "ครูผู้สอน (Teacher)",
        "module_admin": "ผู้ดูแลโมดูล (Module Admin)",
        "superadmin": "แอดมินใหญ่ (Superadmin)",
    }[required_role]

    st.title(f"เข้าสู่ระบบ — {role_name}")

    with st.form(f"login_form_{required_role}", clear_on_submit=False):
        tid = st.text_input("User ID / Teacher ID")
        pin = st.text_input("PIN", type="password")
        submit = st.form_submit_button("เข้าสู่ระบบ")

    if submit:
        ok, u, err = check_login(tid, pin)
        if not ok:
            st.error(err)
            return

        allowed = {
            "teacher": ["teacher", "module_admin", "superadmin"],
            "module_admin": ["module_admin", "superadmin"],
            "superadmin": ["superadmin"],
        }[required_role]

        user_role = u.get("role", "").strip().lower()
        if user_role not in allowed:
            st.error("สิทธิ์ไม่เพียงพอสำหรับเมนูนี้")
            return

        st.success(f"ยินดีต้อนรับคุณ {u.get('name','')}")
        st.session_state["user"] = u

        # นำทางไปหน้าเหมาะสม
        if required_role == "teacher":
            st.session_state["menu"] = "สำหรับผู้ใช้"
        else:
            st.session_state["menu"] = "สำหรับผู้ดูแล"

        st.session_state["route"] = "home"
        st.rerun()

    if st.button("← กลับหน้าแรก"):
        st.session_state["route"] = "home"
        st.rerun()

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

    # 2) Title + Subtitle
    st.markdown(
        f"""
        <div class="kys-title" style="text-align:center; margin-top:10px;">
          <h1>{APP_TITLE}</h1>
          <p style="color:{BRAND_MUTED}; font-size:18px;">
            ช่วยให้ครูและบุคลากรทางการศึกษาจัดการข้อมูลส่วนบุคคลได้ง่าย โปร่งใส และตรวจสอบได้
          </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 3) การ์ด 3 ใบ (ใช้ปุ่มพาไปหน้า Login)
    col1, col2, col3 = st.columns(3, gap="large")

    with col1:
        st.markdown(
            """
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
            """,
            unsafe_allow_html=True,
        )
        if st.button("🔐 ไปหน้าเข้าสู่ระบบครู", key="to_login_teacher"):
            st.session_state["route"] = "login_teacher"
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        st.markdown(
            """
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
            """,
            unsafe_allow_html=True,
        )
        if st.button("🔐 ไปหน้าเข้าสู่ระบบผู้ดูแลโมดูล", key="to_login_module"):
            st.session_state["route"] = "login_module_admin"
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    with col3:
        st.markdown(
            """
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
            """,
            unsafe_allow_html=True,
        )
        if st.button("🔐 ไปหน้าเข้าสู่ระบบแอดมินใหญ่", key="to_login_super"):
            st.session_state["route"] = "login_superadmin"
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

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

    # ✅ ตรวจ route ย่อยก่อน (แสดงหน้า login เฉพาะทาง)
    route = st.session_state.get("route", "home")
    if route == "login_teacher":
        show_login("teacher"); return
    elif route == "login_module_admin":
        show_login("module_admin"); return
    elif route == "login_superadmin":
        show_login("superadmin"); return

    # Sidebar / เมนูหลัก
    with st.sidebar:
        st.markdown("### เมนู")
        st.session_state["menu"] = st.radio(
            "ไปหน้า:",
            ["หน้าแรก", "สำหรับผู้ใช้", "สำหรับผู้ดูแล"],
            index=["หน้าแรก", "สำหรับผู้ใช้", "สำหรับผู้ดูแล"].index(st.session_state["menu"]),
            label_visibility="collapsed",
        )

    # Routing หลัก
    if st.session_state["menu"] == "หน้าแรก":
        show_home()
    elif st.session_state["menu"] == "สำหรับผู้ใช้":
        show_teacher_portal()
    else:
        show_admin_portal()

if __name__ == "__main__":
    main()

