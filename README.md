# wsc-exam

## Overview
This project runs two services in Kubernetes:

- **Service B** – a resource consumer pod (uses CPU and memory).
- **Service A** – a Flask web service with an endpoint `/service-b-info` that returns:
  - Node name where Service B runs
  - Current CPU usage (mCores)
  - Current memory usage (MB)

Example response:
```json
{
  "nodeName": "minikube-m01",
  "cpu": "300",
  "memory": "50"
}
Prerequisites
A running Kubernetes cluster (e.g. Minikube)

Metrics Server installed

Helm 

***Deploy***
Using Helm

helm install wsc-exam charts/wsc-exam --namespace my-namespace --create-namespace

Using kubectl

kubectl apply -f service-b/

***Usage***
Get Service A’s endpoint (NodePort, LoadBalancer, or port-forward) and call:

curl http://<SERVICE_A_ENDPOINT>/service-b-info