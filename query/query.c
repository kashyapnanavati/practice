/* Problem Statement :
You are given a binary file containing unsorted unsigned 32-bit integers.
The file contains up to 2^20 random, unique integers, encoded in big-endian format.
Each integer will be in the range [0, 2^25).

Write a program that, given an integer in range [0, 2^25), will return the closest integer from the input file.
If there is a tie for the closest, return the lower one.

Your program should take one command-line argument:

./query <path_to_input_file>

Your program should read test cases from standard input and write results to standard output, one per line.

Constraints
------------------------------

1. Must be written in C or C++, using only standard libraries
    * Will compile with: g++ <sourcefile> -o query
    * Will run with: ./query <inputfile>.bin
2. Only 35 KB of system RAM available, but infinite disk space (can create new files as needed)
    * Simulates a small embedded system with external hard disk
    * Will be checking static mem usage with objdump (objdump -x query | grep bss | head -1)
    * Will be checking dynamic mem usage with valgrind
    * mmap cannot be used
3. Try to minimize file I/O and dynamic memory usage
4. Optimize for fast queries

Test Case Input/Output format
------------------------------

First line of input contains an integer, N (1 <= N <= 10000), denoting the number of test cases, followed by N query integers, one per line.
For each of the N query integers, output the closest integer from the input file, one per line.

Sample Input File (hexadecimal, easy_input.bin)
------------------------------

00 00 00 80 00 00 00 61 00 00 00 60 00 00 00 2E 00 00 00 0B 00 00 00 02 00 00 00 06 00 00 00 7F

Explanation:

Binary file containing 8 random, unique, unsorted, 32-bit unsigned integers: [128, 97, 96, 46, 11, 2, 6, 127]

Sample Test Cases
-----------------
5
0
255
90
4
16


Sample Test Cases Output
-----------------
2
128
96
2
11

Explanation:

N = 5, the number of test cases
Closest to 0 is 2
Closest to 255 is 128
Closest to 90 is 96
Closest to 4 is either 2 or 6, break tie by choosing lower (2)
Closest to 16 is 11

Additional Notes
-----------------
* Your program will be tested against hard_input.bin (contains 2^20 integers). Test cases will be hidden.
* You can test your program on easy_input.bin with:
    ./query easy_input.bin <easy_stdin.txt >easy_stdout.txt
    diff easy_stdout.txt easy_expected_stdout.txt
   
 */


#include <stdio.h>
#include <stdlib.h>
#include <limits.h>
#include <time.h>
#include <dirent.h>
#include <string.h>
#include <assert.h>
#include <sys/time.h>

#ifndef INT_MAX
#error INT_MAX not defined at this point
#endif

#define SYSTEM_MEMORY_SIZE (33UL * 1024UL)

/* Only Debugging purpose */
#define DEBUG_PERFORMANCE

/* Integer round-up division of a with b */
#define CEIL_DIV(a, b)		((b) ? (((a) + (b) - 1) / (b)) : 0)

struct MinHeapNode
{
	int elem;
	int i;
};

struct MinHeapNode *heapArr;
int heap_size;

// to get index of left child of node at index i
int left(int i) { return (2 * i + 1); }
 
// to get index of right child of node at index i
int right(int i) { return (2 * i + 2); }
 
// to get the root
struct MinHeapNode getMin() {  return heapArr[0]; }
 
void MinHeapify(int i);

// to replace root with new node x and heapify()
// new root
void replaceMin(struct MinHeapNode  *x)
{
	heapArr[0].elem = x->elem;
	heapArr[0].i = x->i;
	MinHeapify(0);
}


// A utility function to swap two elements
void swap(struct MinHeapNode* x, struct MinHeapNode* y)
{
    struct MinHeapNode temp = *x;
    *x = *y;
    *y = temp;
}

void createMinHeap(struct MinHeapNode a[], int size)
{
    heap_size = size;
    heapArr = a; // store address of array
    int i = (heap_size - 1) / 2;
    while (i >= 0)
    {
        MinHeapify(i);
        i--;
    }
}

