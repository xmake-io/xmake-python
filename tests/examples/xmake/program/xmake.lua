add_rules("mode.release", "mode.debug")

target("main")
do
    set_kind("binary")
    add_files("*.c")

    add_installfiles("main.py", { prefixdir = "$(bindir)" })
    -- by default, prefixdir is $(prefix)
    -- so it can be ignored except you call set_prefixdir()
    add_installfiles("README.md", { prefixdir = "share/doc" })
    add_installfiles("example.py", { prefixdir = "$(pythondir)" })
    add_installfiles("pyproject.toml", { prefixdir = "$(metadatadir)" })
    add_installfiles("xmake.lua", { prefixdir = "$(nulldir)" })

    set_configvar("version", "$(project_version)")
    add_configfiles("main.h.in")
    add_includedirs("$(buildir)")
    add_installfiles("$(buildir)/main.h", { prefixdir = "$(includedir)" })
end
