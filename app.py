# app.py
# =========================================================
# School HR System — Streamlit + Google Sheets (RBAC)
# =========================================================

import os
import base64
import json
import textwrap

import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials


# ======================
# ตั้งค่าหน้าเว็บ
# ======================
st.set_page_config(page_title="School HR System", page_icon="🏫", layout="wide")

# --- ใช้ไฟล์รูปภายในโปรเจกต์ ---
ASSETS_DIR  = os.path.join(os.path.dirname(__file__), "assets")
BANNER_PATH = os.path.join(ASSETS_DIR, "banner.jpg")
LOGO_PATH   = os.path.join(ASSETS_DIR, "logo.jpg")


# ======================
# Utilities (Banner/Logo)
# ======================
def _img_to_data_uri(path: str) -> str:
    """อ่านรูปจากไฟล์และแปลงเป็น data URI (base64) สำหรับใช้ใน <img>"""
    try:
        with open(path, "rb") as f:
            encoded = base64.b64encode(f.read()).decode("utf-8")
        ext = os.path.splitext(path)[1].lower().replace(".", "")
        if ext in {"jpg", "jpeg"}:
            mime = "image/jpeg"
        elif ext == "png":
            mime = "image/png"
        else:
            mime = "image/jpeg"
        return f"data:{mime};base64,{encoded}"
    except Exception:
        return ""


