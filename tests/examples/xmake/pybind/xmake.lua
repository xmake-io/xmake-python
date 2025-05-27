add_rules("mode.release", "mode.debug")
add_requires("pybind11")

target("example")
do
    set_prefixdir("$(prefixdir)/$(pythondir)", { libdir = "" })
    add_rules("python.library", { soabi = true })
    add_files("*.cpp")
    add_packages("pybind11")
    set_languages("c++11")

    add_installfiles("README.md", {prefixdir= "$(prefix)/share/doc"})
    add_installfiles("pyproject.toml", {prefixdir= "$(metadatadir)"})
    add_installfiles("xmake.lua", {prefixdir= "$(nulldir)"})
end
