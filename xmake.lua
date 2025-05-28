target("phony")
do
    set_kind("phony")
    add_installfiles("src/xmake_python/*.py", { prefixdir = "$(pythondir)/xmake_python" })
    add_installfiles("src/xmake_python/builder/*.py", { prefixdir = "$(pythondir)/xmake_python/builder" })
    add_installfiles("src/xmake_python/templates/xmake.lua", { prefixdir = "$(pythondir)/xmake_python/templates" })
    add_installfiles("src/xmake_python/templates/Makefile", { prefixdir = "$(pythondir)/xmake_python/templates" })

    set_configvar("version", "$(project_version)")
    add_configfiles("src/xmake_python/templates/__init__.py")
    add_installfiles("$(buildir)/*.py", { prefixdir = "$(pythondir)/xmake_python/templates" })
end
