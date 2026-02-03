# Guide des Commandes Docker et Minikube

## Pour lancer l'API et accéder via le port 8080 avec Minikube 

```bash
kubectl port-forward -n air-quality service/frontend 8080:80
```

Accès : **http://localhost:8080**

---

## Commandes Docker

### Construction des images

```bash
# Construire l'image backend
docker build -t air-quality-backend:latest ./backend

# Construire l'image frontend
docker build -t air-quality-frontend:latest ./frontend

# Construire les deux images
docker build -t air-quality-backend:latest ./backend && docker build -t air-quality-frontend:latest ./frontend
```

### Docker Compose - Développement

```bash
# Démarrer les services
docker compose up -d

# Démarrer avec reconstruction
docker compose up --build -d

# Démarrer avec mode watch (hot-reload)
docker compose up --watch

# Afficher les logs
docker compose logs -f

# Afficher les logs d'un service spécifique
docker compose logs -f backend

# Arrêter les services
docker compose down

# Arrêter et supprimer les volumes
docker compose down -v
```

### Gestion des images Docker

```bash
# Lister les images
docker images

# Supprimer une image
docker rmi air-quality-backend:latest

# Supprimer les images non utilisées
docker image prune
```

### Gestion des conteneurs Docker

```bash
# Lister les conteneurs en cours d'exécution
docker ps

# Lister tous les conteneurs
docker ps -a

# Voir les logs d'un conteneur
docker logs container_name

# Accéder à un shell dans un conteneur
docker exec -it container_name /bin/bash
```

---

## Commandes Minikube

### Configuration initiale

```bash
# Démarrer minikube
minikube start

# Arrêter minikube
minikube stop

# Supprimer minikube
minikube delete

# Configurer l'environnement Docker local
eval $(minikube docker-env)
```

### Gestion des services

```bash
# Lister tous les services
minikube service list

# Accéder à un service (ouvre le navigateur)
minikube service frontend -n air-quality

# Accéder au backend
minikube service backend -n air-quality

# Créer un tunnel réseau stable
minikube tunnel
```

### Diagnostic

```bash
# Voir le statut de minikube
minikube status

# Voir les logs de minikube
minikube logs

# Voir les logs dans un fichier
minikube logs --file=logs.txt

# Afficher les informations du cluster
minikube info
```

### Dashboard

```bash
# Ouvrir le dashboard Kubernetes
minikube dashboard
```

---

## Commandes Kubernetes (kubectl)

### Application des configurations

```bash
# Appliquer tous les fichiers K8s de manière récursive
kubectl apply -f k8s/ --recursive

# Appliquer un seul fichier
kubectl apply -f k8s/namespace.yaml

# Appliquer le fichier et afficher le résultat
kubectl apply -f k8s/ --recursive -o wide
```

### Gestion des ressources

```bash
# Lister tous les services du namespace air-quality
kubectl get svc -n air-quality

# Lister tous les pods du namespace air-quality
kubectl get pods -n air-quality

# Lister tous les déploiements
kubectl get deployment -n air-quality

# Lister tous les ressources
kubectl get all -n air-quality

# Surveiller les pods en temps réel
kubectl get pods -n air-quality -w
```

### Inspections détaillées

```bash
# Voir les détails d'un pod
kubectl describe pod pod_name -n air-quality

# Voir les détails d'un déploiement
kubectl describe deployment backend -n air-quality

# Voir les détails d'un service
kubectl describe svc frontend -n air-quality

# Voir les événements du cluster
kubectl get events -n air-quality
```

### Logs et débogage

```bash
# Voir les logs d'un pod
kubectl logs pod_name -n air-quality

# Voir les logs en temps réel
kubectl logs -f pod_name -n air-quality

# Voir les logs des 100 dernières lignes
kubectl logs --tail=100 pod_name -n air-quality

# Accéder au shell d'un pod
kubectl exec -it pod_name -n air-quality -- /bin/bash

# Exécuter une commande dans un pod
kubectl exec pod_name -n air-quality -- command
```

### Port forwarding

```bash
# Rediriger le port du frontend
kubectl port-forward -n air-quality service/frontend 8080:80

# Rediriger le port du backend
kubectl port-forward -n air-quality service/backend 8000:8000

# Rediriger le port de PostgreSQL
kubectl port-forward -n air-quality service/postgres 5432:5432
```

### Suppression des ressources

```bash
# Supprimer le namespace (supprime toutes les ressources)
kubectl delete namespace air-quality

# Supprimer un déploiement spécifique
kubectl delete deployment backend -n air-quality

# Supprimer un service spécifique
kubectl delete service frontend -n air-quality
```

---

## Commandes utiles pour minikube : 