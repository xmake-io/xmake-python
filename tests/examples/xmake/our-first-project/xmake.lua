add_rules("mode.debug", "mode.release")
add_requires("python 3.x")

target("our_first_module")
do
    set_prefixdir("$(prefixdir)/$(pythondir)", { libdir = "our_first_project" })
    add_rules("python.library", { soabi = true })
    add_files("*.c")
    add_packages("python")

    add_installfiles("README.md", {prefixdir= "$(prefix)/share/doc"})
    add_installfiles("pyproject.toml", {prefixdir= "$(metadatadir)"})
    add_installfiles("xmake.lua", {prefixdir= "$(nulldir)"})
end
