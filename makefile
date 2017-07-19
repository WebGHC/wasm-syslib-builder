

obj lib :
	mkdir $@

all : | lib obj

.PHONY : clean
clean:
	rm -rf lib
	rm -rf obj
