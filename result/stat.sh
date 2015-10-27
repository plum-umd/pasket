LoC_sk=$(find $1 -type f -name "*sk" | xargs wc -l | awk '{total+=$1}END{print total/2}')
echo "LoC sketch : " $LoC_sk
LoC_jsk=$(find java_$1 -type f -name "*java" | xargs wc -l | awk '{total+=$1}END{print total/2}')
echo "LoC jsk : " $LoC_jsk
LoC_j=$(find java -type f -name "*java" | xargs wc -l | awk '{total+=$1}END{print total/2}')
echo "LoC java : " $LoC_j
N_cls=$(find java -type f -name "*java" | wc -l)
echo "# of classes : " $N_cls
