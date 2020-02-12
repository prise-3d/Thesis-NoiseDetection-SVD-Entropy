list="complexity, complexity_diff, complexity_norm, complexity_norm2, complexity_sobel"

if [ -z "$1" ]
  then
    echo "No argument supplied"
    echo "Need argument from [${list}]"
    exit 1
fi

if [[ "$1" =~ ^(complexity|complexity_pow|complexity_diff|complexity_norm|complexity_norm2|complexity_sobel)$ ]]; then
    method=$1
    # echo "Start computing each scene result using '${method}' approach from entropy and sobel complexity..."
    # echo "-------------------------------------------------------------------------------------------"
else
    # echo "$1 is not in the list"
    exit 1
fi


declare -A scenes_ref_index=( ["A"]="00900" ["B"]="10000" ["C"]="01480" ["D"]="01200" ["E"]="10000" ["F"]="40000" ["G"]="00950" ["H"]="00950" ["I"]="03100")

metric="rmse"
output_directory="data/results"

if [ ! -d "$output_directory" ]; then
    # Control will enter here if $DIRECTORY doesn't exist.
    echo mkdir -p $output_directory
fi

# compute only one time human threshold image
for scene in {"A","B","C","D","E","F","G","H","I"}; do
    echo python utils/reconstruct_image_human.py --scene ${scene} --output data/images/humans/${scene}_human.png
done

# for each interval
for norm in {0,1}; do
    for imnorm in {0,1}; do
        for std in {0,1}; do
            for ksize in {3,5,7,9,11,13}; do
                for start in {0,50,100,150}; do
                    for end in {50,100,150,200}; do
                        result=$((end - start))
                        if [ $result -gt 0 ]; then
                            
                            echo python methods/compute_${method}_entropy.py --data1 data/generated/entropy_data_imnorm${imnorm}_${start}_${end}.csv --data2 data/generated/complexity_data_imnorm${imnorm}_${ksize}.csv --norm ${norm} --std ${std} --output entropy_${method}_imnorm${imnorm}_norm${norm}_std${std}_k${ksize}_${start}_${end}.csv

                            output_filename="${output_directory}/vdp_comparisons_imnorm${imnorm}_${method}_norm${norm}_std${std}_${metric}_k${ksize}_${start}_${end}"
                            
                            md_filename="${output_filename}.md"
                            csv_filename="${output_filename}.csv"

                            echo rm ${md_filename}
                            echo rm ${csv_filename}
                            
                            # write into markdown file (human readable)
                            echo 'echo "------|-----------|--------" >> ${md_filename}'
                            echo 'echo "Scene | Estimated | Metric " >> ${md_filename}'
                            echo 'echo "------|-----------|--------" >> ${md_filename}'

                            for scene in {"A","B","C","D","E","F","G","H","I"}; do

                                reference_image="references/${scene}_${scenes_ref_index[$scene]}.png"
                                
                                current_output_image_path=data/images/${scene}_${method}_imnorm${imnorm}_norm${norm}_std${std}_k${ksize}_${start}_${end}_estimated.png
                                echo python utils/reconstruct_image_estimated.py --data data/thresholds/entropy_${method}_imnorm${imnorm}_norm${norm}_std${std}_k${ksize}_${start}_${end}.csv --scene ${scene} --output ${current_output_image_path}
                                
                                # run vdp between ref and estimated image
                                vdp_estimated_image_without_ext=data/images/vdp_${scene}_${method}_imnorm${imnorm}_norm${norm}_std${std}_k${ksize}_${start}_${end}_estimated
                                vdp_estimated_image_path=${vdp_estimated_image_without_ext}.png
                                
                                echo matlab -nodesktop -nodisplay -nosplash -r "\"path_ref='../${reference_image}';path_noisy='../${current_output_image_path}';prefix='../${vdp_estimated_image_without_ext}';cd ${hdrvdp_folder};run;exit"\"

                                # run vdp between ref and human image
                                vdp_human_image_without_ext=data/images/vdp_${scene}_human
                                vdp_human_image_path=${vdp_human_image_without_ext}.png

                                echo matlab -nodesktop -nodisplay -nosplash -r "\"path_ref='../${reference_image}';path_noisy='../data/images/humans/${scene}_human.png';prefix='../data/images/vdp_${scene}_human.png';cd ${hdrvdp_folder};run;exit"\"

                                echo 'estimated_error=$(python utils/compare_images.py --img1 ${vdp_human_image_path} --img2 ${vdp_estimated_image_path} --metric ${metric})'

                                echo 'echo "${scene}|${estimated_error}|${metric}" >> ${md_filename}'
                                echo 'echo "${scene};${estimated_error};${metric}" >> ${csv_filename}'

                                # echo "---------------------------------"
                                # echo "-- Scene ${scene} (${method}) -- "
                                # echo "Error (estimated vs. human) (${metric}): ${estimated_error}"
                            done
                        fi
                    done
                done
            done
        done
    done
    echo rm data/images/*.png
done