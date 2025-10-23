# app.py
# ----------------------------------------------------
# School HR System - Home + Routed Role Logins (4 roles)
# ครู / ผู้ดูแลโมดูล / แอดมินใหญ่ / ฝ่ายบริหาร (Executive)
# ----------------------------------------------------
import os
import pandas as pd
import streamlit as st

# ==============================
# Settings & Branding
# ==============================
APP_TITLE     = "ระบบบริหารงานบุคคลโรงเรียนอนุบาลวัดคลองใหญ่"
CONTACT_EMAIL = "pakka555@gmail.com"  # ครูสุพจน์

BRAND_PRIMARY = "#0a2342"            # น้ำเงินกรมท่า
BRAND_MUTED   = "#445b66"            # เทาอมฟ้า

ASSETS_DIR   = "assets"
BANNER_PATH  = os.path.join(ASSETS_DIR, "banner.jpg")

DATA_PATH = "teachers.csv"           # ไฟล์บัญชีผู้ใช้ (CSV)

# session_state init
if "route" not in st.session_state:
    st.session_state["route"] = "home"    # หน้าแรก
if "user" not in st.session_state:
    st.session_state["user"] = None

# ==============================
# Helpers: CSS & Navigation
# ==============================
def inject_fonts_and_css():
    st.markdown(
        f"""
        <link rel="preconnect" href="https://fonts.googleapis.com">
        <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
        <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+Thai:wght@300;400;500;700&display=swap" rel="stylesheet">
        <style>
          :root{{
            --brand: {BRAND_PRIMARY};
            --muted: {BRAND_MUTED};
            --bg-card: #ffffff;
            --bg-soft: #f5f8fb;
            --shadow: 0 10px 30px rgba(10,35,66,0.08);
            --radius: 16px;
          }}
          html, body, [class*="css"] {{
            font-family: 'Noto Sans Thai', system-ui, -apple-system, Segoe UI, Roboto, 'Helvetica Neue', Arial, sans-serif;
          }}
          .block-container {{ max-width: 1220px !important; }}

          .kys-banner {{
            border-radius: var(--radius);
            overflow: hidden; box-shadow: var(--shadow);
            margin: 6px 0 18px 0;
          }}

          .kys-title h1 {{
            margin: 12px 0 6px 0; font-size: clamp(26px,2.6vw,36px);
            font-weight: 800; color: var(--brand); text-align:center;
          }}
          .kys-title p {{ margin:0; text-align:center; color:var(--muted) }}

          .kys-grid {{
            display:grid; gap:26px; margin-top:16px;
            grid-template-columns: repeat(3,1fr);
          }}
          @media (max-width:1100px) {{ .kys-grid {{ grid-template-columns: repeat(2,1fr); }} }}
          @media (max-width:760px)  {{ .kys-grid {{ grid-template-columns: 1fr; }} }}

          .kys-card {{
            background:var(--bg-card);
            border-radius: var(--radius);
            box-shadow: var(--shadow);
            padding: 22px 22px 16px;
            display:flex; flex-direction:column; min-height: 300px;
          }}
          .kys-card h3 {{ margin: 0 0 6px 0; font-weight:800; color:var(--brand) }}
          .kys-card h4 {{ margin: 0 0 10px 0; font-weight:600; color:var(--muted) }}
          .kys-card ul {{ margin: 10px 0 0 18px; color:#314657; line-height:1.65 }}

          .kys-btn {{
            display:inline-flex; align-items:center; justify-content:center;
            gap:8px; padding: 12px 16px; border-radius: 12px;
            background: var(--brand); color: #fff !important; text-decoration:none !important;
            box-shadow: var(--shadow); min-height: 44px;
          }}
          .kys-btn:hover {{ filter:brightness(1.06); }}

          .kys-contact {{ width:100%; display:flex; justify-content:flex-end; margin-top:18px; }}
          .kys-pill-link {{
            display:inline-flex; align-items:center; gap:8px; padding: 10px 14px;
            border-radius: 999px; background:#0f2748; color:#fff !important; text-decoration:none; box-shadow: var(--shadow);
          }}

          .kys-loginbox {{
            background:var(--bg-card); border-radius: var(--radius); box-shadow: var(--shadow);
            padding: 18px 18px;
          }}

          .kys-back {{ margin-top:12px; }}
        </style>
        """,
        unsafe_allow_html=True,
    )

