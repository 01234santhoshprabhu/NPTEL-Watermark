import streamlit as st
from pypdf import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from io import BytesIO

st.set_page_config(page_title="PDF Image Watermark Tool", layout="centered")

st.title("📄 PDF Image Watermark Tool")
st.markdown("Upload multiple PDFs and apply your logo watermark.")

pdf_files = st.file_uploader(
    "Upload PDF Files",
    type=["pdf"],
    accept_multiple_files=True
)

logo_file = st.file_uploader(
    "Upload Logo Image (PNG/JPG)",
    type=["png", "jpg", "jpeg"]
)

# Initialize session storage
if "processed_files" not in st.session_state:
    st.session_state.processed_files = {}

if pdf_files and logo_file:

    size_percent = st.slider("Watermark Size (% of page width)", 10, 80, 40)
    opacity = st.slider("Transparency", 0.05, 1.0, 0.2)
    rotation = st.slider("Rotation (Degrees)", -180, 180, 0)

    position = st.selectbox(
        "Position",
        ["Center", "Top Center", "Bottom Center"]
    )

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

            c.drawImage(img, x, y, width=watermark_width,
                        height=watermark_height, mask='auto')

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

    if st.button("🚀 Apply Watermark to All PDFs"):

        st.session_state.processed_files = {}

        for pdf in pdf_files:
            with st.spinner(f"Processing {pdf.name}..."):
                output_pdf = add_watermark(pdf, logo_file)

                st.session_state.processed_files[pdf.name] = output_pdf

        st.success("All PDFs Processed Successfully!")

# Show download buttons OUTSIDE button block
if st.session_state.processed_files:

    st.subheader("⬇ Download Files")

    for name, file in st.session_state.processed_files.items():
        st.download_button(
            label=f"Download {name}",
            data=file,
            file_name=name,
            mime="application/pdf",
            key=name
        )
