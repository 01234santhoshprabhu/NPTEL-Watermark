import streamlit as st
from pypdf import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from io import BytesIO
from PIL import Image, ImageEnhance

st.set_page_config(page_title="NPTEL Watermark System", layout="wide")

# ----------------------------
# Custom Styling
# ----------------------------
st.markdown("""
    <style>
    .main-title {
        font-size: 36px;
        font-weight: 700;
        color: #1f4e79;
    }
    .sub-text {
        font-size: 16px;
        color: gray;
    }
    .stButton>button {
        background-color: #1f4e79;
        color: white;
        font-weight: 600;
        border-radius: 8px;
        height: 45px;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown('<p class="main-title">📄 NPTEL PDF Watermark System</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-text">Upload multiple PDFs and apply secure logo watermark.</p>', unsafe_allow_html=True)

# ----------------------------
# Layout Columns
# ----------------------------
col1, col2 = st.columns([1,1])

with col1:
    pdf_files = st.file_uploader(
        "Upload PDF Files",
        type=["pdf"],
        accept_multiple_files=True
    )

    logo_file = st.file_uploader(
        "Upload Logo Image",
        type=["png", "jpg", "jpeg"]
    )

with col2:
    st.subheader("⚙ Watermark Settings")

    size_percent = st.slider("Watermark Size (%)", 10, 80, 40)
    opacity = st.slider("Transparency", 0.05, 1.0, 0.3)
    rotation = st.slider("Rotation", -180, 180, 0)

    position = st.selectbox(
        "Position",
        ["Center", "Top Center", "Bottom Center"]
    )

# ----------------------------
# PREVIEW SECTION
# ----------------------------
if logo_file:

    st.markdown("---")
    st.subheader("👁 Watermark Preview")

    preview_bg = Image.new("RGB", (600, 800), "white")
    logo = Image.open(logo_file).convert("RGBA")

    # Resize
    new_width = int(600 * (size_percent / 100))
    logo = logo.resize((new_width, new_width))

    # Apply transparency
    alpha = logo.split()[3]
    alpha = ImageEnhance.Brightness(alpha).enhance(opacity)
    logo.putalpha(alpha)

    # Apply rotation
    logo = logo.rotate(rotation, expand=True)

    # Position
    if position == "Center":
        x = (600 - logo.width) // 2
        y = (800 - logo.height) // 2
    elif position == "Top Center":
        x = (600 - logo.width) // 2
        y = 50
    else:
        x = (600 - logo.width) // 2
        y = 800 - logo.height - 50

    preview_bg.paste(logo, (x, y), logo)

    st.image(preview_bg, caption="Watermark Preview (Sample Page)", width="stretch")

# ----------------------------
# WATERMARK FUNCTION
# ----------------------------
def add_watermark(input_pdf, watermark_image):

    reader = PdfReader(input_pdf)
    writer = PdfWriter()

    for page in reader.pages:

        packet = BytesIO()
        page_width = float(page.mediabox.width)
        page_height = float(page.mediabox.height)

        c = canvas.Canvas(packet, pagesize=(page_width, page_height))
        img = ImageReader(watermark_image)

        watermark_width = page_width * (size_percent / 100)
        watermark_height = watermark_width

        if position == "Center":
            x = (page_width - watermark_width) / 2
            y = (page_height - watermark_height) / 2
        elif position == "Top Center":
            x = (page_width - watermark_width) / 2
            y = page_height - watermark_height - 50
        else:
            x = (page_width - watermark_width) / 2
            y = 50

        c.saveState()
        c.translate(page_width / 2, page_height / 2)
        c.rotate(rotation)
        c.translate(-page_width / 2, -page_height / 2)
        c.setFillAlpha(opacity)

        c.drawImage(img, x, y,
                    width=watermark_width,
                    height=watermark_height,
                    mask='auto')

        c.restoreState()
        c.save()

        packet.seek(0)
        watermark_pdf = PdfReader(packet)
        page.merge_page(watermark_pdf.pages[0])
        writer.add_page(page)

    output = BytesIO()
    writer.write(output)
    output.seek(0)
    return output

# ----------------------------
# PROCESS SECTION
# ----------------------------
if "processed_files" not in st.session_state:
    st.session_state.processed_files = {}

if pdf_files and logo_file:

    if st.button("🚀 Apply Watermark to All PDFs"):

        st.session_state.processed_files = {}

        for pdf in pdf_files:
            with st.spinner(f"Processing {pdf.name}..."):
                output_pdf = add_watermark(pdf, logo_file)
                st.session_state.processed_files[pdf.name] = output_pdf

        st.success("All PDFs processed successfully!")

# ----------------------------
# DOWNLOAD SECTION
# ----------------------------
if st.session_state.processed_files:

    st.markdown("---")
    st.subheader("⬇ Download Watermarked PDFs")

    for name, file in st.session_state.processed_files.items():
        st.download_button(
            label=f"Download {name}",
            data=file,
            file_name=name,
            mime="application/pdf",
            key=name
        )