def go(route: str):
    """เปลี่ยนหน้า (route) + rerun"""
    st.session_state["route"] = route
    st.rerun()

# ==============================
# Auth (CSV-based) — same asเดิม
# ==============================
REQUIRED_COLS = {"teacher_id","name","email","department","pin","role","admin_modules"}

def load_users() -> pd.DataFrame:
    try:
        df = pd.read_csv(DATA_PATH, dtype=str).fillna("")
        missing = REQUIRED_COLS - set(df.columns)
        if missing:
            st.warning(f"ไฟล์ '{DATA_PATH}' ไม่มีคอลัมน์: {', '.join(missing)} – จะใช้โหมดสาธิตชั่วคราว", icon="⚠️")
            return pd.DataFrame()
        return df
    except Exception:
        # ไม่มีไฟล์/อ่านไม่ได้ → โหมดสาธิต
        return pd.DataFrame()

def get_user(tid: str):
    df = load_users()
    if df.empty:
        # demo mode: mock user
        return {
            "teacher_id": tid,
            "name": "ผู้ใช้สาธิต",
            "email": "",
            "department": "",
            "pin": "1234",
            "role": "teacher",         # ค่าเริ่มต้น
            "admin_modules": "",
        }
    m = df[df["teacher_id"].astype(str).str.strip() == str(tid).strip()]
    return m.iloc[0].to_dict() if not m.empty else None

def check_login(tid: str, pin: str):
    if not tid or not pin:
        return False, None, "กรุณากรอกให้ครบ"
    u = get_user(tid)
    if not u: return False, None, "ไม่พบรหัสผู้ใช้"
    if str(u.get("pin","")).strip() != str(pin).strip():
        return False, None, "PIN ไม่ถูกต้อง"
    return True, u, None

