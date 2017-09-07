echo "Start the hard test"
echo "Cleaning..."
make clean

echo "build ..."
make
if [ $? -ne 0 ]; then
    echo "Compilation failed"
    exit 1
fi 

./query hard_input.bin
if [ $? -ne 0 ]; then
    echo "Runtime Error"
    exit 1
fi 

#echo "compare File ..."
#result=$(diff easy_stdout.txt easy_expected_stdout.txt)
#if [ $? -eq 0 ]; then
#    echo "Hard Test Passed !" 
#else 
#    echo "Hard Test Failed !" 
#fi

