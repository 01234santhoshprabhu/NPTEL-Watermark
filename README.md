# PDF Watermark

Apply a logo watermark to multiple PDF files with adjustable size, transparency, rotation, and placement.

[Open the live app](https://01234santhoshprabhu.github.io/NPTEL-Watermark/)

## Browser application

1. Select one or more PDF files.
2. Upload a PNG or JPEG logo.
3. Choose the watermark size, transparency, rotation, and position.
4. Click **Apply Watermark to All PDFs**.
5. Download each processed PDF.

PDF processing runs in your browser. The browser application does not upload the selected documents to a server and opens without a Google login.

## Run locally

```bash
python -m http.server 8000
```

Open [localhost:8000](http://localhost:8000/). The browser application uses `pdf-lib` from a CDN, so an internet connection is needed to load that library.

## Python alternative

The repository also contains a Streamlit implementation:

```bash
pip install -r requirements.txt
streamlit run image_watermark_app.py
```

Use the URL printed by Streamlit to open the application.

## Project structure

- `index.html` — browser interface, logo preview, and PDF processing.
- `image_watermark_app.py` — Python/Streamlit implementation.
- `requirements.txt` — Python dependencies.
- `render.yaml` — deployment configuration.

## Technologies

JavaScript, HTML, CSS, pdf-lib, Python, Streamlit, pypdf, ReportLab, and Pillow.
