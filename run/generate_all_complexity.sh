for imnorm in {0,1}; do
    for ksize in {3,5,7,9,11,13}; do
        python data_processing/estimate_complexity.py --output complexity_data_imnorm${imnorm}_${ksize}.csv --ksize ${ksize} --imnorm ${imnorm}
    done
done