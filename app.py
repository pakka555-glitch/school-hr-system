# app.py
import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

# =============== หน้าเว็บ ===============
st.set_page_config(page_title="School HR System", page_icon="🏫", layout="wide")

# =============== CSS/Fonts ===============
def inject_css():
    st.markdown(
        """
        <style>
          @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+Thai:wght@300;400;600;700&display=swap');
          html, body, [class*="css"] { font-family: 'Noto Sans Thai', sans-serif; }

          :root{
            --brand:#0a2342;
            --muted:#445b66;
            --soft:#f5f8fb;
            --shadow: 0 10px 30px rgba(10,35,66,0.10);
            --radius: 16px;
          }

          .kys-title{
            text-align:center;
            color:var(--brand);
            margin: 6px 0 2px 0;
            font-weight:800;
          }
          .kys-sub{
            text-align:center;
            color:var(--muted);
            margin: 0 0 22px 0;
            font-size: 15px;
          }

          /* การ์ด (ใช้ container ของคอลัมน์) */
          .kys-card{
            background:#fff;
            border-radius:var(--radius);
            box-shadow:var(--shadow);
            padding:18px 18px 14px 18px;
            height: 220px; /* ความสูงเท่ากันทุกใบ → ปุ่มจะเรียงบรรทัดเดียว */
            display:flex;
            flex-direction:column;
            justify-content:flex-start;
          }
          .kys-card h3{ margin:4px 0 10px 0; color:var(--brand); font-weight:800; }
          .kys-card ul{ margin:6px 0 0 18px; color:#314657; line-height:1.55; }

          /* ปุ่ม Streamlit */
          .stButton>button{
            background:#0f57c7 !important;
            color:#fff !important;
            border-radius:12px !important;
            padding:10px 14px !important;
            box-shadow:var(--shadow) !important;
            border:0 !important;
          }
          .stButton>button:hover{ filter:brightness(1.06); }

          /* ให้ปุ่มเต็มความกว้าง */
          .kys-btn-box .stButton>button{ width:100% !important; }

          /* เครดิตด้านล่าง */
          .kys-footer{
            text-align:center; color:#5b6b7a; font-size:13px;
            margin-top: 12px;
          }
          .kys-hr{ margin-top: 8px; margin-bottom: 10px; border:0; border-top:1px solid #e7edf3; }
        </style>
        """,
        unsafe_allow_html=True,
    )

inject_css()

# =============== Google Sheets ===============
@st.cache_resource(show_spinner=False)
def get_gs_client():
    info = dict(st.secrets["gcp_service_account"])
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive.readonly",
    ]
    creds = Credentials.from_service_account_info(info, scopes=scopes)
    return gspread.authorize(creds)

@st.cache_data(ttl=60)
def load_users_df():
    """โหลดข้อมูลผู้ใช้จาก Google Sheets"""
    try:
        client = get_gs_client()
        sheet_id = st.secrets["gsheets"]["users_sheet_id"]
        ws_name = st.secrets["gsheets"]["users_worksheet"]
        sh = client.open_by_key(sheet_id)
        ws = sh.worksheet(ws_name)
        data = ws.get_all_records()
        df = pd.DataFrame(data).fillna("")
        if "teacher_id" in df: df["teacher_id"] = df["teacher_id"].astype(str).str.strip()
        if "pin" in df: df["pin"] = df["pin"].astype(str).str.strip()
        if "role" in df: df["role"] = df["role"].astype(str).str.lower().str.strip()
        return df
    except Exception as e:
        st.error(f"ไม่สามารถโหลดข้อมูลผู้ใช้ได้: {e}")
        return pd.DataFrame(columns=["teacher_id", "name", "email", "role", "pin"])

def check_login(user_id, pin, allowed_roles):
    df = load_users_df()
    user = df[df["teacher_id"] == str(user_id).strip()]
    if user.empty:
        return False, None, "❌ ไม่พบผู้ใช้"
    u = user.iloc[0]
    if str(u["pin"]) != str(pin).strip():
        return False, None, "🔒 PIN ไม่ถูกต้อง"
    if allowed_roles and u["role"] not in allowed_roles:
        return False, None, "🚫 ไม่มีสิทธิ์เข้าหน้านี้"
    return True, u, None

