# DASHBOARD PORT        8265
# CONNECTION PORT       10001

clear
while true; do
    kubectl port-forward -n ray svc/raycluster-kuberay-head-svc --address 193.167.37.127 $1:$1
    sleep 2;
done