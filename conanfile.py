import os
import glob
from conan import ConanFile
from conan.tools.cmake import CMakeToolchain, CMake, cmake_layout
from conan.tools.files import copy
from conan.tools.scm import Git
from conan.tools.files import collect_libs

class DawnConan(ConanFile):
    name = "dawn"
    version = "7069"

    author = "Dawn Authors"
    description = "Dawn is an open-source and cross-platform implementation of the WebGPU standard."
    topics = ("conan", "dawn", "webgpu", "graphics", "gpu")

    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}
    exports_sources = "AUTHORS", "LICENSE"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def layout(self):
        cmake_layout(self)

    def source(self):
        git = Git(self)
        clone_args = ['--branch', f"chromium/7069"]
        git.clone(url="https://dawn.googlesource.com/dawn",
                  args=clone_args, target=".")

    def generate(self):
        tc = CMakeToolchain(self, generator="Ninja")
        tc.variables["WEBGPU_LINK_TYPE"] = "SHARED"
        tc.variables["DAWN_ENABLE_INSTALL"] = "ON"
        
        tc.variables["DAWN_FETCH_DEPENDENCIES"] = "ON"
        
        if self.settings.os == "Macos":
            tc.variables["USE_VULKAN"] = "OFF"
            tc.variables["USE_METAL"] = "ON"
        else:
            tc.variables["USE_VULKAN"] = "ON"
            tc.variables["USE_METAL"] = "OFF"
        
        tc.variables["DAWN_ENABLE_D3D11"] = "OFF"
        tc.variables["DAWN_ENABLE_D3D12"] = "OFF"
        tc.variables["DAWN_ENABLE_NULL"] = "OFF"
        tc.variables["DAWN_ENABLE_DESKTOP_GL"] = "OFF"
        tc.variables["DAWN_ENABLE_OPENGLES"] = "OFF"
        tc.variables["DAWN_ENABLE_VULKAN"] = tc.variables["USE_VULKAN"]
        
        tc.variables["TINT_BUILD_SPV_READER"] = "OFF"
        tc.variables["TINT_BUILD_CMD_TOOLS"] = "OFF"
        tc.variables["TINT_BUILD_TESTS"] = "OFF"
        tc.variables["TINT_BUILD_IR_BINARY"] = "OFF"
        
        tc.variables["DAWN_BUILD_SAMPLES"] = "OFF"
        
        tc.generate()

    def build(self):
        cmake = CMake(self)

        if self.settings.os == "Windows":
            cmake.configure(variables={
                "CMAKE_CXX_FLAGS": "/utf-8"
            })
        else:
            cmake.configure()
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.set_property("cmake_target_name", "dawn::webgpu_dawn")
        self.cpp_info.libs = ["webgpu_dawn"]

