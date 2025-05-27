add_rules("mode.release", "mode.debug")
add_requires("pybind11")

target("example")
set_prefixdir("/", { libdir = "$(xmake-platlib)/example" })
add_rules("python.library", { soabi = true })
add_files("*.cpp")
add_packages("pybind11")
set_languages("c++11")
