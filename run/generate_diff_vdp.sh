# compute diff vdp images (current image vs most noisy image)
# here need to get all outputs of this script and copy/paste into run oar script

# load matlab module into oar server
echo source /nfs/opt/env/env.sh
echo module load matlab

if [ -z "$1" ]
  then
    echo "No argument supplied"
    echo "Need dataset scenes"
    exit 1
fi

if [ -z "$2" ]
  then
    echo "No argument supplied"
    echo "Need output vdp of scenes"
    exit 1
fi

hdrvdp_folder="hdrvdp"
dataset=$1
output=$2

for folder in $(ls -d -- ${dataset}/*)
do
    # default variable value
    counter=0
    noisy_path=""
    folder=${folder//\/\//\/}

    IFS='/' read -ra ADDR <<< "${folder}"
    folder_name=${ADDR[-1]}

    # construct output folder
    output_folder=$output/$folder_name
    mkdir -p ${output_folder}

    for file in $(ls -f -- $folder/* | grep .png)
    do 
        # get number of path for current generated image
        IFS='/' read -ra ADDR <<< "${file}"
        image_name=${ADDR[-1]}

        IFS='_' read -ra ADDR <<< "${image_name}"
        postfix=${ADDR[-1]}

        IFS='.' read -ra ADDR <<< "${postfix}"
        nb_paths=${ADDR[0]}

        file_path=$file
        file_path=${file_path//\/\//\/}

        # get first image as the most noisy
        if [ $counter -le 0 ]; then
            noisy_path=$file
            noisy_path=${noisy_path//\/\//\/}
            counter=$((${counter} + 1))
        else

            if [[ "${file_path}" = /* ]]; then
                # compute vdp diff between `most noisy` and `current image`
                # need to take that we will be into `hdrvdp` folder
                echo matlab -nodesktop -nodisplay -nosplash -r "\"path_ref='${file_path}';path_noisy='${noisy_path}';prefix='${output_folder}/vdp_diff_${folder_name}_${nb_paths}';cd ${hdrvdp_folder};run;exit"\"
            else 
                # compute vdp diff between `most noisy` and `current image`
                # need to take that we will be into `hdrvdp` folder
                echo matlab -nodesktop -nodisplay -nosplash -r "\"path_ref='../${file_path}';path_noisy='../${noisy_path}';prefix='../${output_folder}/vdp_diff_${folder_name}_${nb_paths}';cd ${hdrvdp_folder};run;exit"\"
            fi
        fi
    done
done


