import os
from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.scm import Git
from conan.tools.files import copy, rm, rmdir, collect_libs

class DawnConan(ConanFile):
    name         = "dawn"
    version      = "7390"
    license      = "Apache-2.0"
    url          = "https://dawn.googlesource.com/dawn"
    description  = "Dawn is an open-source and cross-platform implementation of the WebGPU standard."
    topics       = ("conan", "dawn", "webgpu", "graphics", "gpu")

    settings     = "os", "compiler", "build_type", "arch"
    options      = {
        # backends
        "force_vulkan":     [True, False, None],
        "force_d3d12":      [True, False, None],
        "force_metal":      [True, False, None],
        "force_d3d11":      [True, False, None],
        "force_null":       [True, False, None],
        "force_desktop_gl": [True, False, None],
        "force_opengles":   [True, False, None],
        # sanitizers
        "force_asan":       [True, False, None],
        "force_tsan":       [True, False, None],
        "force_msan":       [True, False, None],
        "force_ubsan":      [True, False, None],
        # windowing
        "force_wayland":    [True, False, None],
        "force_x11":        [True, False, None],
        "force_glfw":       [True, False, None],
        # DXC toggle to avoid FXC (d3dcompiler_47.dll) dependency on Windows
        "force_dxc":        [True, False, None],
    }
    default_options = {
        "force_vulkan":      None,
        "force_d3d12":       None,
        "force_metal":       None,
        "force_d3d11":       None,
        "force_null":        None,
        "force_desktop_gl":  None,
        "force_opengles":    None,
        "force_asan":        None,
        "force_tsan":        None,
        "force_msan":        None,
        "force_ubsan":       None,
        "force_wayland":     None,
        "force_x11":         None,
        "force_glfw":        None,
        "force_dxc":         None,
    }

    generators = "CMakeDeps"

    def config_options(self):
        if self.settings.os == "Macos":
            if self.options.force_vulkan is None:
                self.options.force_vulkan = False
            if self.options.force_metal is None:
                self.options.force_metal = True

    def layout(self):
        cmake_layout(self)

    def source(self):
        git = Git(self)
        url = self.url
        branch = f"chromium/{self.version}"
        git.clone(url=url,
                  args=["--branch", branch,
                        "--single-branch",
                        "--depth=1"],
                  target=".")
        git.checkout(commit=branch)

    def generate(self):
        tc = CMakeToolchain(self, generator="Ninja")
        tc.cache_variables["DAWN_BUILD_MONOLITHIC_LIBRARY"]     = "SHARED"
        tc.cache_variables["DAWN_ENABLE_INSTALL"]               = "ON"
        tc.cache_variables["DAWN_FETCH_DEPENDENCIES"]           = "ON"
        tc.cache_variables["BUILD_SHARED_LIBS"]                 = "OFF"

        def _map(opt, var):
            val = self.options.get_safe(opt, None)
       
            if val is None:
                return
            if val is True:
                tc.cache_variables[var] = "ON"
            elif val is False:
                tc.cache_variables[var] = "OFF"

        # backends
        for opt, var in [
            ("force_vulkan",     "DAWN_ENABLE_VULKAN"),
            ("force_d3d12",      "DAWN_ENABLE_D3D12"),
            ("force_metal",      "DAWN_ENABLE_METAL"),
            ("force_d3d11",      "DAWN_ENABLE_D3D11"),
            ("force_null",       "DAWN_ENABLE_NULL"),
            ("force_desktop_gl", "DAWN_ENABLE_DESKTOP_GL"),
            ("force_opengles",   "DAWN_ENABLE_OPENGLES"),
        ]:
            _map(opt, var)

        # sanitizers
        for opt, var in [
            ("force_asan",  "DAWN_ENABLE_ASAN"),
            ("force_tsan",  "DAWN_ENABLE_TSAN"),
            ("force_msan",  "DAWN_ENABLE_MSAN"),
            ("force_ubsan", "DAWN_ENABLE_UBSAN"),
        ]:
            _map(opt, var)

        # windowing
        for opt, var in [
            ("force_wayland", "DAWN_USE_WAYLAND"),
            ("force_x11",     "DAWN_USE_X11"),
            ("force_glfw",    "DAWN_USE_GLFW"),
        ]:
            _map(opt, var)

        # DXC (avoids runtime load of d3dcompiler_47.dll by building & using DXC)
        _map("force_dxc", "DAWN_USE_BUILT_DXC")

        # disable tests/tools/samples to keep the package lean
        for f in (
            "TINT_BUILD_SPV_READER",
            "TINT_BUILD_CMD_TOOLS",
            "TINT_BUILD_TESTS",
            "TINT_BUILD_IR_BINARY",
            "DAWN_BUILD_SAMPLES",
            "DAWN_BUILD_TESTS",
        ):
            tc.cache_variables[f] = "OFF"

        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.set_property("cmake_target_name", "dawn::webgpu_dawn")
        self.cpp_info.libs = collect_libs(self)
