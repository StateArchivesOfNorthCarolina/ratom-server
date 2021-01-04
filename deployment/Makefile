# default: lint test

delete-elasticsearch:
	kubectl delete statefulset esnode
	kubectl delete configmap es-config
	kubectl delete svc elasticsearch-loadbalancer
	kubectl delete svc elasticsearch

show-elasticsearch:
	kubectl get statefulsets
	kubectl get po
	kubectl get configmaps
	kubectl get svc

.PHONY: delete-elasticsearch
