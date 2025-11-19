const dropZone = document.getElementById("dropZone");
const folderInput = document.getElementById("folderInput");
const convertBtn = document.getElementById("convertBtn");

let selectedFiles = null;

// Enable button only when a folder is selected
function updateButtonState() {
    if (selectedFiles && selectedFiles.length > 0) {
        convertBtn.classList.add("enabled");
        convertBtn.style.cursor = "pointer";
    } else {
        convertBtn.classList.remove("enabled");
        convertBtn.style.cursor = "not-allowed";
    }
}

// Clicking the drop zone opens folder picker
dropZone.onclick = () => folderInput.click();

// Drag events
dropZone.addEventListener("dragover", e => {
    e.preventDefault();
    dropZone.style.background = "#eef";
});
dropZone.addEventListener("dragleave", () => {
    dropZone.style.background = "";
});
dropZone.addEventListener("drop", e => {
    e.preventDefault();
    dropZone.style.background = "";

    selectedFiles = e.dataTransfer.files;
    updateButtonState();
});

// File picker
folderInput.addEventListener("change", () => {
    selectedFiles = folderInput.files;
    updateButtonState();
});

// Button click = send files to backend
convertBtn.addEventListener("click", async () => {
    if (!convertBtn.classList.contains("enabled")) return;

    const formData = new FormData();
    for (let f of selectedFiles) formData.append("files", f);

    const response = await fetch("/convert", {
        method: "POST",
        body: formData
    });

    const blob = await response.blob();
    const url = URL.createObjectURL(blob);

    const a = document.createElement("a");
    a.href = url;
    a.download = "VS2022_Converted_Project.zip";
    a.click();
});

const fileInput = document.getElementById("fileInput");
const modeSelect = document.getElementById("modeSelect");

modeSelect.addEventListener("change", () => {
    if (modeSelect.value === "folder") {
        fileInput.setAttribute("webkitdirectory", "");
        fileInput.setAttribute("directory", "");
    } else {
        fileInput.removeAttribute("webkitdirectory");
        fileInput.removeAttribute("directory");
    }
});
