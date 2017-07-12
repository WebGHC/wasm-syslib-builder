# wasm-syslib-builder
Many wasm-backend style projects are dependent on system libraries like libc. Emscripten has a port of libc that builds to Webassembly. This project's aim is to provide a streamlined builder of Emscripten's libc (and eventually the other libraries Emscripten furnishes) such that wasm-backend project don't need to rely on all of Emscripten as a dependency.