// A recursive method to heapify a subtree with root
// at given index. This method assumes that the
// subtrees are already heapified
void MinHeapify(int i)
{
    int l = left(i);
    int r = right(i);
    int smallest = i;
    if (l < heap_size && heapArr[l].elem < heapArr[i].elem)
        smallest = l;
    if (r < heap_size && heapArr[r].elem < heapArr[smallest].elem)
        smallest = r;
    if (smallest != i)
    {
        swap(&heapArr[i], &heapArr[smallest]);
        MinHeapify(smallest);
    }
}

FILE* openFile(const char* fileName, const char* mode)
{
    FILE* fp = fopen(fileName, mode);
    if (fp == NULL)
    {
        perror("Error while opening the file.\n");
        exit(EXIT_FAILURE);
    }
    return fp;
}

void swap_sort(unsigned int *a, unsigned int *b)
{
    *a=*a^*b;
    *b=*a^*b;
    *a=*a^*b;
}

void heapify(unsigned int input[], int n, int i)
{
    int largest = i;  // Initialize largest as root
    int l = 2*i + 1;  // left = 2*i + 1
    int r = 2*i + 2;  // right = 2*i + 2
 
    // If left child is larger than root
    if (l < n && input[l] > input[largest])
        largest = l;
 
    // If right child is larger than largest so far
    if (r < n && input[r] > input[largest])
        largest = r;
 
    // If largest is not root
    if (largest != i)
    {
        swap_sort(&input[i], &input[largest]);
 
        // Recursively heapify the affected sub-tree
        heapify(input, n, largest);
    }
}

void do_sorting(unsigned int input[], int n)
{
    // Build heap (rearrange array)
    for (int i = n / 2 - 1; i >= 0; i--)
        heapify(input, n, i);
 
    // One by one extract an element from heap
    for (int i=n-1; i>0; i--)
    {
        // Move current root to end
        swap_sort(&input[0], &input[i]);
 
        // call max heapify on the reduced heap
        heapify(input, i, 0);
    }
}


/* Note : 
   Folowing merge file logic/pusedo code is copied from following link
   http://www.geeksforgeeks.org/external-sorting/
   It is modified as per this problem requirement
   Merges k sorted files.  Names of files are assumed to be 1, 2, 3, ... k
*/
void mergeFiles(const char *output_file, int n, int k)
{
    FILE* in[k];
    for (int i = 0; i < k; i++)
    {
        char fileName[16];
 
        // convert i to string
        snprintf(fileName, sizeof(fileName), "unsorted/%d", i);
 
        // Open output files in read mode.
        in[i] = openFile(fileName, "r");
    }
 
    // FINAL OUTPUT FILE
    FILE *out = openFile(output_file, "w");
 
    // Create a min heap with k heap nodes.  Every heap node
    // has first element of scratch output file
    /* Optimization BUG : as we are not freeing arr, this allocation may go beyond 35 KB size
       TODO : Handle this properly
     */
    struct MinHeapNode* heapArr = (struct MinHeapNode *) malloc (sizeof(struct MinHeapNode) * k);
    int i;
    for (i = 0; i < k; i++)
    {
        // break if no output file is empty and
        // index i will be no. of input files
        if (fread(&heapArr[i].elem, sizeof(unsigned int), 1, in[i]) != 1)
            break;
	//printf("merge File data =%x\n", heapArr[i].elem); 
        heapArr[i].i = i; // Index of scratch output file
    }

    createMinHeap(heapArr, i);
 
    int count = 0;
 
    // Now one by one get the minimum elem from min
    // heap and replace it with next elem.
    // run till all filled input files reach EOF
    while (count != i)
    {
        // Get the minimum element and store it in output file
        MinHeapNode root = getMin();
	fwrite(&root.elem, sizeof(unsigned int), 1, out);
 
        // Find the next element that will replace current
        // root of heap. The next element belongs to same
        // input file as the current min element.
        if (fread(&root.elem, sizeof(unsigned int), 1, in[root.i]) != 1)
        {
            root.elem = INT_MAX;
            count++;
        }
        // Replace root with next elem of input file
        replaceMin(&root);
    }

    if (heapArr)
    	free(heapArr);
 
    // close input and output files
    for (int i = 0; i < k; i++)
        fclose(in[i]);
 
    fclose(out);
}

