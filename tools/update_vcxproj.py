import xml.etree.ElementTree as ET
import glob
import os

VCXPROJ_FILE = "VScompress.vcxproj"
NS = "http://schemas.microsoft.com/developer/msbuild/2003"
ns = {"ns": NS}

# Ensure VCXPROJ exists
if not os.path.exists(VCXPROJ_FILE):
    with open(VCXPROJ_FILE, "w", encoding="utf-8") as f:
        f.write("""<?xml version="1.0" encoding="utf-8"?>
<Project DefaultTargets="Build" xmlns="http://schemas.microsoft.com/developer/msbuild/2003">
  <ItemGroup>
  </ItemGroup>
</Project>
""")

# Gather all source/header files
source_files = sorted(glob.glob("src/**/*.cpp", recursive=True))
header_files = sorted(glob.glob("src/**/*.h", recursive=True))

tree = ET.parse(VCXPROJ_FILE)
root = tree.getroot()

def sync_group(tag, real_files):
    groups = root.findall(".//ns:ItemGroup", ns)
    group = None
    for g in groups:
        if g.find(f"ns:{tag}", ns) is not None:
            group = g
            break
    if group is None:
        group = ET.SubElement(root, f"{{{NS}}}ItemGroup")

    # Existing entries
    existing_elems = group.findall(f"ns:{tag}", ns)
    existing_paths = {e.attrib["Include"]: e for e in existing_elems}
    real_set = set(real_files)

    # Remove missing files
    for path, elem in list(existing_paths.items()):
        if path not in real_set:
            group.remove(elem)

    # Add new files
    for f in real_files:
        if f not in existing_paths:
            elem = ET.SubElement(group, f"{{{NS}}}{tag}")
            elem.set("Include", f)

sync_group("ClCompile", source_files)
sync_group("ClInclude", header_files)

tree.write(VCXPROJ_FILE, encoding="utf-8", xml_declaration=True)
