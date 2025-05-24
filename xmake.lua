target("phony")
do
    set_kind("phony")
    add_installfiles("src/xmake_python/*.py", { prefixdir = "$(xmake-platlib)/xmake_python" })
    add_installfiles("src/xmake_python/builder/*.py", { prefixdir = "$(xmake-platlib)/xmake_python/builder" })
    add_installfiles("src/xmake_python/templates/xmake.lua", { prefixdir = "$(xmake-platlib)/xmake_python/templates" })

    set_configvar("version", "$(xmake-version)")
    add_configfiles("src/xmake_python/templates/__init__.py")
    add_installfiles("$(buildir)/*.py", { prefixdir = "$(xmake-platlib)/xmake_python/templates" })
end
