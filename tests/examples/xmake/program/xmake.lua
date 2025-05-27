add_rules("mode.release", "mode.debug")

target("main")
do
    set_kind("binary")
    add_files("*.c")

    add_installfiles("main.py", { prefixdir = "$(xmake-scripts)" })
    add_installfiles("*.h", { prefixdir = "$(xmake-headers)" })
    -- by default, prefixdir is $(xmake-data)
    -- so it can be ignored except you call set_prefixdir()
    add_installfiles("README.md", { prefixdir = "share/doc" })
    add_installfiles("example.py", { prefixdir = "$(xmake-platlib)" })
    add_installfiles("pyproject.toml", { prefixdir = "$(xmake-metadata)" })
    add_installfiles("xmake.lua", { prefixdir = "$(xmake-null)" })
end
