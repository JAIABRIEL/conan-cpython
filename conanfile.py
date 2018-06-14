import os
from conans import ConanFile, MSBuild, tools, AutoToolsBuildEnvironment


class CpythonConan(ConanFile):
    name = "cpython"
    version = "3.6.5"
    license = "PYTHON SOFTWARE FOUNDATION LICENSE VERSION 2"
    url = "<Package recipe repository url here, for issues about the package>"
    description = "<Description of Cpython here>"
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False]}
    default_options = "shared=True"
    generators = "cmake"

    def source(self):
        tools.get("https://github.com/python/cpython/archive/v%s.tar.gz" % self.version)

    def build(self):
        with tools.chdir(self.src_subfolder):
            if self.settings.os == "Windows":
                with tools.chdir("PCBuild"):
                    self.run("get_externals.bat")
                    msbuild = MSBuild(self)
                    msbuild.build("pcbuild.sln")
            else:
                atools = AutoToolsBuildEnvironment(self)
                args = ["--enable-shared"] if self.options.shared else []
                atools.configure(args=args)
                atools.make()

    def package(self):
        if self.settings.os != "Windows":
            with tools.chdir("cpython-%s" % self.version):
                atools = AutoToolsBuildEnvironment(self)
                atools.install()
        else:
            out_folder = {"x86_64": "amd64", "x86": "win32"}.get(str(self.settings.arch))
            src = os.path.join("cpython-%s" % self.version, "PCBuild", out_folder)
            self.copy(pattern="*.dll", dst="bin", src=src, keep_path=False)
            self.copy(pattern="*.lib", dst="lib", src=src, keep_path=False)
            self.copy(pattern="*.h", dst="include", src= os.path.join(self.src_subfolder, "Include"), keep_path=False)
            self.copy(pattern="*.h", dst="include", src=os.path.join("cpython-%s" % self.version, "PC"), keep_path=False)
            self.copy(pattern="*.exe", dst="bin", src=src, keep_path=False)

    def package_info(self):

        if self.settings.os != "Windows":
            name = "python%sm" % ".".join(self.version.split(".")[0:2])
            self.cpp_info.includedirs.append("include/%s" % name)
            self.cpp_info.libs.append(name)
            if self.settings.os == "Macos":
                self.cpp_info.libs.append("dl")
                self.cpp_info.exelinkflags.append("-framework CoreFoundation")
                self.cpp_info.sharedlinkflags = self.cpp_info.exelinkflags
            elif self.settings.os == "Linux":
                self.cpp_info.libs.extend(["pthread", "dl", "util"])
        else:
            self.cpp_info.libs = ["python%s" % self.version[0]]

    @property
    def src_subfolder(self):
        return os.path.join(self.source_folder, "cpython-%s" % self.version)

    def configure(self):
        if self.settings.os == "Windows" and self.options.shared == "False":
            raise Exception("Win static python lib is not supported")
