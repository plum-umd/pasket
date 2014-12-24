LoC_k=$(find $1 -name "*sk" | xargs wc -l | awk '{total+=$1}END{print total/2}')
echo "LoC sketch : " $LoC_k
LoC_j=$(find java -type f -name "*java" | xargs wc -l | awk '{total+=$1}END{print total/2}')
echo "LoC java : " $LoC_j
N_cls=$(find java -type f -name "*java" | wc -l)
echo "# of classes : " $N_cls
