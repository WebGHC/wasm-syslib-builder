import os, sys
from subprocess import Popen
def main():
    # entire libc folders that are ignored
    ignoredModules = ['ipc', 'passwd', 'thread', 'signal', 'sched', 'ipc', 'time', 'linux', 'aio', 'exit', 'legacy', 'mq', 'process', 'search', 'setjmp', 'env', 'ldso', 'conf']

    # specific files that are ignored
    ignoredFiles = ['getaddrinfo.c', 'getnameinfo.c', 'inet_addr.c', 'res_query.c', 'gai_strerror.c', 'proto.c', 'gethostbyaddr.c', 'gethostbyaddr_r.c', 'gethostbyname.c', 'gethostbyname2_r.c', 'gethostbyname_r.c', 'gethostbyname2.c', 'usleep.c', 'alarm.c', 'syscall.c', '_exit.c']

    # abs path to here
    rootpath = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

    # abs path to libc code
    musl_srcdir = os.path.join(rootpath, 'system', 'lib', 'libc', 'musl', 'src')

    # get a ton of absolute paths that lead to the files we want to compile
    libc_files = []
    for dirpath, dirnames, filenames in os.walk(musl_srcdir):
      for f in filenames:
        if f.endswith('.c'):
          if f in ignoredFiles: continue
          dir_parts = os.path.split(dirpath)
          cancel = False
          for part in dir_parts:
            if part in ignoredModules:
              cancel = True
              break
          if not cancel:
            libc_files.append(os.path.join(musl_srcdir, dirpath, f))

    #build and execute the command a lot
    for f in libc_files:
        objectFile = os.path.basename(f)[:-1]+'o'
        cmd = ["clang", "-I", rootpath+"/system/lib/libc/musl/src/internal", "-Os",
        "-Werror=implicit-function-declaration", "-Werror", "-Wno-return-type", "-Wno-parentheses",
        "-Wno-ignored-attributes", "-Wno-shift-count-overflow", "-Wno-shift-negative-value",
        "-Wno-dangling-else", "-Wno-unknown-pragmas", "-Wno-shift-op-parentheses",
        "-Wno-string-plus-int", "-Wno-logical-op-parentheses", "-Wno-bitwise-op-parentheses",
        "-Wno-visibility", "-Wno-pointer-sign", "-isystem"+rootpath+"/system/include",
        "-isystem"+rootpath+"/system/include/libc", "-isystem"+rootpath+"/system/lib/libc/musl/arch/emscripten",
        "-o", rootpath+"/build/"+objectFile, f]

        Popen(cmd, stdout=sys.stdout)

if __name__ == '__main__':
    main()
    sys.exit(0)
