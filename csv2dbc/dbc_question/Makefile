.PHONY: all clean

all: clean example test test1 test2 test3 test4 test5 test6 test7

example:
	@echo "Test example.csv ..."
	@python solution.py -i example.csv -o example_out.dbc || { echo "example failed !"; exit 1; }
	@test -s example_out.dbc || { echo "example_out.dbc file not found ! Test Failed !"; exit 1; }
	@diff example_out.dbc example.dbc || { echo "example test : comparison Failed !"; exit 1; }
	@echo "Test example.csv to example.dbc PASS"
	
test:
	@echo "Test test.csv ..."
	@python solution.py -i test.csv -o test_out.dbc || { echo "test failed !"; exit 1; }
	@test -s test_out.dbc || { echo "test_out.dbc file not found ! Test Failed !"; exit 1; }
	@diff test_out.dbc test.dbc || { echo "test : comparison Failed !"; exit 1; }
	@echo "Test test.csv to test.dbc PASS"

	@echo "End Successfully !!"

test1:
	@echo "Test1 (mutiple enumed and normal signal) test1.csv ..."
	@python solution.py -i testcases/test1.csv -o testcases/test1_out.dbc || { echo "test1 failed !"; exit 1; }
	@test -s testcases/test1_out.dbc || { echo "testcases/test1_out.dbc file not found ! test1 Failed !"; exit 1; }
	@diff testcases/test1_out.dbc testcases/test1.dbc || { echo "test1 : comparison Failed !"; exit 1; }
	@echo "Test testcases/test1.csv to testcases/test1.dbc PASS"

test2:
	@echo "Test2 (single normal signal) test2.csv ..."
	@python solution.py -i testcases/test2.csv -o testcases/test2_out.dbc || { echo "test2 failed !"; exit 1; }
	@test -s testcases/test2_out.dbc || { echo "testcases/test2_out.dbc file not found ! test2 Failed !"; exit 1; }
	@diff testcases/test2_out.dbc testcases/test2.dbc || { echo "test2 : comparison Failed !"; exit 1; }
	@echo "Test testcases/test2.csv to testcases/test2.dbc PASS"

test3:
	@echo "Test3 (All normal signals) test3.csv ..."
	@python solution.py -i testcases/test3.csv -o testcases/test3_out.dbc || { echo "test3 failed !"; exit 1; }
	@test -s testcases/test3_out.dbc || { echo "testcases/test3_out.dbc file not found ! test3 Failed !"; exit 1; }
	@diff testcases/test3_out.dbc testcases/test3.dbc || { echo "test3 : comparison Failed !"; exit 1; }
	@echo "Test testcases/test3.csv to testcases/test3.dbc PASS"

test4:
	@echo "Test4 (enumed signal contain multiple enumed signal inside) test4.csv ..."
	@python solution.py -i testcases/test4.csv -o testcases/test4_out.dbc || { echo "test4 failed !"; exit 1; }
	@test -s testcases/test4_out.dbc || { echo "testcases/test4_out.dbc file not found ! test4 Failed !"; exit 1; }
	@diff testcases/test4_out.dbc testcases/test4.dbc || { echo "test4 : comparison Failed !"; exit 1; }
	@echo "Test testcases/test4.csv to testcases/test4.dbc PASS"

test5:
	@echo "Test5 (non-cyclic message) test5.csv ..."
	@python solution.py -i testcases/test5.csv -o testcases/test5_out.dbc || { echo "test5 failed !"; exit 1; }
	@test -s testcases/test5_out.dbc || { echo "testcases/test5_out.dbc file not found ! test5 Failed !"; exit 1; }
	@diff testcases/test5_out.dbc testcases/test5.dbc || { echo "test5 : comparison Failed !"; exit 1; }
	@echo "Test testcases/test5.csv to testcases/test5.dbc PASS"

test6:
	@echo "Test6 (non-cyclic + cyclic + enumed + normal messages) test6.csv ..."
	@python solution.py -i testcases/test6.csv -o testcases/test6_out.dbc || { echo "test6 failed !"; exit 1; }
	@test -s testcases/test6_out.dbc || { echo "testcases/test6_out.dbc file not found ! test6 Failed !"; exit 1; }
	@diff testcases/test6_out.dbc testcases/test6.dbc || { echo "test6 : comparison Failed !"; exit 1; }
	@echo "Test testcases/test6.csv to testcases/test6.dbc PASS"

test7:
	@echo "Test7 (None/none field Test) test7.csv ..."
	@python solution.py -i testcases/test7.csv -o testcases/test7_out.dbc || { echo "test7 failed !"; exit 1; }
	@test -s testcases/test7_out.dbc || { echo "testcases/test7_out.dbc file not found ! test7 Failed !"; exit 1; }
	@diff testcases/test7_out.dbc testcases/test7.dbc || { echo "test7 : comparison Failed !"; exit 1; }
	@echo "Test testcases/test7.csv to testcases/test7.dbc PASS"

	@echo "End Successfully !!"

clean :
	@echo "Started Cleaning ..."
	@rm -f example_out.dbc
	@rm -f test_out.dbc
	@rm -f testcases/test1_out.dbc
	@rm -f testcases/test2_out.dbc
	@rm -f testcases/test3_out.dbc

