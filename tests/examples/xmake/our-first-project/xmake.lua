add_rules("mode.debug", "mode.release")
add_requires("python 3.x")

target("our_first_module")
set_prefixdir("/", { libdir = "$(xmake-platlib)/our_first_project" })
add_rules("python.library", { soabi = true })
add_files("*.c")
add_packages("python")
