
declare -A scenes_ref_index=( ["A"]="00900" ["B"]="10000" ["C"]="01480" ["D"]="01200" ["E"]="10000" ["F"]="40000" ["G"]="00950" ["H"]="00950" ["I"]="03100")

diff_file="entropy_diff_norm0.csv"
metric="rmse"

#python compute_diff_entropy.py --data data/entropy_data.csv --output ${diff_file}

for scene in {"A","B","C","D","E","F","G","H","I"}; do

    reference_image="references/${scene}_${scenes_ref_index[$scene]}.png"
    
    python reconstruct_image_estimated.py --data data/${diff_file} --scene ${scene} --output data/images/${scene}_estimated.png
    python reconstruct_image_human.py --scene ${scene} --output data/images/${scene}_human.png

    estimated_error=$(python compare_images.py --img1 ${reference_image} --img2 data/images/${scene}_estimated.png --metric ${metric})
    human_error=$(python compare_images.py --img1 ${reference_image} --img2 data/images/${scene}_human.png --metric ${metric})

    echo "--------------"
    echo "-- Scene ${scene} -- "
    echo "Estimated (${metric}): ${estimated_error}"
    echo "Human     (${metric}): ${human_error}"
done
