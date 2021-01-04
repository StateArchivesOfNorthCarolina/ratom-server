# default: lint test

delete-elasticsearch:
	kubectl delete statefulset esnode
	kubectl delete configmap es-config
	kubectl delete svc elasticsearch
	kubectl delete pvc es-data-esnode-0
	kubectl delete pvc es-data-esnode-1
	kubectl delete pvc es-data-esnode-2

show-elasticsearch:
	kubectl get statefulsets
	kubectl get po
	kubectl get configmaps
	kubectl get svc

.PHONY: delete-elasticsearch