# =============== Footer (กันซ้ำ) ===============
def render_footer():
    if st.session_state.get("_footer_rendered"):  # กันซ้ำ
        return
    st.session_state["_footer_rendered"] = True
    st.markdown("<hr class='kys-hr'/>", unsafe_allow_html=True)
    st.markdown(
        """
        <div class="kys-footer">
          พัฒนาโดย <b>ครูสุพจน์ บ้านกวักดอก</b> โรงเรียนอนุบาลวัดคลองใหญ่ จังหวัดตราด<br/>
          School HR System v2 | Powered by Streamlit + Google Sheets
        </div>
        """,
        unsafe_allow_html=True,
    )

# =============== Routing ===============
if "route" not in st.session_state:
    st.session_state["route"] = "home"

# =============== หน้า Home ===============
def page_home():
    st.markdown("<h2 class='kys-title'>ระบบบริหารงานบุคคลโรงเรียนอนุบาลวัดคลองใหญ่</h2>", unsafe_allow_html=True)
    st.markdown(
        "<div class='kys-sub'>ช่วยให้ครูและบุคลากรทางการศึกษาจัดการข้อมูลบุคคลง่าย โปร่งใส และตรวจสอบได้</div>",
        unsafe_allow_html=True,
    )

    c1, c2, c3, c4 = st.columns(4, gap="large")

    # --- Card 1: Teacher ---
    with c1:
        st.markdown("<div class='kys-card'>"
                    "<h3>👩‍🏫 สำหรับครูผู้สอน</h3>"
                    "<ul>"
                    "<li>จัดการ/ปรับปรุงข้อมูลส่วนบุคคล</li>"
                    "<li>ส่งคำขอลา/อบรม</li>"
                    "<li>อัปโหลดเอกสาร</li>"
                    "</ul>"
                    "</div>", unsafe_allow_html=True)
        st.container().markdown("", unsafe_allow_html=True)  # no-op
        with st.container():  # กล่องปุ่ม (เต็มกว้างเท่า ๆ กัน)
            st.markdown("<div class='kys-btn-box'>", unsafe_allow_html=True)
            if st.button("🔐 เข้าสู่ระบบครูผู้สอน", use_container_width=True, key="btn_t"):
                st.session_state["route"] = "login_teacher"
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

    # --- Card 2: Module Admin ---
    with c2:
        st.markdown("<div class='kys-card'>"
                    "<h3>⚙️ ผู้ดูแลโมดูล</h3>"
                    "<ul>"
                    "<li>ตรวจสอบ/อนุมัติคำขอในโมดูล</li>"
                    "<li>สถิติและรายงานในโมดูล</li>"
                    "</ul>"
                    "</div>", unsafe_allow_html=True)
        with st.container():
            st.markdown("<div class='kys-btn-box'>", unsafe_allow_html=True)
            if st.button("🔐 เข้าสู่ระบบผู้ดูแลโมดูล", use_container_width=True, key="btn_m"):
                st.session_state["route"] = "login_module_admin"
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

    # --- Card 3: Superadmin ---
    with c3:
        st.markdown("<div class='kys-card'>"
                    "<h3>🛡️ แอดมินใหญ่</h3>"
                    "<ul>"
                    "<li>จัดการสิทธิ์เข้าระบบ</li>"
                    "<li>ออกรายงานรวมเพื่อบริหาร</li>"
                    "</ul>"
                    "</div>", unsafe_allow_html=True)
        with st.container():
            st.markdown("<div class='kys-btn-box'>", unsafe_allow_html=True)
            if st.button("🔐 เข้าสู่ระบบแอดมินใหญ่", use_container_width=True, key="btn_s"):
                st.session_state["route"] = "login_superadmin"
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

    # --- Card 4: Executive ---
    with c4:
        st.markdown("<div class='kys-card'>"
                    "<h3>🏫 ฝ่ายบริหาร (Executive)</h3>"
                    "<ul>"
                    "<li>สำหรับผู้บริหารโรงเรียน</li>"
                    "<li>ดูรายงานภาพรวมทั้งหมด</li>"
                    "</ul>"
                    "</div>", unsafe_allow_html=True)
        with st.container():
            st.markdown("<div class='kys-btn-box'>", unsafe_allow_html=True)
            if st.button("🔐 เข้าสู่ระบบฝ่ายบริหาร", use_container_width=True, key="btn_e"):
                st.session_state["route"] = "login_executive"
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

    render_footer()

