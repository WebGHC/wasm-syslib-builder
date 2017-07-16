import os, json, logging, zipfile, glob
import shared
from subprocess import Popen, CalledProcessError
import subprocess, multiprocessing, re
from sys import maxint
from tools.shared import check_call

stdout = None
stderr = None

def call_process(cmd):
  proc = Popen(cmd, stdout=stdout, stderr=stderr)
  proc.communicate()
  if proc.returncode != 0:
    # Deliberately do not use CalledProcessError, see issue #2944
    raise Exception('Command \'%s\' returned non-zero exit status %s' % (' '.join(cmd), proc.returncode))

CORES = int(os.environ.get('EMCC_CORES') or multiprocessing.cpu_count())

def run_commands(commands):
  cores = min(len(commands), CORES)
  if cores <= 1:
    for command in commands:
      call_process(command)
  else:
    pool = multiprocessing.Pool(processes=cores)
    # https://stackoverflow.com/questions/1408356/keyboard-interrupts-with-pythons-multiprocessing-pool, https://bugs.python.org/issue8296
    pool.map_async(call_process, commands, chunksize=1).get(maxint)

def calculate(temp_files, in_temp, stdout_, stderr_, forced=[]):
  global stdout, stderr
  stdout = stdout_
  stderr = stderr_

  # Check if we need to include some libraries that we compile. (We implement libc ourselves in js, but
  # compile a malloc implementation and stdlibc++.)

  def read_symbols(path):
    with open(path) as f:
      return shared.Building.parse_symbols(f.read()).defs

  default_opts = ['-Werror']

  # XXX We also need to add libc symbols that use malloc, for example strdup. It's very rare to use just them and not
  #     a normal malloc symbol (like free, after calling strdup), so we haven't hit this yet, but it is possible.
  libc_symbols = read_symbols(shared.path_from_root('system', 'lib', 'libc.symbols'))
  libcxx_symbols = read_symbols(shared.path_from_root('system', 'lib', 'libcxx', 'symbols'))
  libcxxabi_symbols = read_symbols(shared.path_from_root('system', 'lib', 'libcxxabi', 'symbols'))
  gl_symbols = read_symbols(shared.path_from_root('system', 'lib', 'gl.symbols'))
  compiler_rt_symbols = read_symbols(shared.path_from_root('system', 'lib', 'compiler-rt.symbols'))
  pthreads_symbols = read_symbols(shared.path_from_root('system', 'lib', 'pthreads.symbols'))
  wasm_libc_symbols = read_symbols(shared.path_from_root('system', 'lib', 'wasm-libc.symbols'))

  # XXX we should disable EMCC_DEBUG when building libs, just like in the relooper

  def build_libc(lib_filename, files, lib_opts):
    o_s = []
    musl_internal_includes = ['-I', shared.path_from_root('system', 'lib', 'libc', 'musl', 'src', 'internal'), '-I', shared.path_from_root('system', 'lib', 'libc', 'musl', 'arch', 'js')]
    commands = []
    # Hide several musl warnings that produce a lot of spam to unit test build server logs.
    # TODO: When updating musl the next time, feel free to recheck which of their warnings might have been fixed, and which ones of these could be cleaned up.
    c_opts = ['-Wno-return-type', '-Wno-parentheses', '-Wno-ignored-attributes', '-Wno-shift-count-overflow', '-Wno-shift-negative-value', '-Wno-dangling-else', '-Wno-unknown-pragmas', '-Wno-shift-op-parentheses', '-Wno-string-plus-int', '-Wno-logical-op-parentheses', '-Wno-bitwise-op-parentheses', '-Wno-visibility', '-Wno-pointer-sign']
    if shared.Settings.WASM_BACKEND:
      c_opts.append('-Wno-error=absolute-value')
    for src in files:
      o = in_temp(os.path.basename(src) + '.o')
      commands.append([shared.PYTHON, shared.EMCC, shared.path_from_root('system', 'lib', src), '-o', o] + musl_internal_includes + default_opts + c_opts + lib_opts)
      o_s.append(o)
    run_commands(commands)
    shared.Building.link(o_s, in_temp(lib_filename))
    return in_temp(lib_filename)

  def build_libcxx(src_dirname, lib_filename, files, lib_opts, has_noexcept_version=False):
    o_s = []
    commands = []
    opts = default_opts + lib_opts
    if has_noexcept_version and shared.Settings.DISABLE_EXCEPTION_CATCHING:
      opts += ['-fno-exceptions']
    for src in files:
      o = in_temp(src + '.o')
      srcfile = shared.path_from_root(src_dirname, src)
      commands.append([shared.PYTHON, shared.EMXX, srcfile, '-o', o, '-std=c++11'] + opts)
      o_s.append(o)
    run_commands(commands)
    if lib_filename.endswith('.bc'):
      shared.Building.link(o_s, in_temp(lib_filename))
    elif lib_filename.endswith('.a'):
      shared.Building.emar('cr', in_temp(lib_filename), o_s)
    else:
      raise Exception('unknown suffix ' + lib_filename)
    return in_temp(lib_filename)

  # libc
  def create_libc(libname):
    logging.debug(' building libc for cache')
    libc_files = [
    ]
    musl_srcdir = shared.path_from_root('system', 'lib', 'libc', 'musl', 'src')
    blacklist = set(
      ['ipc', 'passwd', 'thread', 'signal', 'sched', 'ipc', 'time', 'linux', 'aio', 'exit', 'legacy', 'mq', 'process', 'search', 'setjmp', 'env', 'ldso', 'conf'] + # musl modules
      ['memcpy.c', 'memset.c', 'memmove.c', 'getaddrinfo.c', 'getnameinfo.c', 'inet_addr.c', 'res_query.c', 'gai_strerror.c', 'proto.c', 'gethostbyaddr.c', 'gethostbyaddr_r.c', 'gethostbyname.c', 'gethostbyname2_r.c', 'gethostbyname_r.c', 'gethostbyname2.c', 'usleep.c', 'alarm.c', 'syscall.c'] + # individual files
      ['abs.c', 'cos.c', 'cosf.c', 'cosl.c', 'sin.c', 'sinf.c', 'sinl.c', 'tan.c', 'tanf.c', 'tanl.c', 'acos.c', 'acosf.c', 'acosl.c', 'asin.c', 'asinf.c', 'asinl.c', 'atan.c', 'atanf.c', 'atanl.c', 'atan2.c', 'atan2f.c', 'atan2l.c', 'exp.c', 'expf.c', 'expl.c', 'log.c', 'logf.c', 'logl.c', 'sqrt.c', 'sqrtf.c', 'sqrtl.c', 'fabs.c', 'fabsf.c', 'fabsl.c', 'ceil.c', 'ceilf.c', 'ceill.c', 'floor.c', 'floorf.c', 'floorl.c', 'pow.c', 'powf.c', 'powl.c', 'round.c', 'roundf.c'] # individual math files
    )
    # TODO: consider using more math code from musl, doing so makes box2d faster
    for dirpath, dirnames, filenames in os.walk(musl_srcdir):
      for f in filenames:
        if f.endswith('.c'):
          if f in blacklist: continue
          dir_parts = os.path.split(dirpath)
          cancel = False
          for part in dir_parts:
            if part in blacklist:
              cancel = True
              break
          if not cancel:
            libc_files.append(os.path.join(musl_srcdir, dirpath, f))
    args = ['-Os']
    if shared.Settings.USE_PTHREADS:
      args += ['-s', 'USE_PTHREADS=1']
      assert '-mt' in libname
    else:
      assert '-mt' not in libname
    return build_libc(libname, libc_files, args)
