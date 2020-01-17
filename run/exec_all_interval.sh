list="diff, gradient, gradientabs, minus"

if [ -z "$1" ]
  then
    echo "No argument supplied"
    echo "Need argument from [${list}]"
    exit 1
fi

if [[ "$1" =~ ^(diff|gradient|gradientabs|minus)$ ]]; then
    method=$1
    echo "Start computing each scene result using '${method}' approach from entropy..."
    echo "--------------------------------------------------------------------------"
else
    echo "$1 is not in the list"
    exit 1
fi


declare -A scenes_ref_index=( ["A"]="00900" ["B"]="10000" ["C"]="01480" ["D"]="01200" ["E"]="10000" ["F"]="40000" ["G"]="00950" ["H"]="00950" ["I"]="03100")

metric="rmse"
output_directory="results"

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
        for std in {0,1}; do
            for start in {0,50,100,150}; do
                for end in {50,100,150,200}; do
                    result=$((end - start))
                    if [ $result -gt 0 ]; then
                        
                        python methods/compute_${method}_entropy.py --data data/entropy_data_imnorm${imnorm}_${start}_${end}.csv --norm ${norm} --std ${std} --output entropy_${method}_imnorm${imnorm}_norm${norm}_std${std}_${start}_${end}.csv
                        std_method=$(python utils/get_std_method.py --data data/entropy_${method}_imnorm${imnorm}_norm${norm}_std${std}_${start}_${end}.csv) 
                        
                        echo "${method}_imnorm${imnorm}_norm${norm}_std${std}_${metric}_${start}_${end};${std_method};${metric}" >> results/std_analysis.csv

                        # write into markdown file (human readable)
                        echo "------|-----------|-------|--------" >> results/comparisons_${method}_imnorm${imnorm}_norm${norm}_std${std}_${metric}_${start}_${end}.md
                        echo "Scene | Estimated | Human | Metric " >> results/comparisons_${method}_imnorm${imnorm}_norm${norm}_std${std}_${metric}_${start}_${end}.md
                        echo "------|-----------|-------|--------" >> results/comparisons_${method}_imnorm${imnorm}_norm${norm}_std${std}_${metric}_${start}_${end}.md

                        for scene in {"A","B","C","D","E","F","G","H","I"}; do

                            reference_image="references/${scene}_${scenes_ref_index[$scene]}.png"
                            
                            python utils/reconstruct_image_estimated.py --data data/entropy_${method}_imnorm${imnorm}_norm${norm}_std${std}_${start}_${end}.csv --scene ${scene} --output data/images/${scene}_${method}_imnorm${imnorm}_norm${norm}_std${std}_${start}_${end}_estimated.png

                            estimated_error=$(python utils/compare_images.py --img1 ${reference_image} --img2 data/images/${scene}_${method}_imnorm${imnorm}_norm${norm}_std${std}_${start}_${end}_estimated.png --metric ${metric})
                            human_error=$(python utils/compare_images.py --img1 ${reference_image} --img2 data/images/${scene}_human.png --metric ${metric})

                            echo "${scene}|${estimated_error}|${human_error}|${metric}" >> results/comparisons_${method}_imnorm${imnorm}_norm${norm}_std${std}_${metric}_${start}_${end}.md
                            echo "${scene};${estimated_error};${human_error};${metric}" >> results/comparisons_${method}_imnorm${imnorm}_norm${norm}_std${std}_${metric}_${start}_${end}.csv

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