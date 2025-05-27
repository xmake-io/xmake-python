add_rules("mode.debug", "mode.release")
add_requires("python 3.x")

target("our_first_module")
do
    set_prefixdir("$(xmake-prefix)/$(xmake-platlib)", { libdir = "our_first_project" })
    add_rules("python.library", { soabi = true })
    add_files("*.c")
    add_packages("python")

    add_installfiles("README.md", {prefixdir= "$(xmake-data)/share/doc"})
    add_installfiles("pyproject.toml", {prefixdir= "$(xmake-metadata)"})
    add_installfiles("xmake.lua", {prefixdir= "$(xmake-null)"})
end
