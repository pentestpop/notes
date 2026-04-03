---
layout: default
title: "Kubernetes"
parent: "DevSecOps"
grand_parent: "Defensive Security"
nav_order: 6
---

### K8S Terms

**Pod** - Pods are the smallest deployable unit of computing you can create and manage in Kubernetes.
- group of one or more containers
- these containers share storage and network resources, so they can communicate easily despite having some separation
- unit of replication, so scale up by adding them

**Nodes** - pods run on nodes. 
- **Control plane/master node** components:
	- The API server (**kube-apiserver**) is the front end of the control plane and is responsible for exposing the Kubernetes API.
	- **Etcd** - a key/value store containing cluster data / the current state of the cluster
		- highly available
		- other components query it for information such as number of pods
	- **Kube-scheduler** - actively monitors the cluster to make sure any newly created pods that have yet to be assigned to a node and make sure it gets assigned to one
	- **Kube-controller-manager** - responsible for running the controller processes
	- **Cloud-controller-manager** - enables communication between a Kubernetes cluster and a cloud provider API
- **Worker node** components: 
	- **Kubelet** - agent that runs on every node in the cluster and is responsible for ensuring containers are running in a pod
	- **Kube-proxy** - responsible for network communication within the cluster with networking rules
	- **Container runtime** - must be installed for pods to have containers running inside them, examples:
		- Docker
		- rkt
		- runC

![Cluster diagram](https://tryhackme-images.s3.amazonaws.com/user-uploads/6228f0d4ca8e57005149c3e3/room-content/1eba5a686238be009bc802dd419a09c8.svg)


### Other Terms
**Namespace** - namespaces are used to isolate groups of resources in a single cluster. Resources must be uniquely named within a namespace.

**ReplicaSet** - a ReplicaSet in Kubernetes maintains a set of replica pods and can guarantee the availability of x number of identical pods. They are managed by deployment rather than defined directly. 

**Deployment** - They define a desired state and then the deployment controller (one of the controller processes) changes the actual state. For example you can define a deployment as "test-nginx-deployment". In the definition, you can note that you want this deployment to have a ReplicaSet comprising three nginx pods. Once this deployment is defined, the ReplicaSet will create the pods in the background.

**StatefulSets** - Statefulsets enable stateful applications to run on Kubernetes, but unlike pods in a deployment, they cannot be created in any order and will have a unique ID (which is persistent, meaning if a pod fails, it will be brought back up and keep this ID) associated with each pod.StatefulSets will *have one pod that can read/write to the database* (because there would be absolute carnage and all sorts of data inconsistency if the other pods could), referred to as the master pod. The other pods, referred to as slave pods, can only read and have their own replication of the storage, which is continuously synchronized to ensure any changes made by the master node are reflected.

**Services** - A service is placed in front of pods and exposes them, acting as an access point. Having this single access point allows for requests to be load-balanced between the pod replicas (one IP address). There are different types of services you can define: ClusterIP, LoadBalancer, NodePort and ExternalName.

**Ingress** - Directs traffic to services which direct traffic to pods


### Configuration

![Interfacing with deployment diagram](https://tryhackme-images.s3.amazonaws.com/user-uploads/6228f0d4ca8e57005149c3e3/room-content/a0872c63c555b82e63ce1ea3dbed6c42.svg)

^ For these we need a config file for the 1. service and 2. deployment

Required fields: 
1. apiVersion
2. kind (what kind of object such as Deployment, Service StatefulSet)
3. metadata - such as name and namespace
4. spec - the desired state of the object such as 3 nginx pods for a deployment

Example service config file:
```yaml
apiVersion: v1
kind: Service
metadata:
  name: example-nginx-service
spec:
  selector:
    app: nginx
  ports:
    - protocol: TCP
      port: 8080
      targetPort: 80
  type: ClusterIP
```

- An important distinction to make here is between the 'port' and 'targetPort' fields. The 'targetPort' is the port to which the service will send requests, i.e., the port the pods will be listening on. The 'port' is the port the service is exposed on.

Example deployment config file: 
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: example-nginx-deployment
spec:
  replicas: 3
  selector:
    matchLabels:
      app: nginx
  template:
    metadata:
      labels:
        app: nginx
    spec:
      containers:
      - name: nginx
        image: nginx:latest
        ports:
        - containerPort: 80
```
- The template field is the template that Kubernetes will use to create the pods and so requires its own metadata field (so the pod can be identified) and spec field (so Kubernetes knows what image to run and which port to listen on)
- The containerPort should match the targetPort from the service config file above as that is the port that will be listening. 

### Kubectl
To interact with the config files, we can use two methods: UI if using the Kubernetes dashboard, API if using some sort of script or command line using a tool called `kubectl`.

Apply - to turn into running process
- `kubectl apply -f example-deployment.yaml`

Get - check status of the configurations
- `kubectl get pods -n example-namespace`

Describe - show the details of a resource or a group of resources
- `kubectl describe pod example-pod -n example-namsepace`

Kubectl logs - view application logs of erroring pods
- `kubectl logs example-pod -n example-namespace`

Kubectl exec - get inside a container and access shell
- `kubectl exec -it example-pod -n example-namespace -- sh`
	- the `-it` flag runs in interactive mode, and the `--` denotes what will be run inside the container, in this case `sh`.

Kubectl port-forward - allows you to create a secure tunnel between your local machine and a running pod in your cluster
- `kubectl port-forward service/example-service 8090:8080`
- Forwards port 8080 on the pod to port 8090 on our machine

### K8S and DevSecOps

1. Secure pods:
	-  Containers that run applications should not have root privileges
	- Containers should have an immutable filesystem, meaning they cannot be altered or added to (depending on the purpose of the container, this may not be possible) 
	- Container images should be frequently scanned for vulnerabilities or misconfigurations 
	- Privileged containers should be prevented  
	- [Pod Security Standards](https://kubernetes.io/docs/concepts/security/pod-security-standards/) and [Pod Security Admission](https://kubernetes.io/docs/concepts/security/pod-security-admission/)

2. Harden and Separate Network:
	- Access to the control plane node should be restricted using a firewall and role-based access control in an isolated network
	- Control plane components should communicate using Transport Layer Security (TLS) certificates
	- An explicit deny policy should be created
	- Credentials and sensitive information should not be stored as plain text in configuration files. Instead, they should be encrypted and in Kubernetes secrets
3. Use Optimal Authentication and Authorization
	- Anonymous access should be disabled 
	- Strong user authentication should be used 
	- RBAC policies should be created for the various teams using the cluster and the service accounts utilized
4. Keep an Eye Out
	- Audit logging should be enabled
	- A log monitoring and altering system should be implemented
	- Security patches and updated should be applied quickly
	- Vuln scan and pentests should be done regularly
	- Remove obsolete components in the cluster


**PSA (Pod Security Admission) and PSS (Pod Security Standards)**
Pod Security Standards are used to define security policies at 3 levels (privileged, baseline and restricted) at a namespace or cluster-wide level. What these levels mean: 
- Privileged: This is a near unrestricted policy (allows for known privilege escalations)
- Baseline: This is a minimally restricted policy and will prevent known privilege escalations (allows deployment of pods with default configuration)
- Restricted: This heavily restricted policy follows the current pod hardening best practices
- Used to both be defined as Pod Security Policies (PSPs)
- **Pod Security Admission** (using a Pod Security Admission controller) *enforces these Pod Security Standards by intercepting API server requests and applying these policies.*



