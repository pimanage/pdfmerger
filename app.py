import io
import streamlit as st
from pypdf import PdfReader, PdfWriter
from streamlit_sortables import sort_items

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

# Custom CSS ตกแต่งสีพาสเทล
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
</style>
""", unsafe_allow_html=True)

st.title("✿ PDF Merger & Naming Tool ✿")
st.write("❤ ลากไฟล์ PDF มาวางในกล่องด้านล่างได้เลยค่ะ ❤")

# Session state สำหรับจัดเก็บข้อมูล
if "pdf_files_dict" not in st.session_state:
    st.session_state.pdf_files_dict = {}

if "sorted_filenames" not in st.session_state:
    st.session_state.sorted_filenames = []

# ฟังก์ชันอัปเดตไฟล์เมื่อมีการเลือกไฟล์เพิ่ม
def sync_uploaded_files():
    uploaded = st.session_state.get("uploader_widget", [])
    if uploaded:
        for f in uploaded:
            if f.name not in st.session_state.pdf_files_dict:
                st.session_state.pdf_files_dict[f.name] = f
                st.session_state.sorted_filenames.append(f.name)

# 3. กล่องอัปโหลดไฟล์
st.file_uploader(
    "หรือคลิกเลือกไฟล์ที่นี่ (เลือกได้หลายไฟล์พร้อมกัน)",
    type=["pdf"],
    accept_multiple_files=True,
    key="uploader_widget",
    on_change=sync_uploaded_files
)

# 4. ส่วน Drag & Drop สลับลำดับแนวตั้ง (ใช้ Dynamic Key รีเซ็ต Widget เมื่อไฟล์เพิ่ม)
if len(st.session_state.sorted_filenames) > 1:
    st.write("---")
    st.subheader("📋 ลากสลับลำดับการรวมไฟล์ด้านล่างนี้ได้เลยค่ะ")
    
    # บังคับอัปเดต Widget ด้วยการสร้าง key ตามจำนวนไฟล์ + ชื่อไฟล์รวมกัน
    dynamic_key = f"sortable_{len(st.session_state.sorted_filenames)}_{'_'.join(st.session_state.sorted_filenames)}"
    
    sorted_res = sort_items(
        st.session_state.sorted_filenames,
        direction="vertical",
        key=dynamic_key
    )
    
    if sorted_res:
        st.session_state.sorted_filenames = sorted_res

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
    ordered_names = st.session_state.sorted_filenames
    files_map = st.session_state.pdf_files_dict
    
    if not ordered_names or not files_map:
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
                for name in ordered_names:
                    pdf_file = files_map[name]
                    reader = PdfReader(pdf_file)
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
