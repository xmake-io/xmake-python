add_rules("mode.release", "mode.debug")
add_requires("pybind11")

target("example")
do
    set_prefixdir("$(xmake-prefix)/$(xmake-platlib)", { libdir = "" })
    add_rules("python.library", { soabi = true })
    add_files("*.cpp")
    add_packages("pybind11")
    set_languages("c++11")

    add_installfiles("README.md", {prefixdir= "$(xmake-data)/share/doc"})
    add_installfiles("pyproject.toml", {prefixdir= "$(xmake-metadata)"})
    add_installfiles("xmake.lua", {prefixdir= "$(xmake-null)"})
end
