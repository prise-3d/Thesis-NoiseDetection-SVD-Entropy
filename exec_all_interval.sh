


declare -A scenes_ref_index=( ["A"]="00900" ["B"]="10000" ["C"]="01480" ["D"]="01200" ["E"]="10000" ["F"]="40000" ["G"]="00950" ["H"]="00950" ["I"]="03100")

diff_file="entropy_diff_norm0.csv"
metric="rmse"
output_directory="results"

if [ ! -d "$output_directory" ]; then
    # Control will enter here if $DIRECTORY doesn't exist.
    mkdir $output_directory
fi

# compute only one time human threshold image
for scene in {"A","B","C","D","E","F","G","H","I"}; do
    python reconstruct_image_human.py --scene ${scene} --output data/images/${scene}_human.png
done

# for each interval
for start in {0,50,100,150}; do
    for end in {50,100,150,200}; do
        result=$((end - start))
        if [ $result -gt 0 ]; then
            
            python compute_diff_entropy.py --data data/entropy_data_${start}_${end}.csv --output entropy_diff_norm0_${start}_${end}.csv

            # write into markdown file (human readable)
            echo "------|-----------|-------|--------" >> results/comparisons_${metric}_${start}_${end}.md
            echo "Scene | Estimated | Human | Metric " >> results/comparisons_${metric}_${start}_${end}.md
            echo "------|-----------|-------|--------" >> results/comparisons_${metric}_${start}_${end}.md

            for scene in {"A","B","C","D","E","F","G","H","I"}; do

                reference_image="references/${scene}_${scenes_ref_index[$scene]}.png"
                
                python reconstruct_image_estimated.py --data data/${diff_file} --scene ${scene} --output data/images/${scene}_${start}_${end}_estimated.png

                estimated_error=$(python compare_images.py --img1 ${reference_image} --img2 data/images/${scene}_${start}_${end}_estimated.png --metric ${metric})
                human_error=$(python compare_images.py --img1 ${reference_image} --img2 data/images/${scene}_human.png --metric ${metric})

                echo "${scene}|${estimated_error}|${human_error}|${metric}" >> results/comparisons_${metric}_${start}_${end}.md
                echo "${scene};${estimated_error};${human_error};${metric}" >> results/comparisons_${metric}_${start}_${end}.csv

                echo "--------------"
                echo "-- Scene ${scene} -- "
                echo "Estimated (${metric}): ${estimated_error}"
                echo "Human     (${metric}): ${human_error}"
            done
        fi
    done
done