void createInitialRuns(char *input_file, int run_size,
                       int num_ways,
                       unsigned int *arr)
{
    // For big input file
    FILE *in = openFile(input_file, "r");
    // output scratch files
    FILE* out[num_ways];
    char fileName[16];
	if (arr == NULL) {
		printf("ERROR createInitialRuns : Invalid input buffer\n");    
		exit(EXIT_FAILURE);
	}
    for (int i = 0; i < num_ways; i++)
    {
        // convert i to string
        snprintf(fileName, sizeof(fileName), "unsorted/%d", i);
 
        // Open output files in write mode.
        out[i] = openFile(fileName, "w");
    }
 
    // allocate a dynamic array large enough
    // to accommodate runs of size run_size
    bool more_input = true;
    int next_output_file = 0;
    unsigned char temp_buffer[4];
 
    int i;
    while (more_input)
    {
        // write run_size elements into arr from input file
        /* TODO : Optimize this code and remove multiple IO operation */
        for (i = 0; i < run_size; i++)
        {
            //if (fscanf(in, "%d ", &arr[i]) != 1)
	    if (fread(&temp_buffer, sizeof(unsigned int), 1, in) != 1)
            {
                more_input = false;
                break;
            }
            arr[i] = temp_buffer[3] | (temp_buffer[2] << 8) | (temp_buffer[1]<<16) | (temp_buffer[0]<<24);
        }
#if 0
        printf("\nDebug before Sorting\n");
        for (int j = 0; j < run_size; j++) {
            printf("%d\t", arr[j]);
        }
#endif
        do_sorting(arr, i); //Do not change i to run_size
#if 0
        printf("\nDebug after Sorting\n");
        for (int j = 0; j < run_size; j++) {
            printf("%d\t", arr[j]);
        }
#endif
 
        // write the records to the appropriate scratch output file
        // can't assume that the loop runs to run_size
        // since the last run's length may be less than run_size
	fwrite(arr, sizeof(unsigned int), i, out[next_output_file]);
 
        next_output_file++;
    }

    // close input and output files
    for (int i = 0; i < num_ways; i++)
        fclose(out[i]);
 
    fclose(in);
}


void externalFileSort(char* input_file,  const char *output_file,
                  int num_ways, int run_size, unsigned int *arr)
{
    // read the input file, create the initial runs,
    // and assign the runs to the scratch output files
      createInitialRuns(input_file, run_size, num_ways, arr);

    // Merge the runs using the K-way merging
     mergeFiles(output_file, run_size, num_ways);
}

int devideSortedFiles(const char *output_file, int num_ways, unsigned int run_size, unsigned int *arr)
{
	
	FILE* out_s;
	char fileName[100];
	FILE* out_f;
	size_t file_size;
	unsigned int extra_bytes;
	unsigned int first, last;
	unsigned int debug_counter= 0;

    	if (arr == NULL) {
		printf("ERROR devideSortedFiles : Invalid input buffer\n");    
		exit(EXIT_FAILURE);
    	}
	out_f = openFile(output_file, "rb");
	fseek(out_f, 0, SEEK_END);
	file_size = ftell(out_f);
	fseek(out_f, 0, SEEK_SET); // Set to begining
	extra_bytes = ((num_ways * run_size * sizeof(unsigned int))- file_size) / sizeof (unsigned int);
	//printf("Debug devideSortedFiles : extra bytes = %d * 4 = %d\n", extra_bytes, extra_bytes * 4);

	for (int i = 0; i < num_ways; i++) {
		if (fread(arr, sizeof(unsigned int), run_size, out_f) != run_size) {
			printf("WARNING devideSortedFiles: buffer is larger then remaining bytes\n");    
		}
		if (i == num_ways-1) {
			first = arr[0];
			last = arr[run_size - extra_bytes - 1];
		} else {
			first = arr[0];
			last = arr[run_size-1];
		}
       		snprintf(fileName, sizeof(fileName), "out_sorted/%x_%x", first, last);
		out_s = openFile(fileName, "wb");
		if (fwrite(arr, sizeof(unsigned int), run_size, out_s) != run_size) {
			printf("WARNING devideSortedFiles: cannot write output files\n");    
		}
        	fclose(out_s);
        	debug_counter+=(run_size * sizeof(unsigned int));
	}

	//printf("INFO devideSortedFiles : debug_count = %d (total bytes processed)", debug_counter);
        fclose(out_f);

	return 0;
}


