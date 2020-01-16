for ksize in {3,5,7,9,11,13}; do
    python data_processing/estimate_complexity.py --output complexity_data_${ksize}.csv --ksize ${ksize}
done
