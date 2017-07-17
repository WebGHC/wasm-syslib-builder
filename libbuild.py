import os, sys
from subprocess import Popen
def main():
    # entire libc folders that are ignored
    ignoredModules = ['ipc', 'passwd', 'thread', 'signal', 'sched', 'ipc', 'time', 'linux', 'aio', 'exit', 'legacy', 'mq', 'process', 'search', 'setjmp', 'env', 'ldso', 'conf']

    # specific files that are ignored
    ignoredFiles = ['getaddrinfo.c', 'getnameinfo.c', 'inet_addr.c', 'res_query.c', 'gai_strerror.c', 'proto.c', 'gethostbyaddr.c', 'gethostbyaddr_r.c', 'gethostbyname.c', 'gethostbyname2_r.c', 'gethostbyname_r.c', 'gethostbyname2.c', 'usleep.c', 'alarm.c', 'syscall.c', '_exit.c']

    # questionable math files
    badMath = ['abs.c', 'sqrt.c', 'sqrtf.c', 'sqrtl.c', 'fabs.c', 'fabsf.c', 'fabsl.c', 'ceil.c', 'ceilf.c', 'ceill.c', 'floor.c', 'floorf.c', 'floorl.c', 'round.c', 'roundf.c']

    # abs path to here
    rootpath = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

    # abs path to libc code
    musl_srcdir = os.path.join(rootpath, 'emscripten', 'system', 'lib', 'libc', 'musl', 'src')

    # setup
    objs = os.path.join(rootpath, "obj")
    lib = os.path.join(rootpath, "lib")
    if not os.path.exists(objs):
        os.makedirs(objs)
    if not os.path.exists(lib):
        os.makedirs(lib)

    # get a ton of absolute paths that lead to the files we want to compile
    libc_files = [os.path.join(rootpath, "emscripten/system/lib/dlmalloc.c")]
    for dirpath, dirnames, filenames in os.walk(musl_srcdir):
      for f in filenames:
        if f.endswith('.c'):
          if f in ignoredFiles+badMath: continue
          dir_parts = os.path.split(dirpath)
          cancel = False
          for part in dir_parts:
            if part in ignoredModules:
              cancel = True
              break
          if not cancel:
            libc_files.append(os.path.join(musl_srcdir, dirpath, f))

    cc = os.getenv("CC")
    objectListing = []
    #build and execute the command a lot
    for f in libc_files:
        objectFile = os.path.join(objs, os.path.basename(f)[:-1]+'o')
        objectListing.append(objectFile)
        cmd = [cc, "-I", rootpath+"/emscripten/system/lib/libc/musl/src/internal", "-Os",
        "-Werror=implicit-function-declaration", "-Wno-return-type", "-Wno-parentheses",
        "-Wno-ignored-attributes", "-Wno-shift-count-overflow", "-Wno-shift-negative-value",
        "-Wno-dangling-else", "-Wno-unknown-pragmas", "-Wno-shift-op-parentheses", "-D", "__EMSCRIPTEN__",
        "-Wno-string-plus-int", "-Wno-logical-op-parentheses", "-Wno-bitwise-op-parentheses",
        "-Wno-visibility", "-Wno-pointer-sign", "-isystem"+rootpath+"/emscripten/system/include",
        "-isystem"+rootpath+"/emscripten/system/include/libc", "-v", "-isystem"+rootpath+"/emscripten/system/lib/libc/musl/arch/emscripten",
        "-c", "-o", objectFile, f]
        proc = Popen(cmd, stdout=sys.stdout)
        proc.communicate()
        if proc.returncode != 0:
            # Deliberately do not use CalledProcessError, see issue #2944
            raise Exception('Command \'%s\' returned non-zero exit status %s' % (' '.join(cmd), proc.returncode))

    ar = os.getenv("AR")
    arProc = Popen([ar, "rcs", os.path.join(lib, "libc.a")] + objectListing)
    arProc.communicate()

if __name__ == '__main__':
    main()
    sys.exit(0)
