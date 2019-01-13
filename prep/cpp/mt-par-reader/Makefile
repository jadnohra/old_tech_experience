CXX = g++

src = $(wildcard *.cpp)
obj = $(src:.cpp=.o)

CXXFLAGS = -std=c++11 -stdlib=libc++
LDFLAGS = -lc++

mt-par-reader: $(obj)
	$(CC) -o $@ $^ $(LDFLAGS)

.PHONY: clean
clean:
	rm -f $(obj) mt-par-reader
