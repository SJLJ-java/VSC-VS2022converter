import io
import os
import zipfile
import tempfile
import subprocess
from flask import Flask, request, send_file, abort, render_template_string

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 512 * 1024 * 1024  # bump to 512MB for folders

UPLOAD_FORM = """
<!DOCTYPE html>
<html>
<head>
<title>VS2022 Converter</title>
<style>
body { font-family: Arial; padding: 30px; }
.box { border: 2px dashed #333; padding: 30px; width: 400px; text-align: center; }

/* Button styles */
button {
    margin-top: 15px;
    padding: 10px 22px;
    font-size: 17px;
    color: white;
    border: none;
    border-radius: 6px;
    cursor: not-allowed;           
    opacity: 0.5;
    background: grey;
    transition: opacity 0.3s ease, background 0.3s ease;
}

/* Enabled state */
button:enabled {
    cursor: pointer;
    opacity: 1;
    background: rgb(255,0,0);
    animation: color-rotate 6s linear infinite;
}

/* RGB color rotation */
@keyframes color-rotate {
    0%   { background-color: rgb(255,0,0); }
    14%  { background-color: rgb(255,127,0); }
    28%  { background-color: rgb(255,255,0); }
    42%  { background-color: rgb(0,255,0); }
    57%  { background-color: rgb(0,0,255); }
    71%  { background-color: rgb(75,0,130); }
    85%  { background-color: rgb(148,0,211); }
    100% { background-color: rgb(255,0,0); }
}
</style>
</head>
<body>
<h2>VS2022 Auto Converter</h2>
<p>Upload any number of .cpp/.h files OR an entire folder.</p>
<form action="/convert" method="post" enctype="multipart/form-data" id="uploadForm">
<div class="box">

<!-- Folder + multi-file upload -->
<input type="file" 
       name="files" 
       id="fileInput"
       webkitdirectory 
       directory 
       multiple 
       accept=".cpp,.h">

<br>
<button type="submit" id="convertBtn" disabled>Do the thing!</button>
</div>
</form>

<script>
// Enable the RGB button only after selecting files
const fileInput = document.getElementById("fileInput");
const convertBtn = document.getElementById("convertBtn");

fileInput.addEventListener("change", () => {
    convertBtn.disabled = !fileInput.files.length;
});
</script>
</body>
</html>
"""


VCXPROJ_TEMPLATE = """<?xml version="1.0" encoding="utf-8"?>
<Project DefaultTargets="Build" xmlns="http://schemas.microsoft.com/developer/msbuild/2003">
  <ItemGroup>
  </ItemGroup>
</Project>
"""

FILTERS_TEMPLATE = """<?xml version="1.0" encoding="utf-8"?>
<Project ToolsVersion="4.0" xmlns="http://schemas.microsoft.com/developer/msbuild/2003">
  <ItemGroup>
  </ItemGroup>
</Project>
"""


@app.get("/")
def index():
    return UPLOAD_FORM


@app.post("/convert")
def convert_file():

    uploaded_files = request.files.getlist("files")

    if not uploaded_files or uploaded_files[0].filename == "":
        abort(400, "No files uploaded")

    workdir = tempfile.mkdtemp()

    # Save each uploaded file WITH its folder structure
    for f in uploaded_files:

        raw_disp = f.headers.get("Content-Disposition", "")
        if "filename=" not in raw_disp:
            continue

        # Extract the full folder path
        rel_path = raw_disp.split("filename=")[1].strip('"')
        rel_path = rel_path.replace("\\", "/")

        # Ensure folder exists
        full_out = os.path.join(workdir, rel_path)
        os.makedirs(os.path.dirname(full_out), exist_ok=True)

        # Save file
        f.save(full_out)

    # Create minimal project files in root
    vcxproj_file = os.path.join(workdir, "VScompress.vcxproj")
    filters_file = os.path.join(workdir, "VScompress.filters")

    with open(vcxproj_file, "w", encoding="utf-8") as f:
        f.write(VCXPROJ_TEMPLATE)
    with open(filters_file, "w", encoding="utf-8") as f:
        f.write(FILTERS_TEMPLATE)

    # Run your conversion scripts
    script_dir = os.path.dirname(os.path.abspath(__file__))
    try:
        subprocess.run(
            ["python3", os.path.join(script_dir, "tools/update_filters.py")],
            cwd=workdir, check=True
        )
        subprocess.run(
            ["python3", os.path.join(script_dir, "tools/update_vcxproj.py")],
            cwd=workdir, check=True
        )
    except subprocess.CalledProcessError as e:
        return f"Conversion failed: {e}", 500

    # ZIP everything
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        for root, dirs, files in os.walk(workdir):
            for file in files:
                full = os.path.join(root, file)
                rel = os.path.relpath(full, workdir)
                z.write(full, rel)

    buf.seek(0)
    return send_file(
        buf,
        as_attachment=True,
        download_name="VS2022_converted.zip",
        mimetype="application/zip"
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
