.DEFAULT_GOAL := all

PATHTOMUSLSRC := ./emscripten/system/lib/libc/musl/src
MUSLMODULES := $(shell find $(PATHTOMUSLSRC) -mindepth 1 -maxdepth 1 -type d)

IGNOREDMODULES := ipc passwd thread signal sched ipc time linux aio exit legacy mq process search setjmp env ldso conf
IGNOREDFILES := getaddrinfo.c getnameinfo.c inet_addr.c res_query.c gai_strerror.c proto.c gethostbyaddr.c gethostbyaddr_r.c gethostbyname.c gethostbyname2_r.c gethostbyname_r.c gethostbyname2.c usleep.c alarm.c syscall.c _exit.c

PROCESSEDMODULES := $(filter-out $(addprefix %/, $(IGNOREDMODULES)), $(MUSLMODULES))
CANDIDATEFILES := $(foreach module, $(PROCESSEDMODULES), $(shell find $(module) -name '*.c'))
PATHTODLMALLOC := ./emscripten/system/lib/dlmalloc.c
WASMLIBCFILES := $(PATHTODLMALLOC) $(filter-out $(addprefix %/, $(IGNOREDFILES)), $(CANDIDATEFILES))

WASMLIBCNAMES := $(notdir $(basename $(WASMLIBCFILES)))
WASMOBJS := $(addprefix obj/, $(addsuffix .o, $(WASMLIBCNAMES)))

vpath %.c $(sort $(dir $(WASMLIBCFILES)))

HEADERS := $(shell find ./emscripten/system/include -mindepth 1 -maxdepth 1 -name '*.h') $(shell find ./emscripten/system/include/libc -mindepth 1 -name '*.h') $(shell find ./emscripten/system/lib/libc/musl -mindepth 1 -name '*.h' )
HEADERHOMES := $(sort $(dir $(subst /lib/libc/musl,, $(subst /emscripten/system,, $(HEADERS) ))))

obj lib include:
	mkdir $@

$(HEADERHOMES):
	mkdir -p ./include/$@


$(HEADERS): %.h: %.h | include $(HEADERHOMES)
	cp $@ ./include/$(subst /lib/libc/musl,, $(subst /emscripten/system,, $@ ))

$(WASMOBJS): obj/%.o: %.c $(HEADERS)| obj
	@$$CC -I ./emscripten/system/lib/libc/musl/src/internal -Os \
	-Werror=implicit-function-declaration -Wno-return-type -Wno-parentheses \
	-Wno-ignored-attributes -Wno-shift-count-overflow -Wno-shift-negative-value \
	-Wno-dangling-else -Wno-unknown-pragmas -Wno-shift-op-parentheses -D __EMSCRIPTEN__ \
	-Wno-string-plus-int -Wno-logical-op-parentheses -Wno-bitwise-op-parentheses \
	-Wno-visibility -Wno-pointer-sign -isystem ./emscripten/system/include -mthread-model single \
	-isystem ./emscripten/system/include/libc -isystem ./emscripten/system/lib/libc/musl/arch/emscripten \
	-c -o $@ $<

lib/libc.a: $(WASMOBJS) | lib
	@$$AR rcs $@ $(WASMOBJS)

.PHONY: all
all: lib/libc.a

.PHONY: clean
clean:
	rm -rf lib
	rm -rf obj
	rm -rf include
