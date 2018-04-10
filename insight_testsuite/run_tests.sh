#!/bin/sh
echo "Test 1"
python ../src/processdata.py --input=log.csv --timeout=inactivity_period.txt --output=sessionization.txt --input_path=tests/test1/input/ --output_path=tests/test1/output/

file1="tests/test1/output/sessionization.txt"
file2="tests/test1/output/sessionization_gt.txt"
echo $file1
echo $file2
if cmp -s "$file1" "$file2"
then
   echo "The files match"
else
   echo "The files are different"
fi

echo "Test 2.1"
python ../src/processdata.py --input=log1.csv --timeout=inactivity_period.txt --output=sessionization.txt --input_path=tests/test2/input/ --output_path=tests/test2/output/

echo "File throws header exception"

echo "Test 2.2"
python ../src/processdata.py --input=log2.csv --timeout=inactivity_period.txt --output=sessionization.txt --input_path=tests/test2/input/ --output_path=tests/test2/output/

echo "File throws data field in sufficient indexing"