unsigned int findClosest(unsigned int *input, int start, int length, unsigned int target)
{
	int end = length -1;  
	int s = start;
    	if (end < 0) {
		printf("Error : Invalid range");
        	exit(EXIT_FAILURE);
	}
	while (start <= end) {
		int mid = start + (end-start) / 2;
		if (mid < s || mid-1 < s || mid > length - 1) {
			break;	    
		}
		unsigned int a = abs(input[mid] - target);
		unsigned int b = abs(input[mid-1] - target);
		if (b <= a)
		    end = mid - 1;
		else
		    start = mid + 1;
	}
	if (end < 0) {
	    end = 0;
	} else if (end > length -1) {
	    end = length -1;
	}
	return input[end];
}

int performGlobalBinarySearch(unsigned int data_tobe_searched,
				int num_ways,
				int run_size,
				unsigned int *final_output,
				unsigned int *arr)
{
	DIR *dir;
	struct dirent *directory;
	unsigned int first = 0, last = 0, count = 0;
	/* readdir cannot perform file search in sorted order, In that case,
	   we need to handle seperately
	 */
	bool out_of_bound = false;
	/* Assume given input file is not more 5 MB on 35 KB RAM system
	  In that case, max number of files will be generate = ~150 (considering 30 KB RAM)
	  To total bounded value (first and last) will be 300 = 300 * 4 = ~1.2KB
	 */
	unsigned int* f_l_arr = (unsigned int*)malloc(300 * sizeof(unsigned int));

	dir = opendir("out_sorted/");
	if (!dir) {
		printf("ERROR performGlobalBinarySearch : Cannot open directory\n");    
		return -1;
	}
	
	while((directory = readdir(dir)) != NULL) {
		/* Skip the . and .. files */	    
		if (!strncmp(directory->d_name, ".", 1) || !strncmp(directory->d_name, "..", 2)) {
			continue;
		}
		//printf("%s\n", directory->d_name);
		sscanf(directory->d_name, "%x_%x", &first, &last);
		//printf("First = %x and last = %x\n", first, last);
		f_l_arr[count++] = first;
		f_l_arr[count++] = last;
		assert(count < 300);
		if (data_tobe_searched >= first && data_tobe_searched <= last) {
		    	FILE *in_bin_fle;
		    	char l_filename[270] = "out_sorted/";
		    	strncat(l_filename, directory->d_name, 256);
		    	//printf("Debug : String is %s\n", l_filename);
			in_bin_fle = openFile(l_filename, "rb");
		    	if (arr == NULL) {
				printf("ERROR : performGlobalBinarySearch Malloc Failed\n");    
				return -1;
		    	}
			if (fread(arr, sizeof(unsigned int), run_size, in_bin_fle) != run_size) {
				printf("WARNING performGlobalBinarySearch : buffer is larger then remaining bytes\n");
			}
			/* Perform Loalized Binary sarch */
			*final_output = findClosest(arr, 0, run_size, data_tobe_searched);
			fclose(in_bin_fle);
			out_of_bound = false;
			break;
		} else {
		    	/* Corner cases */
		    	out_of_bound = true;
		}
	}

	if (out_of_bound) {
		do_sorting(f_l_arr, count);
		if (data_tobe_searched < f_l_arr[0]) {
			*final_output = f_l_arr[0];
			goto END;
		} else if (data_tobe_searched >= f_l_arr[count-1]) {
		    	*final_output = f_l_arr[count-1];
		    	goto END;
		} else {
		    	*final_output = findClosest(f_l_arr, 0, count, data_tobe_searched);
		}
	}

END :
	if (f_l_arr) {
	    free(f_l_arr);
	    closedir(dir);
	}
	return 0;   
}

