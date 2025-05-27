add_rules("mode.debug", "mode.release")
add_requires("python 3.x")

includes("src")

target("c")
do
    set_prefixdir("$(xmake-prefix)/$(xmake-platlib)", {libdir = "example"})
    add_rules("python.library", "python.cython", { soabi = true })
    add_files("*.py")
    add_packages("python")

    add_installfiles("src/(example/*.py)")
    add_installfiles("README.md", {prefixdir= "$(xmake-data)/share/doc"})
    add_installfiles("pyproject.toml", {prefixdir= "$(xmake-metadata)"})
    add_installfiles("xmake.lua", {prefixdir= "$(xmake-null)"})
end
