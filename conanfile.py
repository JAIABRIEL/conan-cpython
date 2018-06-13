import os
from conans import ConanFile, MSBuild, tools, AutoToolsBuildEnvironment


class CpythonConan(ConanFile):
    name = "cpython"
    version = "3.6.5"
    license = "<Put the package license here>"
    url = "<Package recipe repository url here, for issues about the package>"
    description = "<Description of Cpython here>"
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False]}
    default_options = "shared=False"
    generators = "cmake"

    def source(self):
        tools.get("https://github.com/python/cpython/archive/v%s.tar.gz" % self.version)

    @property
    def src_subfolder(self):
        return os.path.join(self.source_folder, "cpython-%s" % self.version)

    def build(self):
        with tools.chdir(self.src_subfolder):
            if self.settings.os == "Windows":
                self.run(r".\PCBuild\build.bat")
                msbuild = MSBuild(self)
                msbuild.build("PCBuild/pcbuild.sln")
            else:
                atools = AutoToolsBuildEnvironment(self)
                args = ["--enable-shared"] if self.options.shared else []
                atools.configure(args=args)
                atools.make()

    def package(self):
        with tools.chdir(self.src_subfolder):
            atools = AutoToolsBuildEnvironment(self)
            atools.install()

    def package_info(self):
        name = "python%sm" % ".".join(self.version.split(".")[0:2])
        self.cpp_info.includedirs.append("include/%s" % name)
        self.cpp_info.libs = [name]
        if self.settings.os == "Macos":
            self.cpp_info.libs.append("dl")
            self.cpp_info.exelinkflags.append("-framework CoreFoundation")
            self.cpp_info.sharedlinkflags = self.cpp_info.exelinkflags
