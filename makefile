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
WASMOBJS := $(addprefix ./obj/, $(addsuffix .o, $(WASMLIBCNAMES)))

vpath %.c $(sort $(dir $(WASMLIBCFILES)))

test:
	echo $(words $(CANDIDATEFILES))
	echo $(words $(IGNOREDFILES))
	echo $(words $(WASMLIBCFILES))


obj lib:
	mkdir $@

$(WASMOBJS):./obj/%.o: %.c | obj
	


.PHONY: all
all: $(WASMOBJS) | obj lib

.PHONY: clean
clean:
	rm -rf lib
	rm -rf obj
