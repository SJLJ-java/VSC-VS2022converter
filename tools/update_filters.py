import xml.etree.ElementTree as ET
import glob
import os

FILTER_FILE = "VScompress.filters"

source_files = sorted(glob.glob("src/**/*.cpp", recursive=True))
header_files = sorted(glob.glob("src/**/*.h", recursive=True))

tree = ET.parse(FILTER_FILE)
root = tree.getroot()

ns = {'ns': 'http://schemas.microsoft.com/developer/msbuild/2003'}

def add_files(tag, files):
    existing = {elem.attrib['Include'] for elem in root.findall(f".//ns:{tag}", ns)}

    for f in files:
        if f in existing:
            continue

        groups = root.findall(".//ns:ItemGroup", ns)
        if tag == "ClCompile":
            group = groups[-2]
        else:
            group = groups[-1]

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
