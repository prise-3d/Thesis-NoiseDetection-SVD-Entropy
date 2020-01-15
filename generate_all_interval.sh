for start in {0,50,100,150}; do
    for end in {50,100,150,200}; do
        result=$((end - start))
        if [ $result -gt 0 ]; then
            python estimate_entropy.py --output entropy_data_${start}_${end}.csv --interval "$start,$end"
        fi
    done
done
