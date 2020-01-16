for imnorm in {0,1}; do
    for start in {0,50,100,150}; do
        for end in {50,100,150,200}; do
            result=$((end - start))
            if [ $result -gt 0 ]; then
                python data_processing/estimate_entropy.py --output entropy_data_imnorm${imnorm}_${start}_${end}.csv --interval "$start,$end" --imnorm ${imnorm}
            fi
        done
    done
done
