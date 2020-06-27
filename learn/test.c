#include <stdio.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>
/*
Given a string, your task is to count how many palindromic substrings in this string.
The substrings with different start indexes or end indexes are counted as different substrings even they consist of same characters.
Example 1:
Input: "abc"
Output: 3
Explanation: Three palindromic strings: "a", "b", "c".
Example 2:
Input: "aaa"
Output: 6
Explanation: Six palindromic strings: "a", "a", "a", "aa", "aa", "aaa".
*/
int countPallindromicSubstrings(char *cs) {
        int n = strlen(cs);
        //char[] cs = s.toCharArray();
        bool dp[n][n];
        int ans = 0;
        for (int i = 0; i < n; ++i){
            for (int j = i; j >= 0; --j){
                if (i == j || (dp[i - 1][j + 1] && cs[i] == cs[j]) || (cs[i] == cs[j] && i - j == 1)){
                    dp[i][j] = true;
                    ans ++;
                }   
            }
        }
        return ans;
}

void test_count_pallindromic_substring()
{
    char in[] = "abc";
    if(countPallindromicSubstrings(in) != 3) {
    	exit(1);
    	printf("Test FAIL\n");
    }
    if(countPallindromicSubstrings("aaa") != 6) {
    	exit(1);
    	printf("Test FAIL\n");
    }
    printf("Test PASS\n");
}

void swap(int *a, int *b)
{
    int tmp = *a;
    *a = *b;
    *b = tmp;
}

int Qpartition(int *arr, int start, int end)
{
    	int pivot = arr[end];
    	int plen = start;
    	for(int j = start; j <= end-1; j++) {
    	    if (pivot >= arr[j]) {
    	    	swap(&arr[plen], &arr[j]);
    	    	plen++;
    	    }
    	}
    	swap(&arr[end], &arr[plen]);
    	return plen;
}

void quickSort(int *arr, int start, int end)
{
    	int pp;
	if (start < end) {
	    pp = Qpartition(arr, start, end);
	    quickSort(arr, start, pp-1);
	    quickSort(arr, pp+1, end);
	}
}

void test_sort()
{
    	int arr[] = {0,-1, 4, 123, 100};
	printf("Before Sorting\n");
	for(int i =0; i < 5; i++) {
		printf("%d ", arr[i]);
	}
	printf("\n");
	quickSort(arr, 0, 4);
	printf("After Sorting\n");
	for(int i =0; i < 5; i++) {
		printf("%d ", arr[i]);
	}
	printf("\n");

}



int main()
{
    	//test_sort();
    	test_count_pallindromic_substring();
	return 0;
}
