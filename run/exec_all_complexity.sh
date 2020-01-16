list="complexity, complexity_sqrt"

if [ -z "$1" ]
  then
    echo "No argument supplied"
    echo "Need argument from [${list}]"
    exit 1
fi

if [[ "$1" =~ ^(complexity|complexity_sqrt)$ ]]; then
    method=$1
    echo "Start computing each scene result using '${method}' approach from entropy and sobel complexity..."
    echo "-------------------------------------------------------------------------------------------"
else
    echo "$1 is not in the list"
    exit 1
fi


declare -A scenes_ref_index=( ["A"]="00900" ["B"]="10000" ["C"]="01480" ["D"]="01200" ["E"]="10000" ["F"]="40000" ["G"]="00950" ["H"]="00950" ["I"]="03100")

metric="rmse"
output_directory="results"
norm=0

if [ ! -d "$output_directory" ]; then
    # Control will enter here if $DIRECTORY doesn't exist.
    mkdir $output_directory
fi

# compute only one time human threshold image
for scene in {"A","B","C","D","E","F","G","H","I"}; do
    python utils/reconstruct_image_human.py --scene ${scene} --output data/images/${scene}_human.png
done

# for each interval
for norm in {0,1}; do
    for imnorm in {0,1}; do
        for ksize in {3,5,7,9,11,13}; do
            for start in {0,50,100,150}; do
                for end in {50,100,150,200}; do
                    result=$((end - start))
                    if [ $result -gt 0 ]; then
                        
                        python methods/compute_${method}_entropy.py --data1 data/entropy_data_imnorm${imnorm}_${start}_${end}.csv --data2 data/complexity_data_imnorm${imnorm}_${ksize}.csv --norm ${norm} --output entropy_${method}_imnorm${imnorm}_norm${norm}_k${ksize}_${start}_${end}.csv

                        # write into markdown file (human readable)
                        echo "------|-----------|-------|--------" >> results/comparisons_${method}_norm${norm}_${metric}_k${ksize}_${start}_${end}.md
                        echo "Scene | Estimated | Human | Metric " >> results/comparisons_${method}_norm${norm}_${metric}_k${ksize}_${start}_${end}.md
                        echo "------|-----------|-------|--------" >> results/comparisons_${method}_norm${norm}_${metric}_k${ksize}_${start}_${end}.md

                        for scene in {"A","B","C","D","E","F","G","H","I"}; do

                            reference_image="references/${scene}_${scenes_ref_index[$scene]}.png"
                            
                            python utils/reconstruct_image_estimated.py --data data/entropy_${method}_imnorm${imnorm}_norm${norm}_k${ksize}_${start}_${end}.csv --scene ${scene} --output data/images/${scene}_${method}_imnorm${imnorm}_norm${norm}_k${ksize}_${start}_${end}_estimated.png

                            estimated_error=$(python utils/compare_images.py --img1 ${reference_image} --img2 data/images/${scene}_${method}_imnorm${imnorm}_norm${norm}_k${ksize}_${start}_${end}_estimated.png --metric ${metric})
                            human_error=$(python utils/compare_images.py --img1 ${reference_image} --img2 data/images/${scene}_human.png --metric ${metric})

                            echo "${scene}|${estimated_error}|${human_error}|${metric}" >> results/comparisons_imnorm${imnorm}_${method}_norm${norm}_${metric}_k${ksize}_${start}_${end}.md
                            echo "${scene};${estimated_error};${human_error};${metric}" >> results/comparisons_imnorm${imnorm}_${method}_norm${norm}_${metric}_k${ksize}_${start}_${end}.csv

                            echo "---------------------------------"
                            echo "-- Scene ${scene} (${method}) -- "
                            echo "Estimated (${metric}): ${estimated_error}"
                            echo "Human     (${metric}): ${human_error}"
                        done
                    fi
                done
            done
        done
    done
done