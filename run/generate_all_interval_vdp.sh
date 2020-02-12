if [ -z "$1" ]
  then
    echo "No argument supplied"
    echo "Need vdp folder"
    exit 1
fi

vdp_folder=$1

for imnorm in {0,1}; do
    for start in {0,50,100,150}; do
        for end in {50,100,150,200}; do
            result=$((end - start))
            if [ $result -gt 0 ]; then
                python data_processing/estimate_vdp_entropy.py --vdp_folder ${vdp_folder} --output vdp_entropy_data_imnorm${imnorm}_${start}_${end}.csv --interval "$start,$end" --imnorm ${imnorm}
            fi
        done
    done
done