# =============== หน้า Login (รวม 4 บทบาท) ===============
def login_page(title, roles, next_route):
    st.markdown(f"<h3 class='kys-title' style='margin-bottom:12px'>{title}</h3>", unsafe_allow_html=True)
    with st.form("login_form"):
        uid = st.text_input("User ID / Teacher ID")
        pin = st.text_input("PIN", type="password")
        ok = st.form_submit_button("เข้าสู่ระบบ")
        if ok:
            success, user, err = check_login(uid, pin, roles)
            if not success:
                st.error(err)
            else:
                st.success(f"ยินดีต้อนรับคุณ {user.get('name','')}")
                st.session_state["user"] = dict(user)
                st.session_state["route"] = next_route
                st.rerun()
    st.button("⬅️ กลับหน้าหลัก", on_click=lambda: st.session_state.update({"route": "home"}))
    render_footer()

# =============== Portal ตัวอย่าง (คงของเดิม) ===============
def teacher_portal():
    st.success("เข้าสู่ระบบในบทบาท: ครูผู้สอน")
    st.info("หน้านี้ไว้ต่อยอดฟอร์ม/เมนูย่อยของครู")
    st.button("ออกจากระบบ", on_click=lambda: st.session_state.update({"route": "home"}))
    render_footer()

def module_portal():
    st.success("เข้าสู่ระบบในบทบาท: ผู้ดูแลโมดูล")
    st.info("หน้านี้ไว้ต่อยอดเมนูสำหรับผู้ดูแลโมดูล")
    st.button("ออกจากระบบ", on_click=lambda: st.session_state.update({"route": "home"}))
    render_footer()

def superadmin_portal():
    st.success("เข้าสู่ระบบในบทบาท: แอดมินใหญ่")
    st.info("หน้านี้ไว้ต่อยอดเมนูสำหรับแอดมินใหญ่")
    st.button("ออกจากระบบ", on_click=lambda: st.session_state.update({"route": "home"}))
    render_footer()

def executive_portal():
    st.success("เข้าสู่ระบบในบทบาท: ฝ่ายบริหาร (Executive)")
    st.info("หน้านี้ไว้ต่อยอดรายงานภาพรวมสำหรับผู้บริหาร")
    st.button("ออกจากระบบ", on_click=lambda: st.session_state.update({"route": "home"}))
    render_footer()

# =============== Route Controller ===============
def main():
    route = st.session_state.get("route", "home")
    if route == "home":
        page_home()
    elif route == "login_teacher":
        login_page("👩‍🏫 เข้าสู่ระบบครูผู้สอน", ["teacher", "module_admin", "superadmin"], "teacher_portal")
    elif route == "login_module_admin":
        login_page("⚙️ เข้าสู่ระบบผู้ดูแลโมดูล", ["module_admin", "superadmin"], "module_portal")
    elif route == "login_superadmin":
        login_page("🛡️ เข้าสู่ระบบแอดมินใหญ่", ["superadmin"], "superadmin_portal")
    elif route == "login_executive":
        login_page("🏫 เข้าสู่ระบบฝ่ายบริหาร (Executive)", ["executive", "superadmin"], "executive_portal")
    elif route == "teacher_portal":
        teacher_portal()
    elif route == "module_portal":
        module_portal()
    elif route == "superadmin_portal":
        superadmin_portal()
    elif route == "executive_portal":
        executive_portal()

if __name__ == "__main__":
    main()
