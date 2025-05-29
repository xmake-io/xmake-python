add_rules("mode.debug", "mode.release")
add_requires("python 3.x")

target("c")
do
    set_prefixdir("$(prefixdir)/$(pythondir)", {libdir = "example"})
    add_rules("python.cython")
    add_files("*.py")
    add_packages("python")

    add_installfiles("src/(example/*.py)")
    add_installfiles("README.md", {prefixdir= "$(prefix)/share/doc"})
    add_installfiles("pyproject.toml", {prefixdir= "$(metadatadir)"})
    add_installfiles("xmake.lua", {prefixdir= "$(nulldir)"})
end
