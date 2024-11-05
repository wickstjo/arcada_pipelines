wget https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml
mv components.yaml metrics_server.yaml
kubectl apply -f metrics_server.yaml