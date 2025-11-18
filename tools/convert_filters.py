import xml.etree.ElementTree as ET
import glob
import os

FILTER_FILE = "VScompress.filters"
NS = "http://schemas.microsoft.com/developer/msbuild/2003"
ns = {"ns": NS}

# Gather files
source_files = sorted(glob.glob("src/**/*.cpp", recursive=True))
header_files = sorted(glob.glob("src/**/*.h", recursive=True))

tree = ET.parse(FILTER_FILE)
root = tree.getroot()

def add_files(tag, files):
    # Find an existing ItemGroup
    group = root.find(".//ns:ItemGroup", ns)
    if group is None:
        # Create one if missing
        group = ET.SubElement(root, f"{{{NS}}}ItemGroup")

    existing = {elem.attrib['Include'] for elem in root.findall(f".//ns:{tag}", ns)}
    for f in files:
        if f in existing:
            continue

        elem = ET.SubElement(group, tag)
        elem.set("Include", f)

        # filter folder = path without filename
        folder = os.path.dirname(f).replace("/", "\\")
        if folder:
            f_elem = ET.SubElement(elem, "Filter")
            f_elem.text = folder


add_files("ClCompile", source_files)
add_files("ClInclude", header_files)

tree.write(FILTER_FILE, encoding="utf-8", xml_declaration=True)
