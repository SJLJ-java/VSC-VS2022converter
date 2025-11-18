import xml.etree.ElementTree as ET
import glob

VCXPROJ_FILE = "VScompress.vcxproj"

# find all code files
source_files = sorted(glob.glob("src/**/*.cpp", recursive=True))
header_files = sorted(glob.glob("src/**/*.h", recursive=True))

tree = ET.parse(VCXPROJ_FILE)
root = tree.getroot()

ns = {'ns': 'http://schemas.microsoft.com/developer/msbuild/2003'}

def ensure_file(group_xpath, tag, files):
    group = root.find(group_xpath, ns)
    if group is None:
        group = ET.SubElement(root, "ItemGroup")

    existing = {elem.attrib['Include'] for elem in group.findall(tag, ns)}

    for file in files:
        if file not in existing:
            elem = ET.SubElement(group, tag)
            elem.set("Include", file)

ensure_file(".//ns:ItemGroup", "ClCompile", source_files)
ensure_file(".//ns:ItemGroup", "ClInclude", header_files)

tree.write(VCXPROJ_FILE, encoding="utf-8", xml_declaration=True)