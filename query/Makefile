.PHONY: all clean
FILES=query.c

all: query_build

query_build:
	g++ $(FILES) -o query


clean:
	rm -rf ./unsorted
	mkdir -p ./unsorted
	rm -rf ./out_sorted
	mkdir out_sorted
	rm -f query
	rm -f sorted_output.bin
	rm -f easy_stdout.txt
