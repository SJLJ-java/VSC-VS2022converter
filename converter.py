from flask import Flask, request, send_file
import os, zipfile, uuid, tempfile

app = Flask(__name__)

IGNORED_DIRS = {"bin", "obj", ".vscode", ".vs", "build", "out"}

VCXPROJ_TEMPLATE = r"""<?xml version="1.0" encoding="utf-8"?>
<Project DefaultTargets="Build" ToolsVersion="17.0" xmlns="http://schemas.microsoft.com/developer/msbuild/2003">
  <ItemGroup Label="ProjectConfigurations">
    <ProjectConfiguration Include="Debug|x64">
      <Configuration>Debug</Configuration>
      <Platform>x64</Platform>
    </ProjectConfiguration>
    <ProjectConfiguration Include="Release|x64">
      <Configuration>Release</Configuration>
      <Platform>x64</Platform>
    </ProjectConfiguration>
  </ItemGroup>

  <ItemGroup>
{SOURCES}
{HEADERS}
  </ItemGroup>

  <PropertyGroup Label="Globals">
    <VCProjectVersion>17.0</VCProjectVersion>
    <ProjectGuid>{GUID}</ProjectGuid>
    <Keyword>Win32Proj</Keyword>
    <WindowsTargetPlatformVersion>10.0</WindowsTargetPlatformVersion>
  </PropertyGroup>

  <Import Project="$(VCTargetsPath)\Microsoft.Cpp.Default.props" />
  <PropertyGroup Condition="'$(Configuration)|$(Platform)'=='Debug|x64'" Label="Configuration">
    <ConfigurationType>Application</ConfigurationType>
    <UseDebugLibraries>true</UseDebugLibraries>
    <PlatformToolset>v143</PlatformToolset>
    <CharacterSet>MultiByte</CharacterSet>
  </PropertyGroup>
  <PropertyGroup Condition="'$(Configuration)|$(Platform)'=='Release|x64'" Label="Configuration">
    <ConfigurationType>Application</ConfigurationType>
    <UseDebugLibraries>false</UseDebugLibraries>
    <PlatformToolset>v143</PlatformToolset>
    <CharacterSet>MultiByte</CharacterSet>
  </PropertyGroup>
  <Import Project="$(VCTargetsPath)\Microsoft.Cpp.props" />

</Project>
"""

SLN_TEMPLATE = """Microsoft Visual Studio Solution File, Format Version 12.00
# Visual Studio Version 17
VisualStudioVersion = 17.0.31903.59
MinimumVisualStudioVersion = 10.0.40219.1
Project("{{FAKEGUID}}") = "ConvertedProject", "ConvertedProject.vcxproj", "{GUID}"
EndProject
Global
    GlobalSection(SolutionConfigurationPlatforms) = preSolution
        Debug|x64 = Debug|x64
        Release|x64 = Release|x64
    EndGlobalSection
    GlobalSection(ProjectConfigurationPlatforms) = postSolution
        {GUID}.Debug|x64.ActiveCfg = Debug|x64
        {GUID}.Debug|x64.Build.0 = Debug|x64
        {GUID}.Release|x64.ActiveCfg = Release|x64
        {GUID}.Release|x64.Build.0 = Release|x64
    EndGlobalSection
EndGlobal
"""

def collect_files(files):
    cpp_files = []
    h_files = []

    for f in files:
        name = f.filename.replace("\\", "/")
        parts = name.split("/")

        # skip junk folders
        if any(p in IGNORED_DIRS for p in parts):
            continue

        if name.endswith(".cpp"):
            cpp_files.append(name)
        elif name.endswith(".h") or name.endswith(".hpp"):
            h_files.append(name)

    return cpp_files, h_files


@app.post("/convert")
def convert_folder():
    files = request.files.getlist("files")

    tempdir = tempfile.mkdtemp()
    proj_dir = os.path.join(tempdir, "ConvertedProject")
    os.makedirs(proj_dir)

    # Save all uploaded files
    for f in files:
        out = os.path.join(proj_dir, f.filename)
        os.makedirs(os.path.dirname(out), exist_ok=True)
        f.save(out)

    cpp_files, h_files = collect_files(files)

    # Generate vcxproj entries
    src_entries = "\n".join(f'    <ClCompile Include="{f}" />' for f in cpp_files)
    hdr_entries = "\n".join(f'    <ClInclude Include="{f}" />' for f in h_files)

    guid = "{" + str(uuid.uuid4()).upper() + "}"

    vcxproj_text = VCXPROJ_TEMPLATE.replace("{SOURCES}", src_entries).replace("{HEADERS}", hdr_entries).replace("{GUID}", guid)
    sln_text = SLN_TEMPLATE.replace("{GUID}", guid)

    # write vcxproj + sln
    with open(os.path.join(proj_dir, "ConvertedProject.vcxproj"), "w") as f:
        f.write(vcxproj_text)

    with open(os.path.join(proj_dir, "ConvertedProject.sln"), "w") as f:
        f.write(sln_text)

    # zip project
    zip_path = os.path.join(tempdir, "VS2022_Converted_Project.zip")
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
        for root, dirs, files in os.walk(proj_dir):
            for file in files:
                path = os.path.join(root, file)
                z.write(path, arcname=os.path.relpath(path, proj_dir))

    return send_file(zip_path, as_attachment=True)