from flask import Flask, render_template, request, redirect, url_for
import os

app = Flask(__name__)

# Set paths
UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "converted"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload():
    if "file" not in request.files:
        return "No file part", 400

    file = request.files["file"]

    if file.filename == "":
        return "No selected file", 400

    # Save uploaded file
    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)

    # TODO: Call your conversion logic here
    # For example:
    # output_file = run_conversion(filepath)

    return redirect(url_for("done"))


@app.route("/done")
def done():
    return "Conversion complete!"


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)