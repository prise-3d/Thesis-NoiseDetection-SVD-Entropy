


for start in {0,50,100,150}; do
    for end in {50,100,150,200}; do
        result=$((end - start))
        if [ $result -gt 0 ]; then
            echo python estimate_entropy.py --output entropy_data_${start}_${end}.csv
        fi
    done
done
