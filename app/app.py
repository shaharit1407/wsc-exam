from flask import Flask, jsonify
from kubernetes import client, config

app = Flask(__name__)

# Load kube config (works inside cluster too with incluster_config)
try:
    config.load_incluster_config()
except:
    config.load_kube_config()

core_api = client.CoreV1Api()
metrics_api = client.CustomObjectsApi()

@app.route("/service-b-info", methods=["GET"])
def service_b_info():
    # Get pods with label app=service-b
    pods = core_api.list_namespaced_pod("default", label_selector="app=service-b")
    if not pods.items:
        return jsonify({"error": "Service B not found"}), 404

    pod = pods.items[0]
    pod_name = pod.metadata.name
    node_name = pod.spec.node_name

    # Get metrics from metrics.k8s.io API
    metrics = metrics_api.get_namespaced_custom_object(
        "metrics.k8s.io", "v1beta1", "default", "pods", pod_name
    )

    container = metrics["containers"][0]
    cpu_usage = container["usage"]["cpu"]
    mem_usage = container["usage"]["memory"]

    # Convert CPU to millicores
    if cpu_usage.endswith("n"):
        cpu_mcores = int(cpu_usage[:-1]) / 1_000_000
    elif cpu_usage.endswith("m"):
        cpu_mcores = int(cpu_usage[:-1])
    else:
        cpu_mcores = int(cpu_usage)

    # Convert memory to MB
    if mem_usage.endswith("Ki"):
        mem_mb = int(mem_usage[:-2]) / 1024
    elif mem_usage.endswith("Mi"):
        mem_mb = int(mem_usage[:-2])
    elif mem_usage.endswith("Gi"):
        mem_mb = int(mem_usage[:-2]) * 1024
    else:
        mem_mb = int(mem_usage) / (1024 * 1024)

    return jsonify({
        "nodeName": node_name,
        "cpu": str(int(cpu_mcores)),
        "memory": str(int(mem_mb))
    })


if __name__ == '__main__':
    # Bind to 0.0.0.0 so it’s reachable inside the cluster
    app.run(host='0.0.0.0', port=5000)
