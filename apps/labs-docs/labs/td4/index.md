---
title: "TD4 - Containerisation Docker"
publish: true
---

# TD4 - Containerisation Docker

## Objectif

Containeriser une application Node.js/Express avec Docker et configurer le build multi-architecture.

## Structure du projet

```
sample-app/
├── Dockerfile
├── package.json
├── build-docker-image.sh
└── src/
    └── app.js
```

---

## Script de build multi-architecture

Script pour construire des images Docker compatibles AMD64 et ARM64 :

```bash
#!/usr/bin/env bash

set -e

name=$(npm pkg get name | tr -d '"')
version=$(npm pkg get version | tr -d '"')

docker buildx build \
  --platform=linux/amd64,linux/arm64 \
  --load \
  -t "$name:$version" \
  .
```

> [!NOTE]
> `docker buildx` permet de créer des images multi-architecture en une seule commande, essentielles pour les déploiements sur AWS Graviton (ARM).

---

## Dockerfile optimisé

Exemple de Dockerfile multi-stage pour une application Node.js :

```dockerfile
# Stage 1: Build
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

# Stage 2: Production
FROM node:20-alpine AS production
WORKDIR /app

# Sécurité: utilisateur non-root
RUN addgroup -g 1001 -S nodejs && \
    adduser -S nodejs -u 1001

COPY --from=builder /app/node_modules ./node_modules
COPY --chown=nodejs:nodejs . .

USER nodejs

EXPOSE 8080

CMD ["node", "src/app.js"]
```

---

## Commandes Docker essentielles

```bash
# Build de l'image
./build-docker-image.sh

# Ou manuellement
docker build -t sample-app:v1 .

# Lancer le conteneur
docker run -d -p 8080:8080 --name sample-app sample-app:v1

# Voir les logs
docker logs -f sample-app

# Push vers un registry
docker tag sample-app:v1 registry.example.com/sample-app:v1
docker push registry.example.com/sample-app:v1
```

---

## Variantes du projet

| Version | Description |
|---------|-------------|
| `sample-app` | Application Node.js basique |
| `sample-app-express` | Application avec Express.js |
| `sample-app-express-with-tests` | Application avec tests Jest |

---

## Bonnes pratiques Docker

> [!IMPORTANT]
> **Sécurité** : Toujours utiliser un utilisateur non-root dans les conteneurs de production.

> [!TIP]
> **Performance** : Utiliser le multi-stage build pour réduire la taille de l'image finale.

| Pratique | Raison |
|----------|--------|
| Images Alpine | Taille réduite (~50MB vs ~900MB) |
| Multi-stage build | Sépare le build du runtime |
| `.dockerignore` | Évite de copier node_modules local |
| User non-root | Sécurité renforcée |

<!-- 
## À compléter

- Taille des images avant/après optimisation
- Résultats des tests
- Configuration CI/CD avec Docker
-->