# ==============================
# Pages
# ==============================
def page_home():
    inject_fonts_and_css()

    # 1) Banner (ถ้ามี)
    if os.path.exists(BANNER_PATH):
        st.markdown('<div class="kys-banner">', unsafe_allow_html=True)
        st.image(BANNER_PATH, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # 2) Title & Subtitle
    st.markdown(
        f"""
        <div class="kys-title">
          <h1>{APP_TITLE}</h1>
          <p>ช่วยให้ครูและบุคลากรทางการศึกษาจัดการข้อมูลบุคคลง่าย โปร่งใส และตรวจสอบได้</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 3) Grid 3 ใบ (ครู / ผู้ดูแลโมดูล / แอดมินใหญ่)
    st.markdown('<div class="kys-grid">', unsafe_allow_html=True)

    # --- Teacher Card ---
    with st.container():
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
        st.link_button("🔐 ไปหน้าเข้าสู่ระบบครู", "#", help="ไปหน้า Login ครู", on_click=lambda: go("login_teacher"), use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # --- Module Admin Card ---
    with st.container():
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
        st.link_button("🔐 ไปหน้าเข้าสู่ระบบผู้ดูแลโมดูล", "#", on_click=lambda: go("login_module"), use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # --- Superadmin Card ---
    with st.container():
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
        st.link_button("🔐 ไปหน้าเข้าสู่ระบบแอดมินใหญ่", "#", on_click=lambda: go("login_superadmin"), use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

    # 4) Executive section (แสดงเดี่ยวด้านล่าง)
    with st.container():
        st.markdown(
            """
            <div class="kys-card" style="margin-top:18px;">
              <div>
                <h3>🏫 ฝ่ายบริหาร (Executive)</h3>
                <h4>สำหรับผู้อำนวยการ / รองผู้อำนวยการ</h4>
              </div>
            """,
            unsafe_allow_html=True,
        )
        st.link_button("🔐 ไปยังหน้าฝ่ายบริหาร", "#", on_click=lambda: go("login_executive"), use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # 5) ติดต่อผู้ดูแล
    st.markdown(
        f"""
        <div class="kys-contact">
          <a class="kys-pill-link" href="mailto:{CONTACT_EMAIL}">📧 ติดต่อผู้ดูแลระบบ</a>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 6) Footer
    st.markdown(
        """
        <hr style="margin-top:26px;margin-bottom:12px;border:1px solid #e0e6ec;">
        <div style='text-align:center; color:#445b66; font-size:15px;'>
            พัฒนาโดย <b>กลุ่มบริหารงานบุคคล โรงเรียนอนุบาลวัดคลองใหญ่ จังหวัดตราด</b><br>
            เพื่อยกระดับการบริหารจัดการงานบุคคลให้ทันสมัย โปร่งใส และตรวจสอบได้
        </div>
        """,
        unsafe_allow_html=True,
    )

# ---------- Login pages ----------
def page_login(role_key: str, title: str, allow_roles: list, next_route: str):
    """Generic login page for a role"""
    inject_fonts_and_css()

    st.markdown(f"<h2 style='text-align:center;color:{BRAND_PRIMARY}'>{title}</h2>", unsafe_allow_html=True)
    st.markdown("<div class='kys-loginbox'>", unsafe_allow_html=True)
    with st.form(f"login_form_{role_key}"):
        tid = st.text_input("User ID / Teacher ID")
        pin = st.text_input("PIN", type="password")
        ok = st.form_submit_button("🔐 เข้าสู่ระบบ")
        if ok:
            success, u, err = check_login(tid, pin)
            if not success:
                st.error(err)
            else:
                # ตรวจสิทธิ์
                role = str(u.get("role","")).strip().lower()
                if role in [r.lower() for r in allow_roles]:
                    st.success(f"ยินดีต้อนรับคุณ {u.get('name','')}")
                    st.session_state["user"] = u
                    go(next_route)
                else:
                    st.error("สิทธิ์ไม่เพียงพอสำหรับเมนูนี้")
    st.markdown("</div>", unsafe_allow_html=True)
    st.button("⬅️ กลับหน้าแรก", on_click=lambda: go("home"), use_container_width=False)

# ---------- Portals (placeholder) ----------
def page_portal(title: str):
    inject_fonts_and_css()
    st.markdown(f"<h2 style='text-align:center;color:{BRAND_PRIMARY}'>{title}</h2>", unsafe_allow_html=True)
    u = st.session_state.get("user")
    if not u:
        st.warning("ยังไม่ได้เข้าสู่ระบบ", icon="⚠️")
        st.button("⬅️ กลับหน้าแรก", on_click=lambda: go("home"))
        return
    st.success(f"ล็อกอินเป็น: {u.get('name','')}  (role: {u.get('role','')})")
    st.info("หน้านี้เว้นไว้ต่อยอดฟังก์ชันจริงของบทบาทนี้ครับ")
    st.button("🚪 ออกจากระบบ", on_click=lambda: (st.session_state.update(user=None), go("home")))

# ==============================
# App — Routing
# ==============================
def main():
    st.set_page_config(page_title=APP_TITLE, page_icon="🏫", layout="wide")

    route = st.session_state.get("route", "home")

    if route == "home":
        page_home()

    elif route == "login_teacher":
        page_login(
            role_key="teacher",
            title="เข้าสู่ระบบสำหรับครูผู้สอน",
            allow_roles=["teacher","module_admin","superadmin"],
            next_route="portal_teacher",
        )
    elif route == "login_module":
        page_login(
            role_key="module",
            title="เข้าสู่ระบบผู้ดูแลโมดูล (Module Admin)",
            allow_roles=["module_admin","superadmin"],
            next_route="portal_module",
        )
    elif route == "login_superadmin":
        page_login(
            role_key="superadmin",
            title="เข้าสู่ระบบแอดมินใหญ่ (Superadmin)",
            allow_roles=["superadmin"],
            next_route="portal_superadmin",
        )
    elif route == "login_executive":
        page_login(
            role_key="executive",
            title="เข้าสู่ระบบฝ่ายบริหาร (Executive)",
            allow_roles=["executive","superadmin"],
            next_route="portal_executive",
        )

    # portals (ตัวอย่าง)
    elif route == "portal_teacher":
        page_portal("พอร์ทัลสำหรับครูผู้สอน")
    elif route == "portal_module":
        page_portal("พอร์ทัลผู้ดูแลโมดูล")
    elif route == "portal_superadmin":
        page_portal("พอร์ทัลแอดมินใหญ่")
    elif route == "portal_executive":
        page_portal("พอร์ทัลฝ่ายบริหาร")
    else:
        go("home")


if __name__ == "__main__":
    main()
