import os, sys
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

    

if __name__ == '__main__':
    main()
    sys.exit(0)
