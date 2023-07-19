# These can be overidden with env vars.
CLUSTER ?= devops-shopcarts
SPACE ?= dev

PLATFORM ?= "linux/amd64"
IMAGE ?= $(REGISTRY)/$(NAMESPACE)/$(IMAGE_NAME):$(IMAGE_TAG)
REGISTRY ?= us.icr.io
NAMESPACE ?= devops-shopcarts
IMAGE_NAME ?= shopcarts
IMAGE_TAG ?= 1.0

.PHONY: help
help: ## Display this help
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  make \033[36m<target>\033[0m\n"} /^[a-zA-Z_0-9-\\.]+:.*?##/ { printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) } ' $(MAKEFILE_LIST)

.PHONY: all
all: help

.PHONY: clean
clean:	## Removes all dangling docker images
	$(info Removing all dangling docker images..)
	docker image prune -f

.PHONY: venv
venv: ## Create a Python virtual environment
	$(info Creating Python 3 virtual environment...)
	python3 -m venv .venv

.PHONY: install
install: ## Install dependencies
	$(info Installing dependencies...)
	sudo python3 -m pip install --upgrade pip wheel
	sudo pip install -r requirements.txt

.PHONY: lint
lint: ## Run the linter
	$(info Running linting...)
	flake8 service tests --count --select=E9,F63,F7,F82 --show-source --statistics
	flake8 service tests --count --max-complexity=10 --max-line-length=127 --statistics
	pylint service tests --max-line-length=127

.PHONY: tests
test: ## Run the unit tests
	$(info Running tests...)
	green -vvv --processes=1 --run-coverage --termcolor --minimum-coverage=95

.PHONY: run
run: ## Run the service
	$(info Starting service...)
	honcho start

.PHONY: cluster
cluster: ## Create a K3D Kubernetes cluster with load balancer and registry
	$(info Creating Kubernetes cluster with a registry and 1 node...)
	k3d cluster create --agents 1 --registry-create cluster-registry:0.0.0.0:32000 --port '8080:80@loadbalancer'

.PHONY: cluster-rm
cluster-rm: ## Remove a K3D Kubernetes cluster
	$(info Removing Kubernetes cluster...)
	k3d cluster delete

.PHONY: login
login: ## Login to IBM Cloud using yur api key
	$(info Logging into IBM Cloud cluster $(CLUSTER)...)
	ibmcloud login -a cloud.ibm.com -g Default -r us-south --apikey @~/.ibm/apikey_shopcarts.json
	ibmcloud cr login
	ibmcloud ks cluster config --cluster $(CLUSTER)
	ibmcloud ks workers --cluster $(CLUSTER)
	kubectl cluster-info

.PHONY: push
image-push: ## Push to a Docker image registry
	$(info Logging into IBM Cloud cluster $(CLUSTER)...)
	ibmcloud cr login
	docker push $(IMAGE)

.PHONY: deploy
deploy: ## Deploy the service on local Kubernetes
	$(info Deploying service locally...)
	kubectl apply -f deploy/

.PHONY: create_cluster_namespace
create_cluster_namespace: ## Create the namespace assigned to the SPACE env variable
	$(info Creating the $(SPACE) cluster namespace...)
	kubectl create namespace $(SPACE)
	kubectl get secret all-icr-io -n default -o yaml | sed 's/default/$(SPACE)/g' | kubectl create -n $(SPACE) -f -
	kubectl config set-context --current --namespace $(SPACE)

.PHONY: set_cluster_namespace
set_cluster_namespace: ## Set default namespace to the SPACE env var
	$(info Setting default cluster namespace to $(SPACE)...)
	kubectl config set-context --current --namespace $(SPACE)

############################################################
# COMMANDS FOR BUILDING THE IMAGE
############################################################

.PHONY: init
init: export DOCKER_BUILDKIT=1
init:	## Creates the buildx instance
	$(info Initializing Builder...)
	docker buildx create --use --name=qemu
	docker buildx inspect --bootstrap

.PHONY: build
build:	## Build all of the project Docker images
	$(info Building $(IMAGE) for $(PLATFORM)...)
	docker buildx build --file Dockerfile  --pull --platform=$(PLATFORM) --tag $(IMAGE) --load .

.PHONY: remove
remove:	## Stop and remove the buildx builder
	$(info Stopping and removing the builder image...)
	docker buildx stop
	docker buildx rm
