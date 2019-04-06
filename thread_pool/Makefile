CXXFLAGS= -std=c++11 -Iinclude -Wall -Werror -pthread -g

pqsort: bin/thread_pool.o bin/pqsort.o bin/main.o
	g++ $(CXXFLAGS) bin/thread_pool.o bin/pqsort.o bin/main.o -o pqsort

bin/thread_pool.o: src/thread_pool.cpp include/thread_pool.h | bin
	g++ $(CXXFLAGS) -c src/thread_pool.cpp -o bin/thread_pool.o

bin/pqsort.o: src/pqsort.cpp include/pqsort.h include/thread_pool.h | bin
	g++ $(CXXFLAGS) -c src/pqsort.cpp -o bin/pqsort.o

bin/main.o: src/main.cpp include/thread_pool.h include/pqsort.h | bin
	g++ $(CXXFLAGS) -c src/main.cpp -o bin/main.o

bin:
	mkdir bin

clean:
	rm -rf bin pqsort
