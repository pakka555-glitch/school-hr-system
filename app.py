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
        """
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+Thai:wght@300;400;600;700&display=swap" rel="stylesheet">

<style>
  :root{
    --brand:#0a2342;          /* น้ำเงินเข้ม (หัวข้อ/ปุ่ม) */
    --brand-2:#0d3b66;        /* น้ำเงินรอง */
    --text:#1a2b3b;
    --muted:#445b66;
    --line:#e6eef7;
    --card:#ffffff;
    --bg:#f6f9fc;
  }

  html, body, [class^="css"] {
    font-family: "Noto Sans Thai", system-ui, -apple-system, Segoe UI, Roboto, "Helvetica Neue", Arial, "Noto Sans", "Liberation Sans", sans-serif;
  }

  /* ให้พื้นที่ดูโปร่ง */
  .block-container { padding-top: 1.6rem; }

  /* ========= HEADER (โลโก้ + ชื่อระบบ) ========= */
  .kys-hero{
    display:flex; gap:18px; align-items:center;
    background:var(--card);
    border:1px solid var(--line);
    border-radius:16px;
    padding:16px 20px;
    box-shadow: 0 4px 14px rgba(10,35,66,.06);
    margin: 10px 0 6px 0;
  }
  .kys-hero img.kys-logo{
    width:96px;height:96px; object-fit:cover; border-radius:12px;
  }
  .kys-hero .kys-title h1{
    margin:0; font-size:40px; font-weight:700; color:var(--brand);
  }
  .kys-hero .kys-title p{
    margin:4px 0 0; color:var(--muted); font-size:17px;
  }

  /* ========= BANNER ========= */
  .kys-banner{ border-radius:16px; overflow:hidden; box-shadow:0 6px 20px rgba(10,35,66,.08); }

  /* ========= GRID การ์ด ========= */
  .kys-grid{
    display:grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 20px;
    margin-top: 22px;
  }
  .kys-card{
    background:var(--card);
    border:1px solid var(--line);
    border-radius:16px;
    padding:18px 18px 14px 18px;
    box-shadow:0 4px 14px rgba(10,35,66,.06);
    min-height: 360px;
    display:flex; flex-direction:column;
  }
  .kys-card h3{
    margin:0 0 2px 0; font-size:22px; color:var(--brand)
  }
  .kys-card .sub{
    margin:0 0 12px 0; font-weight:600; color:var(--muted)
  }
  .kys-card ul{ margin:0 0 14px 18px; color:var(--text) }
  .kys-card li{ margin:6px 0 }

  .kys-grow{ flex:1 } /* ดันปุ่มลงล่าง */

  .kys-btn{
    display:inline-flex; align-items:center; gap:8px;
    background:var(--brand-2); color:#fff; text-decoration:none;
    padding:10px 16px; border-radius:12px; font-weight:700;
    box-shadow:0 6px 16px rgba(13,59,102,.18);
    transition:.15s ease-in-out;
  }
  .kys-btn:hover{ filter:brightness(1.02); transform: translateY(-1px); }

  .kys-btn-secondary{
    background:#0a234233; color:var(--brand-2);
    box-shadow:none;
  }

  /* ========= เส้นคั่น ========= */
  .kys-hr { border-top:1px solid var(--line); margin: 18px 0 8px 0; }

  /* ========= Footer ขวา ========= */
  .kys-footer{
    text-align:right; color:var(--muted); margin-top:18px;
  }
</style>
        """,
        unsafe_allow_html=True,
    )

# ------------------------------------
# หน้าแรก
# ------------------------------------
def show_home():
    import os
    inject_fonts_and_css()

    # 1) Banner ด้านบน (แสดงเมื่อมีไฟล์)
    if os.path.exists("assets/banner.jpg"):
        st.markdown('<div class="kys-banner">', unsafe_allow_html=True)
        st.image("assets/banner.jpg", use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # 2) โลโก้ซ้าย + ชื่อระบบขวา
    st.markdown(
        f"""
        <div class="kys-hero">
          <img src="assets/logo.jpg" class="kys-logo" />
          <div class="kys-title">
            <h1>ระบบบริหารงานบุคคลโรงเรียนอนุบาลวัดคลองใหญ่</h1>
            <p>ช่วยให้ครูและบุคลากรจัดการข้อมูลบุคคลได้อย่างมีระบบ โปร่งใส และตรวจสอบได้</p>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="kys-hr"></div>', unsafe_allow_html=True)

    # 3) การ์ด 3 ใบ (สูงเท่ากัน ปุ่มอยู่ล่างเสมอ)
    st.markdown(
        """
<div class="kys-grid">

  <!-- ครูผู้สอน -->
  <div class="kys-card">
    <h3>🧑‍🏫 สำหรับครูผู้สอน</h3>
    <div class="sub">Teacher</div>
    <ul>
      <li>จัดการ/ปรับปรุงข้อมูลส่วนบุคคล</li>
      <li>ส่งคำขอ (ลา/ใบราชการ/อบรม ฯลฯ) และตรวจสอบสถานะ</li>
      <li>อัปโหลดเอกสารงานบุคคล (ฟอร์ม/ใบอนุญาต/แฟ้มสะสมงาน)</li>
    </ul>
    <div class="kys-grow"></div>
    <a class="kys-btn" href="#">🔐 เข้าสู่ระบบครู</a>
  </div>

  <!-- ผู้ดูแลโมดูล -->
  <div class="kys-card">
    <h3>✴ ผู้ดูแลโมดูล</h3>
    <div class="sub">Module Admin</div>
    <ul>
      <li>ตรวจสอบ/อนุมัติคำขอในโมดูลที่รับผิดชอบ</li>
      <li>ติดตามเอกสาร ปรับแก้ข้อมูลที่จำเป็น</li>
      <li>ดูสถิติและรายงานในโมดูล</li>
    </ul>
    <div class="kys-grow"></div>
    <a class="kys-btn" href="#">🔐 เข้าสู่ระบบผู้ดูแลโมดูล</a>
  </div>

  <!-- แอดมินใหญ่ -->
  <div class="kys-card">
    <h3>🛡 แอดมินใหญ่</h3>
    <div class="sub">Superadmin</div>
    <ul>
      <li>กำกับดูแลงานภาพรวมของระบบทั้งหมด</li>
      <li>จัดการข้อมูลบุคลากร/สิทธิ์การเข้าใช้</li>
      <li>ออกรายงานภาพรวมเพื่อการบริหาร</li>
    </ul>
    <div class="kys-grow"></div>
    <a class="kys-btn" href="#">🔐 เข้าสู่ระบบแอดมินใหญ่</a>
  </div>

</div>
        """,
        unsafe_allow_html=True,
    )

    # ปุ่มติดต่อผู้ดูแล (ซ้าย)
    st.markdown(
        """
<div style="margin-top:16px;">
  <a class="kys-btn kys-btn-secondary" href="mailto:pakka555@gmail.com">✉️ ติดต่อผู้ดูแลระบบ</a>
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
