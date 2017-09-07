
echo "Start the easy test"

echo "Cleaning..."
make clean

echo "build ..."
make
if [ $? -ne 0 ]; then
    echo "Compilation failed"
    exit 1
fi 

./query easy_input.bin
if [ $? -ne 0 ]; then
    echo "Runtime Error"
    exit 1
fi 

echo "compare File ..."
result=$(diff easy_stdout.txt easy_expected_stdout.txt)
if [ $? -eq 0 ]; then
    echo "Easy Test Passed !" 
    echo "End the easy test"
else 
    echo "Easy Test Failed !" 
    exit 1
fi 
