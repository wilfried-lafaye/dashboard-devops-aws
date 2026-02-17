---
title: "TD1 - Déploiement EC2 avec User Data"
publish: true
---

# TD1 - Déploiement EC2 avec User Data

## Objectif

Déployer une application Node.js sur une instance EC2 AWS en utilisant les User Data scripts pour l'automatisation du provisionnement.

## Concepts clés

- **User Data**: Script exécuté automatiquement au premier démarrage d'une instance EC2
- **Systemd**: Gestionnaire de services Linux pour garantir que l'app tourne en permanence
- **Security Groups**: Pare-feu AWS pour contrôler le trafic réseau

## Script User Data

Ce script installe Node.js, crée une application simple et configure un service Systemd :

```bash
#!/bin/bash
set -euxo pipefail
# Redirection des logs pour le débogage (indispensable en cas d'erreur)
exec > >(tee /var/log/user-data.log | logger -t user-data) 2>&1

# 1. Installation de Node.js (Gestion de la compatibilité Amazon Linux 2 vs 2023)
if grep -qi "Amazon Linux 2" /etc/system-release; then
  yum -y update
  curl -fsSL https://rpm.nodesource.com/setup_20.x | bash -
  yum -y install nodejs
else
  dnf -y update
  curl -fsSL https://rpm.nodesource.com/setup_20.x | bash -
  dnf -y install nodejs
fi

# 2. Création du dossier et de l'application dans /opt (plus propre que le home directory)
mkdir -p /opt/sample-app
cat >/opt/sample-app/app.js <<'EOF'
const http = require('http');
const port = process.env.PORT || 8080;
const server = http.createServer((req,res)=>{
    res.writeHead(200,{'Content-Type':'text/plain'});
    res.end('Hello from EC2 running with Systemd!\n');
});
server.listen(port, '0.0.0.0', () => console.log('Listening on', port));
EOF

# 3. Création du service Systemd (La solution aux problèmes du Lab)
cat >/etc/systemd/system/sample-app.service <<'EOF'
[Unit]
Description=Sample Node app
After=network-online.target
Wants=network-online.target

[Service]
WorkingDirectory=/opt/sample-app
ExecStart=/usr/bin/node /opt/sample-app/app.js
# Redémarrage automatique en cas de crash
Restart=always
# Utilisateur root utilisé ici pour simplifier (comme noté dans ton script)
User=root
Environment=PORT=8080

[Install]
# Permet à l'app de se lancer au démarrage du serveur
WantedBy=multi-user.target
EOF

# 4. Activation et démarrage du service
systemctl daemon-reload
systemctl enable --now sample-app
```

## Points importants

> [!TIP]
> Utiliser Systemd plutôt qu'un simple `node app.js &` garantit que l'application redémarre automatiquement en cas de crash et au reboot de l'instance.

> [!WARNING]
> Les logs User Data sont stockés dans `/var/log/user-data.log` - indispensable pour le débogage.

## Résultat attendu

Après le déploiement, l'application est accessible sur `http://<IP_PUBLIQUE>:8080` et répond "Hello from EC2 running with Systemd!".

<!-- 
## À compléter

- Captures d'écran de votre déploiement
- Problèmes rencontrés et solutions
- Améliorations possibles
-->
