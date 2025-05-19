add_rules("mode.debug", "mode.release")
add_requires("python 3.x")

rule("python.cython")
    set_extensions(".py", ".pyx")

    on_load(function (target)
        local language = target:extraconf("rules", "python.cython", "language")
        if language == "c" then
            target:add("deps", "c")
        elseif language == "c++" then
            target:add("deps", "c++")
        end
    end)

    before_buildcmd_file(function (target, batchcmds, sourcefile, opt)
        import("lib.detect.find_tool")

        local cython = assert(find_tool("cython"), "cython not found! please `pip install cython`.")
        local language = target:extraconf("rules", "python.cython", "language")
        local ext = "c"
        local arg = "-3"
        if language == "c++" then
            ext = "cc"
            arg = arg .. "+"
        end
        local dirname = path.join(target:autogendir(), "rules", "python", "cython")
        local sourcefile_c = path.join(dirname, path.basename(sourcefile) .. "." .. ext)

        -- add objectfile
        local objectfile = target:objectfile(sourcefile_c)
        table.insert(target:objectfiles(), objectfile)

        -- add commands
        batchcmds:show_progress(opt.progress, "${color.build.object}compiling.python %s", sourcefile)
        batchcmds:mkdir(path.directory(sourcefile_c))
        batchcmds:vrunv(cython.program, {arg, "-o", path(sourcefile_c), path(sourcefile)})
        batchcmds:compile(sourcefile_c, objectfile)

        -- add deps
        batchcmds:add_depfiles(sourcefile)
        batchcmds:set_depmtime(os.mtime(objectfile))
        batchcmds:set_depcache(target:dependfile(objectfile))
    end)

target("c")
set_prefixdir("/", {libdir = "src/example"})
add_rules("python.library", "python.cython", { soabi = true })
add_files("c.py")
add_packages("python")
