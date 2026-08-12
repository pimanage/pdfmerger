import io
import streamlit as st
from pypdf import PdfReader, PdfWriter

# 1. กำหนดโครงสร้างหมวดหมู่
CATEGORIES = {
    "หมวดหลัก_A": ["หมวดย่อย_1.1", "หมวดย่อย_1.2", "หมวดย่อย_1.3"],
    "หมวดหลัก_B": ["หมวดย่อย_2.1", "หมวดย่อย_2.2"],
    "หมวดหลัก_C": ["หมวดย่อย_3.1", "หมวดย่อย_3.2"]
}

# 2. ตั้งค่าหน้าตา Web App
st.set_page_config(
    page_title="✿ PDF Merger & Naming Tool ✿",
    page_icon="✿",
    layout="centered"
)

# Custom CSS ตกแต่งสีพาสเทล + ซ่อนรายชื่อไฟล์ในกล่อง Uploader ด้านบน
st.markdown("""
<style>
    .stApp {
        background-color: #FFF5F5;
    }
    .stButton>button {
        background-color: #FFC6FF;
        color: #5A4B4B;
        border-radius: 8px;
        border: none;
        font-weight: 500;
    }
    /* ซ่อนแถบแสดงรายชื่อไฟล์ของ uploader ด้านบน ไม่ให้แสดงซ้ำซ้อน */
    [data-testid="stFileUploaderFileData"] {
        display: none !important;
    }
</style>
""", unsafe_allow_html=True)

st.title("✿ PDF Merger & Naming Tool ✿")
st.write("❤ ลากไฟล์ PDF มาวางในกล่องด้านล่างได้เลยค่ะ ❤")

# Session State ระบบความจำกลางจุดเดียว
if "file_list" not in st.session_state:
    st.session_state.file_list = []

# ฟังก์ชันเพิ่มไฟล์ใหม่เข้าลิสต์ล่าง
def sync_uploaded_files():
    uploaded = st.session_state.get("uploader_widget", [])
    if uploaded:
        for f in uploaded:
            # เพิ่มเฉพาะไฟล์ใหม่ ป้องกันการเพิ่มไฟล์ซ้ำ
            if not any(item['name'] == f.name and item['file'].size == f.size for item in st.session_state.file_list):
                st.session_state.file_list.append({'name': f.name, 'file': f})

# 3. กล่องอัปโหลดไฟล์ (ซ่อนรายการไฟล์ด้านบนไว้แล้ว)
st.file_uploader(
    "หรือคลิกเลือกไฟล์ที่นี่ (เลือกได้หลายไฟล์พร้อมกัน)",
    type=["pdf"],
    accept_multiple_files=True,
    key="uploader_widget",
    on_change=sync_uploaded_files
)

# 4. ส่วนจัดการไฟล์เดี่ยวจุดเดียว (แสดงรายการ / เลื่อนขึ้นลง / ลบทีละไฟล์)
if st.session_state.file_list:
    st.write("---")
    st.subheader("📋 รายการไฟล์ที่เลือกทั้งหมด")
    
    for idx, item in enumerate(st.session_state.file_list):
        col_num, col_name, col_up, col_down, col_del = st.columns([0.5, 5, 1, 1, 1])
        
        col_num.write(f"**{idx + 1}.**")
        col_name.write(f"📄 {item['name']}")
        
        # ปุ่มเลื่อนขึ้น
        if col_up.button("▲", key=f"up_{idx}"):
            if idx > 0:
                st.session_state.file_list[idx], st.session_state.file_list[idx-1] = st.session_state.file_list[idx-1], st.session_state.file_list[idx]
                st.rerun()
                
        # ปุ่มเลื่อนลง
        if col_down.button("▼", key=f"down_{idx}"):
            if idx < len(st.session_state.file_list) - 1:
                st.session_state.file_list[idx], st.session_state.file_list[idx+1] = st.session_state.file_list[idx+1], st.session_state.file_list[idx]
                st.rerun()
                
        # ปุ่มลบไฟล์เดี่ยว (ลบเฉพาะไฟล์นี้ ไฟล์อื่นอยู่ครบ 100%)
        if col_del.button("🗑️", key=f"del_{idx}"):
            st.session_state.file_list.pop(idx)
            st.rerun()

    # ปุ่มล้างรายการทั้งหมด
    if st.button("✖ ล้างไฟล์ทั้งหมด ✖", use_container_width=True):
        st.session_state.file_list = []
        st.rerun()

st.write("---")

# 5. Dropdown เลือกหมวดหมู่หลัก และหมวดย่อย
selected_main = st.selectbox(
    "🎀 1. เลือกหมวดหลัก:",
    options=list(CATEGORIES.keys())
)

sub_options = CATEGORIES.get(selected_main, [])
selected_sub = st.selectbox(
    "🎀 2. เลือกหมวดย่อย:",
    options=sub_options
)

# 6. คำนวณชื่อไฟล์ตั้งต้น และช่องให้แก้ไข
default_filename = f"{selected_main}_{selected_sub}_[ระบุรายละเอียด]"

final_filename = st.text_input(
    "✏ 3. ชื่อไฟล์ระบบตั้งให้ (แก้ไขเพิ่มเติมตรงนี้ได้เลยค่ะ):",
    value=default_filename
)

st.write("---")

# 7. ปุ่มรวมไฟล์และดาวน์โหลด
if st.button("★  เริ่มบันทึกและรวมไฟล์  ★", use_container_width=True):
    active_items = st.session_state.file_list
    
    if not active_items:
        st.error("แจ้งเตือน: ยังไม่มีไฟล์ PDF ในระบบเลยค่ะ")
    elif not final_filename.strip():
        st.error("แจ้งเตือน: กรุณาใส่ชื่อไฟล์ด้วยนะคะ")
    else:
        save_filename = final_filename.strip()
        if not save_filename.lower().endswith(".pdf"):
            save_filename += ".pdf"
            
        try:
            with st.spinner("ระบบกำลังรวมไฟล์ให้อยู่นะคะ..."):
                writer = PdfWriter()
                for item in active_items:
                    reader = PdfReader(item['file'])
                    for page in reader.pages:
                        writer.add_page(page)
                
                output_pdf = io.BytesIO()
                writer.write(output_pdf)
                output_pdf.seek(0)
                
            st.success("ระบบรวมไฟล์และตั้งชื่อให้เรียบร้อยแล้วนะคะ ✿")
            
            st.download_button(
                label=f"⬇️ บันทึกไฟล์ {save_filename}",
                data=output_pdf,
                file_name=save_filename,
                mime="application/pdf"
            )
        except Exception as e:
            st.error(f"เกิดข้อผิดพลาด ระบบหลังบ้านมีปัญหา: {str(e)}")
