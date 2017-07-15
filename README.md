# wasm-syslib-builder

## Purpose
Many wasm-backend style projects are dependent on system libraries like libc. Emscripten has a port of libc that builds to Webassembly. This project's aim is to provide a streamlined builder of Emscripten's libc (and eventually the other libraries Emscripten furnishes) such that wasm-backend projects don't need to rely on all of Emscripten as a dependency.

## Usage
Not ready (yet)

## Notes
* emscripten's port of libc is not a full port. It just is enough to allow for the compilation and linking of useful programs
* any library that is dependent on libc dynamically becomes dependent on `wasm-libc` if building for wasm in emscripten (which all projects using this repo are)
* `wasm-libc` is basically just a bunch of math functions that are excluded when compiling to asm.js (since they can just reach out to javascript math functions instead)

## Emscripten Library Info Table

libname | built extension | builder function | symbols variable name | dependencies
--------|--------|--------|--------|--------|
'libcxx' |                       'a' |  create_libcxx |                          libcxx_symbols |       ['libcxxabi']
'libcxxabi' |                    'bc' | create_libcxxabi |                       libcxxabi_symbols |    ['libc']
'gl' |                           'bc' | create_gl |                              gl_symbols |           ['libc']
'compiler-rt' |                  'a' |  create_compiler_rt |                     compiler_rt_symbols |  ['libc']
'libc-mt' |                      'bc' | create_libc |                            libc_symbols |         []
'pthreads' |                     'bc' | create_pthreads |                        pthreads_symbols |     ['libc']
'dlmalloc_threadsafe' |          'bc' | create_dlmalloc_multithreaded |          [] |                   []
'dlmalloc_threadsafe_tracing' |  'bc' | create_dlmalloc_multithreaded_tracing |  [] |                   []
'libc' |                         'bc' | create_libc |                            libc_symbols |         []
'dlmalloc_tracing' |             'bc' | create_dlmalloc_singlethreaded_tracing | [] |                   []
'dlmalloc_split' |               'bc' | create_dlmalloc_split |                  [] |                   []
'dlmalloc' |                     'bc' | create_dlmalloc_singlethreaded |         [] |                   []
'wasm-libc' |                    'bc' | create_wasm_libc |                       wasm_libc_symbols |    []
