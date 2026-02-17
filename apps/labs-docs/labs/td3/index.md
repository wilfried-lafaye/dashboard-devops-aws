---
title: "TD3 - Kubernetes & Orchestration"
publish: true
---

# TD3 - Kubernetes & Orchestration

## Objectif

Déployer une application containerisée sur un cluster Kubernetes avec load balancing et rolling updates.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Kubernetes Cluster                        │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │                   Service (LoadBalancer)                 │ │
│  │                         :8080                            │ │
│  └─────────────────────────────────────────────────────────┘ │
│                           │                                  │
│        ┌──────────────────┼──────────────────┐               │
│        ▼                  ▼                  ▼               │
│  ┌──────────┐      ┌──────────┐      ┌──────────┐           │
│  │  Pod 1   │      │  Pod 2   │      │  Pod 3   │           │
│  │sample-app│      │sample-app│      │sample-app│           │
│  └──────────┘      └──────────┘      └──────────┘           │
└─────────────────────────────────────────────────────────────┘
```

---

## Deployment Kubernetes

Configuration du Deployment avec 3 réplicas et rolling update :

```yaml
apiVersion: apps/v1
kind: Deployment                  
metadata:                         
  name: sample-app-deployment
spec:

  replicas: 3                     
  template:                       
    metadata:                     
      labels:
        app: sample-app-pods
    spec:
      containers:                 
        - name: sample-app        
          image: sample-app:v1    
          ports:
            - containerPort: 8080 
          env:                    
            - name: NODE_ENV
              value: production
  selector:                       
    matchLabels:
      app: sample-app-pods
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 3
      maxUnavailable: 0
```

> [!TIP]
> `maxSurge: 3` et `maxUnavailable: 0` garantissent un déploiement sans interruption de service.

---

## Service Kubernetes

Exposition du Deployment via un LoadBalancer :

```yaml
apiVersion: v1
kind: Service
metadata:
  name: sample-app-service
spec:
  type: LoadBalancer
  selector:
    app: sample-app-pods
  ports:
    - protocol: TCP
      port: 8080
      targetPort: 8080
```

---

## Provisionnement avec Ansible

Playbook pour déployer Nginx comme load balancer :

```yaml
- name: Configure Nginx as Load Balancer
  hosts: nginx
  become: yes
  vars_files:
    - nginx-vars.yml
  tasks:
    - name: Install Nginx
      ansible.builtin.package:
        name: nginx
        state: present

    - name: Configure Nginx upstream
      ansible.builtin.template:
        src: nginx.conf.j2
        dest: /etc/nginx/nginx.conf
      notify: Restart Nginx

  handlers:
    - name: Restart Nginx
      ansible.builtin.service:
        name: nginx
        state: restarted
```

---

## Commandes utiles

```bash
# Appliquer les configurations
kubectl apply -f sample-app-deployment.yml
kubectl apply -f sample-app-service.yml

# Vérifier le statut
kubectl get deployments
kubectl get pods
kubectl get services

# Voir les logs
kubectl logs -l app=sample-app-pods

# Rolling update
kubectl set image deployment/sample-app-deployment sample-app=sample-app:v2
```

---

## Concepts clés

| Concept | Description |
|---------|-------------|
| **Deployment** | Gère les ReplicaSets et les mises à jour |
| **Service** | Expose les pods avec une IP stable |
| **Rolling Update** | Mise à jour progressive sans downtime |
| **Labels & Selectors** | Liaison entre Service et Pods |

<!-- 
## À compléter

- Captures d'écran du dashboard Kubernetes
- Résultats des tests de charge
- Observations sur les rolling updates
-->
