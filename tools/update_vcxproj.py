import xml.etree.ElementTree as ET
import glob
import os

VCXPROJ_FILE = "VScompress.vcxproj"
NS = "http://schemas.microsoft.com/developer/msbuild/2003"
ns = {"ns": NS}

# Collect all existing real files
source_files = sorted(glob.glob("src/**/*.cpp", recursive=True))
header_files = sorted(glob.glob("src/**/*.h", recursive=True))

tree = ET.parse(VCXPROJ_FILE)
root = tree.getroot()

def sync_group(tag, real_files):
    """Remove missing files, add new ones, keep correct namespace."""

    groups = root.findall(".//ns:ItemGroup", ns)
    group = None

    # Locate the ItemGroup already containing this type
    for g in groups:
        if g.find(f"ns:{tag}", ns) is not None:
            group = g
            break

    # If missing, create a new ItemGroup
    if group is None:
        group = ET.SubElement(root, f"{{{NS}}}ItemGroup")

    # Find existing entries
    existing_elems = group.findall(f"ns:{tag}", ns)
    existing_paths = {e.attrib["Include"]: e for e in existing_elems}

    real_set = set(real_files)

    # REMOVE missing files
    for path, elem in list(existing_paths.items()):
        if path not in real_set:
            group.remove(elem)

    # ADD missing files
    for f in real_files:
        if f not in existing_paths:
            elem = ET.SubElement(group, f"{{{NS}}}{tag}")
            elem.set("Include", f)

# Sync both sections
sync_group("ClCompile", source_files)
sync_group("ClInclude", header_files)

tree.write(VCXPROJ_FILE, encoding="utf-8", xml_declaration=True)
