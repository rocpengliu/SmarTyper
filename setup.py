from setuptools import setup, Extension
from Cython.Build import cythonize
import glob
from pathlib import Path
from setuptools.command.build_ext import build_ext as _build_ext


class build_ext(_build_ext):
    def run(self):
        super().run()
        # Remove transient object files that can appear in src/ after compilation.
        for obj_file in Path("src").glob("*.o"):
            try:
                obj_file.unlink()
            except OSError:
                pass

# Define compiler and linker flags.
extra_compile_args = ["-std=c++11", "-g"]
extra_link_args = ["-lstdc++", "-lz"]  # Assuming you need to link with zlib (-lz).

# Define macros to prevent the _Float128 etc. definitions.
define_macros = [
    ("__STDC_WANT_IEC_60559_TYPES_EXT__", "0"),
    ("__STDC_WANT_IEC_60559_FUNCS_EXT__", "0"),
    ("__STDC_WANT_IEC_60559_BFP_EXT__", "0"),
]

# Resolve glob patterns to actual file paths.
cpp_sources = glob.glob('src/*.cpp')

# Extension module.
extensions = [
    Extension(
        name="seqtyper_core",
        sources=["seqtyper_core.pyx"] + cpp_sources,
        include_dirs=[
                "src",
                "src/zlib"
            ],
        libraries=["z"],
        extra_compile_args=extra_compile_args,
        extra_link_args=extra_link_args,
        define_macros=define_macros,
        language="c++"
    )
]

# Setup configuration.
setup(
    name="seqtyper_project",
    ext_modules=cythonize(extensions, compiler_directives={'language_level': "3"}),
    cmdclass={"build_ext": build_ext},
)