def show_banner():
    """แสดงแบนเนอร์จาก assets พร้อมโลโก้และข้อความซ้อนบนรูป"""
    banner_uri = _img_to_data_uri(BANNER_PATH)
    logo_uri   = _img_to_data_uri(LOGO_PATH)

    if not banner_uri:
        st.warning("⚠️ ไม่พบไฟล์แบนเนอร์ (assets/banner.jpg)")
        return

    st.markdown(
        f"""
        <div class="hero">
          <img class="hero-img" src="{banner_uri}" alt="banner"/>
          {"<img class='hero-logo' src='"+logo_uri+"' alt='logo'/>" if logo_uri else ""}
          <div class="hero-title">โรงเรียนอนุบาลวัดคลองใหญ่ จังหวัดตราด</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ======================
# CSS / Fonts
# ======================
def inject_css():
    st.markdown("""
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
          .kys-title{ text-align:center; color:var(--brand); font-weight:800; margin: 12px 0 6px 0; }
          .kys-sub{ text-align:center; color:var(--muted); font-size:14.5px; margin-bottom: 18px; }

          /* ==== HERO / Banner ==== */
          .hero{
            position: relative;
            width: 100%;
            border-radius: 12px;
            overflow: hidden;
            box-shadow: var(--shadow);
            margin: 6px 0 14px 0;
          }
          .hero-img{
            width: 100%;
            display: block;
          }
          .hero-logo{
            position: absolute;
            left: 14px;
            top: 14px;
            width: 72px;
            height: auto;
            border-radius: 12px;
            box-shadow: 0 6px 16px rgba(0,0,0,.25);
            background: #fff;
            padding: 6px;
          }
          .hero-title{
            position: absolute;
            left: 50%;
            bottom: 22px;
            transform: translateX(-50%);
            color: #fff;
            font-weight: 800;
            font-size: clamp(18px, 2.2vw, 28px);
            text-shadow: 0 6px 16px rgba(0,0,0,.6);
            background: rgba(0,0,0,.22);
            padding: 8px 14px;
            border-radius: 12px;
          }

          .kys-card{
            background:#fff; border-radius:var(--radius); box-shadow:var(--shadow);
            padding:18px 18px 12px 18px; margin-bottom: 14px;
          }
          .kys-card h3{ margin:0 0 6px 0; font-weight:800; color:var(--brand); }
          .kys-card h4{ margin:0 0 8px 0; font-weight:600; color:var(--muted); }
          .kys-card ul{ margin:6px 0 0 18px; line-height:1.55; color:#2f4759; }
          .kys-card .btn-row{ margin-top:12px; }

          .stButton>button{
            width:100% !important;
            background:#0f57c7 !important; color:#fff !important;
            border-radius:12px !important; padding:10px 12px !important;
            border:0 !important; box-shadow:var(--shadow) !important;
          }
          .stButton>button:hover{ filter:brightness(1.06); }

          .kys-contact-wrap{ width:100%; display:flex; justify-content:flex-end; margin: 6px 0 10px 0; }
          .kys-contact{ display:inline-flex; align-items:center; gap:8px; padding:9px 14px;
            background:#0f2748; color:#fff; border-radius:999px; text-decoration:none;
            box-shadow:var(--shadow); font-size:14px; }

          .kys-hr{ margin: 12px 0 8px 0; border:0; border-top:1px solid #e9eff5; }
          .kys-footer{ text-align:center; color:#5b6b7a; font-size:13px; }
        </style>
    """, unsafe_allow_html=True)

inject_css()


# ======================
# Google Sheets client (robust)
# ======================
@st.cache_resource(show_spinner=False)
def get_gs_client():
    """
    อ่าน service account จาก st.secrets["gcp_service_account"] ให้ได้แน่ ๆ
    รองรับ 3 เคส:
      1) secrets เป็น dict ปกติ
      2) private_key เป็นสตริงที่มี '\n' -> แปลงเป็นบรรทัดจริง
      3) private_key ถูกวางเป็น BASE64 ของ "ทั้งไฟล์ JSON" -> ถอด BASE64 แล้วใช้ JSON ที่ได้แทน
    """
    try:
        raw = st.secrets["gcp_service_account"]

        # กรณี raw เป็นสตริง (บางคนเก็บทั้งไฟล์ JSON เป็นสตริงไว้)
        if isinstance(raw, str):
            # ถ้าดูเหมือน BASE64 ให้ถอดดู
            try:
                decoded = base64.b64decode(raw).decode("utf-8")
                info = json.loads(decoded)
            except Exception:
                # ถ้าไม่ใช่ JSON ก็ถือว่าเป็นรูปแบบผิด
                raise ValueError("gcp_service_account ใน secrets เป็นสตริงที่ไม่ใช่ JSON")
        else:
            info = dict(raw)

        # ถ้า private_key ไม่มี HEAD/TAIL ลองตีความว่าอาจเป็น BASE64 ของทั้ง JSON ถูกวางไว้ในช่องนี้
        pk = str(info.get("private_key", ""))
        if "BEGIN PRIVATE KEY" not in pk:
            try:
                decoded = base64.b64decode(pk).decode("utf-8")
                j = json.loads(decoded)
                if "private_key" in j:
                    info = j
                    pk = j["private_key"]
            except Exception:
                # ไม่เป็นไร เดี๋ยวลอง normalize ต่อไป
                pass

        # ทำให้ \n กลายเป็นบรรทัดจริง และตัดช่องว่างส่วนเกิน
        pk = str(info.get("private_key", ""))
        if "\\n" in pk:
            pk = pk.replace("\\n", "\n")
        info["private_key"] = textwrap.dedent(pk).strip()

        if "BEGIN PRIVATE KEY" not in info["private_key"]:
            raise ValueError("No key could be detected (private_key ไม่มีหัว/ท้าย PEM)")

        scopes = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive.readonly",
        ]
        creds = Credentials.from_service_account_info(info, scopes=scopes)
        return gspread.authorize(creds)

    except Exception as e:
        st.error(f"ไม่สามารถสร้างไคลเอนต์ Google Sheets ได้: {e}")
        raise

@st.cache_data(ttl=60)
def load_users_df() -> pd.DataFrame:
    """
    โหลดข้อมูลผู้ใช้จาก Google Sheets
    secrets.toml ต้องมี:
      [gsheets]
      users_sheet_id   = "YOUR_SHEET_ID"
      users_worksheet  = "users"
    """
    try:
        client   = get_gs_client()
        sheet_id = st.secrets["gsheets"]["users_sheet_id"]
        ws_name  = st.secrets["gsheets"]["users_worksheet"]

        sh = client.open_by_key(sheet_id)
        ws = sh.worksheet(ws_name)

        data = ws.get_all_records()
        df = pd.DataFrame(data).fillna("")

        # ให้แน่ใจว่า type เป็น string ทั้ง 3 คอลัมน์สำคัญ
        for c in ("teacher_id", "pin", "role"):
            if c in df:
                df[c] = df[c].astype(str).str.strip()
        # role เก็บเป็นตัวพิมพ์เล็กไว้เทียบสิทธิ์ง่าย ๆ
        if "role" in df:
            df["role"] = df["role"].str.lower()

        return df
    except Exception as e:
        st.error(f"โหลดผู้ใช้ไม่สำเร็จ: {e}")
        return pd.DataFrame(columns=["teacher_id", "name", "email", "role", "pin"])


def check_login(uid, pin, allowed_roles):
    """
    ตรวจสอบรหัสผ่านและสิทธิ์
    allowed_roles: รายชื่อบทบาทที่อนุญาตให้เข้าหน้านั้น ๆ
    """
    df = load_users_df()
    user = df[df["teacher_id"] == str(uid).strip()]
    if user.empty:
        return False, None, "❌ ไม่พบผู้ใช้"
    u = user.iloc[0]
    if str(u["pin"]) != str(pin).strip():
        return False, None, "🔒 PIN ไม่ถูกต้อง"

    # รองรับทั้ง role เดี่ยว และหลาย role ด้วย comma
    u_roles = [r.strip() for r in str(u["role"]).lower().split(",") if r.strip()]
    if allowed_roles and not any(r in allowed_roles for r in u_roles):
        return False, None, "🚫 ไม่มีสิทธิ์เข้าหน้านี้"

    return True, u, None


# ======================
# Layout Elements
# ======================
def footer_once():
    if st.session_state.get("_footer_done"):
        return
    st.session_state["_footer_done"] = True
    st.markdown("<hr class='kys-hr'/>", unsafe_allow_html=True)
    st.markdown("""
        <div class="kys-footer">
          พัฒนาโดย <b>ครูสุพจน์ บ้านกวักดอก</b> โรงเรียนอนุบาลวัดคลองใหญ่ จังหวัดตราด<br/>
          School HR System v2 | Powered by Streamlit + Google Sheets
        </div>
    """, unsafe_allow_html=True)


def role_card(title, subtitle, items, button_key, route_name):
    st.markdown("<div class='kys-card'>", unsafe_allow_html=True)
    st.markdown(f"<h3>{title}</h3>", unsafe_allow_html=True)
    if subtitle:
        st.markdown(f"<h4>{subtitle}</h4>", unsafe_allow_html=True)
    if items:
        st.markdown("<ul>" + "".join([f"<li>{i}</li>" for i in items]) + "</ul>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    if st.button("🔐 เข้าสู่ระบบ", key=button_key, use_container_width=True):
        st.session_state["route"] = route_name
        st.rerun()


def contact_block():
    st.markdown("""
        <div class="kys-contact-wrap">
          <a class="kys-contact" href="mailto:pakka555@gmail.com">📧 ติดต่อผู้ดูแลระบบ</a>
        </div>
    """, unsafe_allow_html=True)


# ======================
# Pages
# ======================
def page_home():
    show_banner()

    st.markdown("<div class='page-wrap'>", unsafe_allow_html=True)
    st.markdown("<h2 class='kys-title'>ระบบบริหารงานบุคคลโรงเรียนอนุบาลวัดคลองใหญ่</h2>", unsafe_allow_html=True)
    st.markdown("<div class='kys-sub'>ช่วยให้ครูและบุคลากรทางการศึกษาจัดการข้อมูลบุคคลง่าย โปร่งใส และตรวจสอบได้</div>", unsafe_allow_html=True)

    role_card("👩‍🏫 สำหรับครูผู้สอน", "Teacher", [
        "จัดการ/ปรับปรุงข้อมูลส่วนบุคคล",
        "ส่งคำขอลา/ไปราชการ/อบรม ฯลฯ และตรวจสอบสถานะ",
        "อัปโหลดเอกสารงานบุคคล (ฟอร์ม/ใบอนุญาต/แฟ้มสะสมงาน)"
    ], "go_teacher", "login_teacher")

    role_card("⚙️ ผู้ดูแลโมดูล", "Module Admin", [
        "ตรวจสอบ/อนุมัติคำขอในโมดูลที่รับผิดชอบ",
        "ติดตามเอกสาร ปรับแก้ข้อมูลที่จำเป็น",
        "ดูสรุปสถิติและรายงานในโมดูล"
    ], "go_module_admin", "login_module_admin")

    role_card("🛡️ แอดมินใหญ่", "Superadmin", [
        "กำกับดูแลภาพรวมของระบบทั้งหมด",
        "จัดการข้อมูลบุคลากร/สิทธิ์การเข้าใช้",
        "ออกรายงานภาพรวมเพื่อการบริหาร"
    ], "go_superadmin", "login_superadmin")

    role_card("🏫 ฝ่ายบริหาร (Executive)", "Executive", [
        "สำหรับผู้บริหารโรงเรียน",
        "ดูรายงานภาพรวมทั้งหมด"
    ], "go_exec", "login_executive")

    contact_block()
    footer_once()
    st.markdown("</div>", unsafe_allow_html=True)


def login_page(title, roles, next_route):
    st.markdown(f"<h3 class='kys-title'>{title}</h3>", unsafe_allow_html=True)
    with st.form("login_form"):
        uid = st.text_input("User ID / Teacher ID")
        pin = st.text_input("PIN", type="password")
        if st.form_submit_button("เข้าสู่ระบบ"):
            ok, user, err = check_login(uid, pin, [r.lower() for r in roles])
            if not ok:
                st.error(err)
            else:
                st.success(f"ยินดีต้อนรับคุณ {user.get('name','')}")
                st.session_state["user"] = dict(user)
                st.session_state["route"] = next_route
                st.rerun()
    st.button("⬅️ กลับหน้าหลัก", on_click=lambda: st.session_state.update({"route": "home"}))
    footer_once()


def teacher_portal():
    st.success("เข้าสู่ระบบในบทบาท: ครูผู้สอน")
    st.info("หน้าตัวอย่างสำหรับต่อยอดเมนูของครู")
    st.button("ออกจากระบบ", on_click=lambda: st.session_state.update({"route": "home", "user": None}))
    footer_once()


def module_portal():
    st.success("เข้าสู่ระบบในบทบาท: ผู้ดูแลโมดูล")
    st.info("หน้าตัวอย่างสำหรับต่อยอดเมนูของผู้ดูแลโมดูล")
    st.button("ออกจากระบบ", on_click=lambda: st.session_state.update({"route": "home", "user": None}))
    footer_once()


def superadmin_portal():
    st.success("เข้าสู่ระบบในบทบาท: แอดมินใหญ่")
    st.info("หน้าตัวอย่างสำหรับต่อยอดเมนูของแอดมินใหญ่")
    st.button("ออกจากระบบ", on_click=lambda: st.session_state.update({"route": "home", "user": None}))
    footer_once()


def executive_portal():
    st.success("เข้าสู่ระบบในบทบาท: ฝ่ายบริหาร (Executive)")
    st.info("หน้าตัวอย่างสำหรับต่อยอดรายงานภาพรวม")
    st.button("ออกจากระบบ", on_click=lambda: st.session_state.update({"route": "home", "user": None}))
    footer_once()


# ======================
# Route Controller
# ======================
def main():
    # init route ครั้งแรก
    if "route" not in st.session_state:
        st.session_state["route"] = "home"

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
