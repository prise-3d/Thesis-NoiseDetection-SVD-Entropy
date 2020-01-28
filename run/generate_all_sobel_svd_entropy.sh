
# by default
imnorm=0

#for imnorm in {0,1}; do
    for ksize in {3,5,7,9,11,13}; do
        for start in {0,50,100,150}; do
            for end in {50,100,150,200}; do
                result=$((end - start))
                
                if [ $result -gt 0 ]; then

                    outfile="sobel_svd_entropy_data_imnorm${imnorm}_${ksize}_${start}_${end}.csv"

                    if [ ! -f data/generated/${outfile} ]; then
                        python data_processing/estimate_sobel_svd_entropy.py --output ${outfile} --ksize ${ksize} --interval "$start,$end" --imnorm ${imnorm}
                    else
                        echo "$outfile is already generated..."
                    fi
                fi
            done
        done
    done
#done