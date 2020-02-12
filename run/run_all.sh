# complexity, complexity_pow, complexity_diff, complexity_norm, complexity_norm2, complexity_sobel
bash run/exec_all_complexity.sh complexity
bash run/exec_all_complexity.sh complexity_diff
bash run/exec_all_complexity.sh complexity_norm
bash run/exec_all_complexity.sh complexity_norm2
bash run/exec_all_complexity.sh complexity_sobel

# diff, gradient, minus
bash run/exec_all_interval.sh diff
bash run/exec_all_interval.sh gradient
bash run/exec_all_interval.sh minus

# diff_sobel_svd_entropy, gradient_sobel_svd_entropy 
bash run/exec_all_sobel_svd_entropy.sh diff_sobel_svd
bash run/exec_all_sobel_svd_entropy.sh gradient_sobel_svd

# diff, gradient, minus
bash run/exec_all_interval_vdp.sh diff
bash run/exec_all_interval_vdp.sh gradient
bash run/exec_all_interval_vdp.sh minus