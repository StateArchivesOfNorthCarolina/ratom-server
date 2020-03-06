# default: lint test

delete-elasticsearch:
	kubectl get pods
	kubectl get statefulset
	kubectl delete statefulset esnode
	kubectl get pvc
	kubectl delete pvc es-data-esnode-0
	kubectl delete pvc es-data-esnode-1
	kubectl delete pvc es-data-esnode-2
	kubectl get endpoints
	kubectl delete endpoints elasticsearch
	kubectl delete endpoints elasticsearch-cluster
	kubectl get statefulset
	kubectl get pvc
	kubectl get pods

.PHONY: delete-elasticsearch
