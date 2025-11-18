import xml.etree.ElementTree as ET
import glob
import os

FILTER_FILE = "VScompress.filters"

NS = "http://schemas.microsoft.com/developer/msbuild/2003"
ns = {"ns": NS}

# Create minimal .filters if missing
if not os.path.exists(FILTER_FILE):
    with open(FILTER_FILE, "w", encoding="utf-8") as f:
        f.write("""<?xml version="1.0" encoding="utf-8"?>
<Project ToolsVersion="4.0" xmlns="http://schemas.microsoft.com/developer/msbuild/2003">
  <ItemGroup>
  </ItemGroup>
</Project>
""")

tree = ET.parse(FILTER_FILE)
root = tree.getroot()

# Find or create an ItemGroup
group = root.find(".//ns:ItemGroup", ns)
if group is None:
    group = ET.SubElement(root, f"{{{NS}}}ItemGroup")

# Gather source/header files
source_files = sorted(glob.glob("src/**/*.cpp", recursive=True))
header_files = sorted(glob.glob("src/**/*.h", recursive=True))

def add_files(tag, files):
    existing = {elem.attrib['Include'] for elem in root.findall(f".//ns:{tag}", ns)}
    for f in files:
        if f in existing:
            continue
        elem = ET.SubElement(group, tag)
        elem.set("Include", f)
        folder = os.path.dirname(f).replace("/", "\\")
        if folder:
            f_elem = ET.SubElement(elem, "Filter")
            f_elem.text = folder

add_files("ClCompile", source_files)
add_files("ClInclude", header_files)

tree.write(FILTER_FILE, encoding="utf-8", xml_declaration=True)
