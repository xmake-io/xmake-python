target("phony")
do
    set_kind("phony")
    add_installfiles("src/xmake_python/*.py", { prefixdir = "$(xmake-platlib)/xmake_python" })
    add_installfiles("src/xmake_python/builder/*.py", { prefixdir = "$(xmake-platlib)/xmake_python/builder" })
    add_installfiles("src/xmake_python/template/*", { prefixdir = "$(xmake-platlib)/xmake_python/template" })
end