int main(int argc, char *argv[])
{
	/* No. of Partitions of input file, when file is larger then SYSTEM RAM */
	int num_ways = 0;
	/* The size of each partition will be set to SYTEM RAM */
	int run_size = 0;
	const char output_sorted_bin_file[] = "sorted_output.bin";
	char input_bin_filename[50] = "easy_input.bin";
	char input_filename[60] = "easy_stdin.txt";
	char output_filename[60] = "easy_stdout.txt";
	FILE *file_in, *file_out;
    	size_t file_size;
	FILE* file_in_bin;
	unsigned int *arr = NULL;

	if (argc < 2) {
		printf("ERROR : Atleast 1 argument must be provided in program !\n");
		printf("Usage : \n");
		printf("---------------------------\n");
		printf("1. ./query <path_to_input_file>\n");
		printf("2. ./query <path_to_input_file> <input_txt_file> <output_txt_file>\n");
		printf("---------------------------\n");
        	exit(EXIT_FAILURE);
	}
	if (argc == 2) {
		strncpy(input_bin_filename, argv[1], 60);
	} else if (argc == 4) {
		strncpy(input_bin_filename, argv[1], 60);
		strncpy(input_filename, argv[2], 60);
		strncpy(output_filename, argv[3], 60);
	}
	printf("Input Binary File = %s\n", input_bin_filename);
	printf("Input txt filename = %s\n", input_filename);
	printf("Output txt filename = %s\n", output_filename);

	file_in_bin = openFile(input_bin_filename, "rb");
	fseek(file_in_bin, 0, SEEK_END);
	file_size = ftell(file_in_bin);
	fseek(file_in_bin, 0, SEEK_SET); /* Set to begining */

	/* No. of Partitions of input file incase it exceeds total RAM size */
	if (file_size > SYSTEM_MEMORY_SIZE) {
    		num_ways = CEIL_DIV(file_size, SYSTEM_MEMORY_SIZE);
	    	run_size = SYSTEM_MEMORY_SIZE/sizeof(unsigned int);
	} else {
	    	num_ways = 1;
    		run_size = file_size/sizeof(unsigned int);
    	}

	printf("file_size = %ld\n", file_size);
	printf("num_ways = %d\n", num_ways);
	printf("run_size = %d\n", run_size * 4);

	fclose(file_in_bin);
 
#ifdef DEBUG_PERFORMANCE
	struct timeval begin, end;
	gettimeofday(&begin, NULL);
#endif
	/* Allocate memory for precessing of data within RAM size */
	arr = (unsigned int*)malloc(run_size * sizeof(unsigned int));
	
	/* TODO : Optimize this function properly */
	externalFileSort(input_bin_filename, output_sorted_bin_file, num_ways,
		run_size, arr);

	devideSortedFiles(output_sorted_bin_file, num_ways, run_size, arr);

    	file_in = openFile(input_filename, "r");
	file_out = openFile(output_filename, "w");
	{
	    	int i = 0, count = 0, ans = 0;
		unsigned int final_output = 0;
		unsigned int data_tobe_searched = 0;
		unsigned int number_of_inputs = 0; /* Hold total number of inputs read from txt file */
		fscanf(file_in, "%d", &number_of_inputs);
		//printf("Total number of inputs to scan = %d\n", number_of_inputs);
		count = number_of_inputs;
		while (count != 0) {
			fscanf(file_in, "%d", &data_tobe_searched);
    			ans = performGlobalBinarySearch(data_tobe_searched, num_ways, run_size, &final_output, arr);
			if (ans == -1) {
				printf("ERROR : Perform Query Failed\n");
				return -1;
			}
			fprintf(file_out, "%d\n", final_output);
			i++;
			count--;
		}
		fclose(file_in);
		fclose(file_out);
	} 
	printf("\n");

	if (arr)
		free(arr);
#ifdef DEBUG_PERFORMANCE
	gettimeofday(&end, NULL);
	double u_seconds = end.tv_usec - begin.tv_usec;
	double seconds = end.tv_sec - begin.tv_sec;
	double mt = (seconds) + (u_seconds/1000000.0);
	printf ("\nTotal time take is = %lf seconds\n", mt);
#endif
    	return 0;
}
