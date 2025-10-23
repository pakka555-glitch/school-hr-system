# app.py
import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

# ========= Site =========
st.set_page_config(page_title="School HR System", page_icon="🏫", layout="wide")
CONTACT_EMAIL = st.secrets.get("contact_email", "pakka555@gmail.com")

# ========= CSS / Fonts =========
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
            --shadow:0 10px 30px rgba(10,35,66,.10);
            --radius:14px;
          }

          .page-wrap{ max-width: 1080px; margin: 0 auto; }
          .kys-title{
            text-align:center; color:var(--brand);
            font-weight:800; margin: 8px 0 6px 0;
          }
          .kys-sub{
            text-align:center; color:var(--muted); font-size:14.5px;
            margin-bottom: 18px;
          }

          /* ====== CARD (แนวตั้ง) ====== */
          .kys-card{
            background:#fff; border-radius:var(--radius); box-shadow:var(--shadow);
            padding:18px 18px 12px 18px; margin-bottom: 14px;
          }
          .kys-card h3{ margin:0 0 6px 0; font-weight:800; color:var(--brand); }
          .kys-card h4{ margin:0 0 8px 0; font-weight:600; color:var(--muted); }
          .kys-card ul{ margin:6px 0 0 18px; line-height:1.55; color:#2f4759; }
          .kys-card .btn-row{ margin-top:12px; }

          /* streamlit button */
          .stButton>button{
            width:100% !important;
            background:#0f57c7 !important; color:#fff !important;
            border-radius:12px !important; padding:10px 12px !important;
            border:0 !important; box-shadow:var(--shadow) !important;
          }
          .stButton>button:hover{ filter:brightness(1.06); }

          /* ติดต่อผู้ดูแล */
          .kys-contact-wrap{
            width:100%; display:flex; justify-content:flex-end; margin: 6px 0 10px 0;
          }
          .kys-contact{
            display:inline-flex; align-items:center; gap:8px; padding:9px 14px;
            background:#0f2748; color:#fff; border-radius:999px;
            text-decoration:none; box-shadow:var(--shadow);
            font-size:14px;
          }

          /* footer */
          .kys-hr{ margin: 12px 0 8px 0; border:0; border-top:1px solid #e9eff5; }
          .kys-footer{ text-align:center; color:#5b6b7a; font-size:13px; }
        </style>
        """,
        unsafe_allow_html=True,
    )

inject_css()

# ========= Google Sheets =========
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
    try:
        client = get_gs_client()
        sheet_id = st.secrets["gsheets"]["users_sheet_id"]
        ws_name = st.secrets["gsheets"]["users_worksheet"]
        sh = client.open_by_key(sheet_id)
        ws = sh.worksheet(ws_name)
        data = ws.get_all_records()
        df = pd.DataFrame(data).fillna("")
        for col in ("teacher_id","pin","role"):
            if col in df: df[col] = df[col].astype(str).str.strip()
        if "role" in df: df["role"] = df["role"].str.lower()
        return df
    except Exception as e:
        st.error(f"ไม่สามารถโหลดข้อมูลผู้ใช้ได้: {e}")
        return pd.DataFrame(columns=["teacher_id","name","email","role","pin"])

def check_login(uid, pin, allowed_roles):
    df = load_users_df()
    user = df[df["teacher_id"] == str(uid).strip()]
    if user.empty:
        return False, None, "❌ ไม่พบผู้ใช้"
    u = user.iloc[0]
    if str(u["pin"]) != str(pin).strip():
        return False, None, "🔒 PIN ไม่ถูกต้อง"
    if allowed_roles and u["role"] not in allowed_roles:
        return False, None, "🚫 ไม่มีสิทธิ์เข้าหน้านี้"
    return True, u, None

# ========= State =========
if "route" not in st.session_state:
    st.session_state["route"] = "home"

def footer_once():
    if st.session_state.get("_footer_done"): return
    st.session_state["_footer_done"] = True
    st.markdown("<hr class='kys-hr'/>", unsafe_allow_html=True)
    st.markdown(
        """
        <div class="kys-footer">
          พัฒนาโดย <b>ครูสุพจน์ นามโคตร</b> กลุ่มบริหารงานบุคคล โรงเรียนอนุบาลวัดคลองใหญ่ จังหวัดตราด<br/>
          School HR System v2 | Powered by Streamlit + Google Sheets
        </div>
        """, unsafe_allow_html=True
    )

# ========= UI Blocks =========
def role_card(title, subtitle, items, button_key, route_name):
    with st.container():
        st.markdown("<div class='kys-card'>", unsafe_allow_html=True)
        st.markdown(f"<h3>{title}</h3>", unsafe_allow_html=True)
        if subtitle:
            st.markdown(f"<h4>{subtitle}</h4>", unsafe_allow_html=True)
        if items:
            st.markdown("<ul>" + "".join([f"<li>{i}</li>" for i in items]) + "</ul>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        # ปุ่มเต็มความกว้าง
        st.markdown("<div class='btn-row'>", unsafe_allow_html=True)
        if st.button("🔐 เข้าสู่ระบบ", key=button_key, use_container_width=True):
            st.session_state["route"] = route_name
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

def contact_block():
    st.markdown(
        f"""
        <div class="kys-contact-wrap">
          <a class="kys-contact" href="mailto:{CONTACT_EMAIL}">📧 ติดต่อผู้ดูแลระบบ</a>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ========= Pages =========
def page_home():
    st.markdown("<div class='page-wrap'>", unsafe_allow_html=True)
    st.markdown("<h2 class='kys-title'>ระบบบริหารงานบุคคลโรงเรียนอนุบาลวัดคลองใหญ่</h2>", unsafe_allow_html=True)
    st.markdown("<div class='kys-sub'>ช่วยให้ครูและบุคลากรทางการศึกษาจัดการข้อมูลบุคคลง่าย โปร่งใส และตรวจสอบได้</div>", unsafe_allow_html=True)

    # การ์ด 4 ใบ (แนวตั้งตามภาพ)
    role_card(
        title="👩‍🏫 สำหรับครูผู้สอน",
        subtitle="Teacher",
        items=[
            "จัดการ/ปรับปรุงข้อมูลส่วนบุคคล",
            "ส่งคำขอลา/ไปราชการ/อบรม ฯลฯ และตรวจสอบสถานะ",
            "อัปโหลดเอกสารงานบุคคล (ฟอร์ม/ใบอนุญาต/แฟ้มสะสมงาน)"
        ],
        button_key="go_teacher_login",
        route_name="login_teacher"
    )

    role_card(
        title="⚙️ ผู้ดูแลโมดูล",
        subtitle="Module Admin",
        items=[
            "ตรวจสอบ/อนุมัติคำขอในโมดูลที่รับผิดชอบ",
            "ติดตามเอกสาร ปรับแก้ข้อมูลที่จำเป็น",
            "ดูสรุปสถิติและรายงานในโมดูล"
        ],
        button_key="go_module_admin_login",
        route_name="login_module_admin"
    )

    role_card(
        title="🛡️ แอดมินใหญ่",
        subtitle="Superadmin",
        items=[
            "กำกับดูแลภาพรวมของระบบทั้งหมด",
            "จัดการข้อมูลบุคลากร/สิทธิ์การเข้าใช้",
            "ออกรายงานภาพรวมเพื่อการบริหาร"
        ],
        button_key="go_superadmin_login",
        route_name="login_superadmin"
    )

    role_card(
        title="🏫 ฝ่ายบริหาร (Executive)",
        subtitle="Executive",
        items=[
            "สำหรับผู้บริหารโรงเรียน",
            "ดูรายงานภาพรวมทั้งหมด"
        ],
        button_key="go_exec_login",
        route_name="login_executive"
    )

    contact_block()
    footer_once()
    st.markdown("</div>", unsafe_allow_html=True)  # page-wrap

def login_page(title, roles, next_route):
    st.markdown("<div class='page-wrap'>", unsafe_allow_html=True)
    st.markdown(f"<h3 class='kys-title' style='margin-bottom:10px'>{title}</h3>", unsafe_allow_html=True)
    with st.form("login_form"):
        uid = st.text_input("User ID / Teacher ID")
        pin = st.text_input("PIN", type="password")
        if st.form_submit_button("เข้าสู่ระบบ"):
            ok, user, err = check_login(uid, pin, roles)
            if not ok:
                st.error(err)
            else:
                st.success(f"ยินดีต้อนรับคุณ {user.get('name','')}")
                st.session_state["user"] = dict(user)
                st.session_state["route"] = next_route
                st.rerun()
    st.button("⬅️ กลับหน้าหลัก", on_click=lambda: st.session_state.update({"route":"home"}))
    footer_once()
    st.markdown("</div>", unsafe_allow_html=True)

def teacher_portal():
    st.markdown("<div class='page-wrap'>", unsafe_allow_html=True)
    st.success("เข้าสู่ระบบในบทบาท: ครูผู้สอน")
    st.info("หน้าตัวอย่างสำหรับต่อยอดเมนูของครู")
    st.button("ออกจากระบบ", on_click=lambda: st.session_state.update({"route":"home"}))
    footer_once()
    st.markdown("</div>", unsafe_allow_html=True)

def module_portal():
    st.markdown("<div class='page-wrap'>", unsafe_allow_html=True)
    st.success("เข้าสู่ระบบในบทบาท: ผู้ดูแลโมดูล")
    st.info("หน้าตัวอย่างสำหรับต่อยอดเมนูของผู้ดูแลโมดูล")
    st.button("ออกจากระบบ", on_click=lambda: st.session_state.update({"route":"home"}))
    footer_once()
    st.markdown("</div>", unsafe_allow_html=True)

def superadmin_portal():
    st.markdown("<div class='page-wrap'>", unsafe_allow_html=True)
    st.success("เข้าสู่ระบบในบทบาท: แอดมินใหญ่")
    st.info("หน้าตัวอย่างสำหรับต่อยอดเมนูของแอดมินใหญ่")
    st.button("ออกจากระบบ", on_click=lambda: st.session_state.update({"route":"home"}))
    footer_once()
    st.markdown("</div>", unsafe_allow_html=True)

def executive_portal():
    st.markdown("<div class='page-wrap'>", unsafe_allow_html=True)
    st.success("เข้าสู่ระบบในบทบาท: ฝ่ายบริหาร (Executive)")
    st.info("หน้าตัวอย่างสำหรับต่อยอดรายงานภาพรวม")
    st.button("ออกจากระบบ", on_click=lambda: st.session_state.update({"route":"home"}))
    footer_once()
    st.markdown("</div>", unsafe_allow_html=True)

# ========= Router =========
def main():
    r = st.session_state.get("route","home")
    if r == "home":
        page_home()
    elif r == "login_teacher":
        login_page("👩‍🏫 เข้าสู่ระบบครูผู้สอน", ["teacher","module_admin","superadmin"], "teacher_portal")
    elif r == "login_module_admin":
        login_page("⚙️ เข้าสู่ระบบผู้ดูแลโมดูล", ["module_admin","superadmin"], "module_portal")
    elif r == "login_superadmin":
        login_page("🛡️ เข้าสู่ระบบแอดมินใหญ่", ["superadmin"], "superadmin_portal")
    elif r == "login_executive":
        login_page("🏫 เข้าสู่ระบบฝ่ายบริหาร (Executive)", ["executive","superadmin"], "executive_portal")
    elif r == "teacher_portal":
        teacher_portal()
    elif r == "module_portal":
        module_portal()
    elif r == "superadmin_portal":
        superadmin_portal()
    elif r == "executive_portal":
        executive_portal()

if __name__ == "__main__":
    main()
