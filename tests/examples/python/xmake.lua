add_rules("mode.release", "mode.debug")

target("example")
set_kind("phony")
add_installfiles("*.py", {prefixdir= "$(xmake-platlib)"})
