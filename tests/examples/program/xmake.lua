add_rules("mode.release", "mode.debug")

target("main")
do
    set_kind("binary")
    add_files("*.c")
    add_installfiles("main.py", { prefixdir = "$(xmake-scripts)" })
    add_installfiles("*.h", { prefixdir = "$(xmake-headers)" })
    add_installfiles("README.md", { prefixdir = "$(xmake-data)/share/doc" })
    add_installfiles("example.py", { prefixdir = "$(xmake-platlib)" })
    add_installfiles("pyproject.toml", { prefixdir = "$(xmake-metadata)" })
    add_installfiles("xmake.lua", { prefixdir = "$(xmake-null)" })
end
