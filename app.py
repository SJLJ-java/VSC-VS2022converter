import io
import os
import zipfile
import tempfile
import subprocess
from flask import Flask, request, send_file, render_template_string, abort

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 64 * 1024 * 1024  # 64MB upload limit


# ------------------------------
# HTML FRONTEND
# ------------------------------

UPLOAD_FORM = """
<!DOCTYPE html>
<html>
<head>
<title>VS2022 Converter</title>
<style>
body { font-family: Arial; padding: 30px; }
.box {
    border: 2px dashed #333;
    padding: 30px;
    width: 400px;
    text-align: center;
}
button { margin-top: 15px; padding: 10px 22px; font-size: 17px; }
</style>
</head>
<body>

<h2>VS2022 Auto Converter</h2>
<p>Select a .zip C++ project and I will fix all .vcxproj & .filters files.</p>

<form action="/convert" method="post" enctype="multipart/form-data">
<div class="box">
    <input type="file" name="file" accept=".zip" required>
    <br>
    <button type="submit">Convert Now</button>
</div>
</form>

</body>
</html>
"""


@app.get("/")
def index():
    return UPLOAD_FORM


# ------------------------------
# MAIN CONVERSION ENDPOINT
# ------------------------------

@app.post("/convert")
def convert_zip():
    if "file" not in request.files:
        abort(400, "Missing file upload")

    uploaded_zip = request.files["file"]

    if uploaded_zip.filename == "" or not uploaded_zip.filename.lower().endswith(".zip"):
        abort(400, "Must upload a .zip file")

    workdir = tempfile.mkdtemp()

    # Extract uploaded zip
    try:
        with zipfile.ZipFile(uploaded_zip) as z:
            z.extractall(workdir)
    except zipfile.BadZipFile:
        abort(400, "Invalid ZIP")

    # -----------------------------------
    # RUN YOUR TWO CONVERTER SCRIPTS
    # -----------------------------------

    # MUST EXIST IN SAME FOLDER AS THIS FILE
    subprocess.run(["python3", "convert_filters.py"], cwd=workdir)
    subprocess.run(["python3", "convert_vcxproj.py"], cwd=workdir)

    # -----------------------------------
    # REZIP RESULTS
    # -----------------------------------

    result_zip = io.BytesIO()
    with zipfile.ZipFile(result_zip, "w", zipfile.ZIP_DEFLATED) as z:
        for root, dirs, files in os.walk(workdir):
            for f in files:
                full = os.path.join(root, f)
                z.write(full, os.path.relpath(full, workdir))

    result_zip.seek(0)

    return send_file(
        result_zip,
        as_attachment=True,
        download_name="VS2022_converted.zip",
        mimetype="application/zip"
    )


# MAIN
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
