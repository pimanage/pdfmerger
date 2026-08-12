import io
import streamlit as st
from pypdf import PdfReader, PdfWriter

# 1. Define Category Structure
CATEGORIES = {
    "Category_A": ["Sub_Category_1.1", "Sub_Category_1.2", "Sub_Category_1.3"],
    "Category_B": ["Sub_Category_2.1", "Sub_Category_2.2"],
    "Category_C": ["Sub_Category_3.1", "Sub_Category_3.2"]
}

# 2. Page Configuration
st.set_page_config(
    page_title="PDF Merger & Auto-Naming Tool",
    page_icon="📄",
    layout="centered"
)

# Professional & Modern Styling (Clean, Elegant Pastel Soft Tone)
st.markdown("""
<style>
    /* Main Background & Font Styling */
    .stApp {
        background-color: #FAFAFC;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Title & Header Styling */
    h1 {
        color: #1E293B;
        font-weight: 700;
        font-size: 2.1rem !important;
        margin-bottom: 0.2rem !important;
    }
    
    p {
        color: #64748B;
        font-size: 0.95rem;
    }

    /* Primary Action Buttons */
    .stButton>button {
        background-color: #6366F1;
        color: #FFFFFF;
        border-radius: 8px;
        border: none;
        font-weight: 600;
        padding: 0.5rem 1rem;
        transition: all 0.2s ease-in-out;
    }
    .stButton>button:hover {
        background-color: #4F46E5;
        color: #FFFFFF;
        box-shadow: 0 4px 12px rgba(99, 102, 241, 0.25);
    }

    /* Small Control Buttons (Reorder & Delete) */
    button[data-testid="baseButton-secondary"] {
        background-color: #F1F5F9 !important;
        color: #475569 !important;
        border: 1px solid #E2E8F0 !important;
        border-radius: 6px !important;
    }
    button[data-testid="baseButton-secondary"]:hover {
        background-color: #E2E8F0 !important;
        color: #0F172A !important;
    }

    /* File Uploader Container */
    [data-testid="stFileUploader"] {
        background-color: #FFFFFF;
        border: 2px dashed #CBD5E1;
        border-radius: 12px;
        padding: 1rem;
    }
    [data-testid="stFileUploader"]:hover {
        border-color: #6366F1;
    }

    /* Divider */
    hr {
        margin: 1.5rem 0;
        border-color: #F1F5F9;
    }
</style>
""", unsafe_allow_html=True)

# App Header
st.title("📄 PDF Merger & Naming Tool")
st.write("Streamline your document workflow: merge multiple PDF files and standardize file names instantly.")

st.divider()

# Session State Management
if "file_list" not in st.session_state:
    st.session_state.file_list = []

if "uploader_key" not in st.session_state:
    st.session_state.uploader_key = 0

# Function to handle uploaded files and auto-clear top container
def process_new_files():
    key_name = f"uploader_{st.session_state.uploader_key}"
    uploaded = st.session_state.get(key_name, [])
    
    if uploaded:
        for f in uploaded:
            if not any(item['name'] == f.name and item['file'].size == f.size for item in st.session_state.file_list):
                st.session_state.file_list.append({'name': f.name, 'file': f})
        st.session_state.uploader_key += 1

# 3. File Upload Area
st.subheader("1. Upload PDF Files")
st.file_uploader(
    "Drag & drop PDF files here or click to browse",
    type=["pdf"],
    accept_multiple_files=True,
    key=f"uploader_{st.session_state.uploader_key}",
    on_change=process_new_files,
    label_visibility="collapsed"
)

# 4. File Queue & Reorder Section
if st.session_state.file_list:
    st.write("---")
    st.subheader("📋 Document Queue & Ordering")
    st.caption("Adjust the merging sequence or remove unwanted files below:")
    
    for idx, item in enumerate(st.session_state.file_list):
        col_num, col_name, col_up, col_down, col_del = st.columns([0.6, 5.4, 1, 1, 1])
        
        col_num.markdown(f"**#{idx + 1}**")
        col_name.write(f"📄 {item['name']}")
        
        # Move Up
        if col_up.button("▲", key=f"up_{idx}", help="Move file up"):
            if idx > 0:
                st.session_state.file_list[idx], st.session_state.file_list[idx-1] = st.session_state.file_list[idx-1], st.session_state.file_list[idx]
                st.rerun()
                
        # Move Down
        if col_down.button("▼", key=f"down_{idx}", help="Move file down"):
            if idx < len(st.session_state.file_list) - 1:
                st.session_state.file_list[idx], st.session_state.file_list[idx+1] = st.session_state.file_list[idx+1], st.session_state.file_list[idx]
                st.rerun()
                
        # Remove File
        if col_del.button("✕", key=f"del_{idx}", help="Remove this file"):
            st.session_state.file_list.pop(idx)
            st.rerun()

    # Clear All Button
    if st.button("Clear All Files", use_container_width=False):
        st.session_state.file_list = []
        st.rerun()

st.divider()

# 5. Metadata & Naming Convention
st.subheader("2. Document Naming & Categorization")

col1, col2 = st.columns(2)

with col1:
    selected_main = st.selectbox(
        "Main Category",
        options=list(CATEGORIES.keys())
    )

with col2:
    sub_options = CATEGORIES.get(selected_main, [])
    selected_sub = st.selectbox(
        "Sub Category",
        options=sub_options
    )

default_filename = f"{selected_main}_{selected_sub}_Details"

final_filename = st.text_input(
    "Standardized Filename Output",
    value=default_filename,
    help="You can edit the final file name here before merging."
)

st.divider()

# 6. Merge & Process Section
if st.button("⚡ Merge & Download PDF", use_container_width=True):
    active_items = st.session_state.file_list
    
    if not active_items:
        st.error("Please upload at least one PDF file before processing.")
    elif not final_filename.strip():
        st.error("Please provide a valid filename.")
    else:
        save_filename = final_filename.strip()
        if not save_filename.lower().endswith(".pdf"):
            save_filename += ".pdf"
            
        try:
            with st.spinner("Merging documents, please wait..."):
                writer = PdfWriter()
                for item in active_items:
                    reader = PdfReader(item['file'])
                    for page in reader.pages:
                        writer.add_page(page)
                
                output_pdf = io.BytesIO()
                writer.write(output_pdf)
                output_pdf.seek(0)
                
            st.success("PDF merged and named successfully!")
            
            st.download_button(
                label=f"⬇️ Download {save_filename}",
                data=output_pdf,
                file_name=save_filename,
                mime="application/pdf",
                use_container_width=True
            )
        except Exception as e:
            st.error(f"Processing Error: {str(e)}")

st.caption("Designed for automated document management and workflow efficiency.")
