CXX = g++

src = $(wildcard *.cpp)
obj = $(src:.cpp=.o)

CXXFLAGS = -std=c++11 -stdlib=libc++
LDFLAGS = -lc++ -lboost_program_options 

semaphore-impl: $(obj)
	$(CC) -o $@ $^ $(LDFLAGS)

.PHONY: clean
clean:
	rm -f $(obj) semaphore-impl
