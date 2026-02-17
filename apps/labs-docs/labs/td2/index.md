---
title: "TD2 - Infrastructure as Code"
publish: true
---

# TD2 - Infrastructure as Code

## Objectif

Automatiser le déploiement d'instances EC2 en utilisant trois approches différentes d'Infrastructure as Code (IaC).

## Approches comparées

| Outil | Type | Avantages |
|-------|------|-----------|
| **Bash/AWS CLI** | Impératif | Simple, rapide pour prototyper |
| **Ansible** | Configuration Management | Idempotent, lisible, agentless |
| **OpenTofu** | Déclaratif | State management, modules réutilisables |

---

## 1. Déploiement avec Bash/AWS CLI

Script bash pour créer un Security Group et lancer une instance EC2 :

```bash
#!/usr/bin/env bash
set -e

# 1. Setup Variables
export AWS_DEFAULT_REGION="us-east-1"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# Ensure user-data exists before catting it to avoid errors
if [ -f "$SCRIPT_DIR/user-data.sh" ]; then
    user_data=$(cat "$SCRIPT_DIR/user-data.sh")
else
    echo "Error: user-data.sh not found."
    exit 1
fi

# 2. Create Security Group
echo "Creating Security Group..."
security_group_id=$(aws ec2 create-security-group \
  --group-name "sample-app-$(date +%s)" \
  --description "Allow HTTP traffic into the sample app" \
  --output text \
  --query GroupId)

# 3. Authorize Traffic
echo "Authorizing Ingress..."
aws ec2 authorize-security-group-ingress \
  --group-id "$security_group_id" \
  --protocol tcp \
  --port 8080 \
  --cidr "0.0.0.0/0" > /dev/null

# 4. Launch Instance
echo "Launching Instance..."
instance_id=$(aws ec2 run-instances \
  --image-id "ami-0fa3fe0fa7920f68e" \
  --instance-type "t3.micro" \
  --security-group-ids "$security_group_id" \
  --user-data "$user_data" \
  --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=sample-app}]' \
  --output text \
  --query Instances[0].InstanceId)

# 5. WAIT for the instance to run (Crucial Step)
echo "Waiting for instance $instance_id to be running..."
aws ec2 wait instance-running --instance-ids "$instance_id"

# 6. Get Public IP
public_ip=$(aws ec2 describe-instances \
  --instance-ids "$instance_id" \
  --output text \
  --query 'Reservations[*].Instances[*].PublicIpAddress')

# 7. Output
echo "--------------------------------"
echo "Instance ID       = $instance_id"
echo "Security Group ID = $security_group_id"
echo "Public IP         = $public_ip"
echo "--------------------------------"
```

---

## 2. Déploiement avec Ansible

Playbook Ansible pour créer les ressources AWS :

```yaml
- name: Deploy an EC2 instance in AWS
  hosts: localhost
  gather_facts: no
  environment:
    AWS_REGION: us-east-1
  tasks:    
    - name: Create security group                      
      amazon.aws.ec2_security_group:
        name: sample-app-ansible 
        description: Allow HTTP and SSH traffic
        rules:
          - proto: tcp
            ports: [8080]
            cidr_ip: 0.0.0.0/0
          - proto: tcp
            ports: [22]
            cidr_ip: 0.0.0.0/0
      register: aws_security_group

    - name: Create a new EC2 key pair                  
      amazon.aws.ec2_key:
        name: ansible-ch2
        file_name: ansible-ch2.key                     
      no_log: true
      register: aws_ec2_key_pair

    - name: Create EC2 instance with Amazon Linux 2003 
      amazon.aws.ec2_instance:
        name: sample-app-ansible
        key_name: "{{ aws_ec2_key_pair.key.name }}"
        instance_type: t3.micro
        security_group: "{{ aws_security_group.group_id }}"
        image_id: ami-0fa3fe0fa7920f68e
        tags:
          Ansible: ch2_instances                       
```

---

## 3. Déploiement avec OpenTofu

Configuration Terraform/OpenTofu avec modules :

```hcl
# main.tf (Racine)

provider "aws" {
  region = "us-east-1"
}

module "app_fleet" {
  # Chemin vers le dossier contenant vos fichiers envoyés
  source = "./modules/ec2-instance"

  # --- LA BOUCLE MAGIQUE ---
  for_each = var.server_config

  # --- Paramètres dynamiques (changent pour chaque instance) ---
  # each.key = "server-blue", "server-green", etc.
  name      = each.key
  
  # each.value = 8080, 8081, etc.
  http_port = each.value

  # --- Paramètres statiques (les mêmes pour tous) ---
  ami_id        = var.ami_id
  key_name      = var.key_name
  instance_type = "t3.micro"
}
```

> [!TIP]
> L'utilisation de `for_each` permet de déployer plusieurs instances avec des configurations différentes à partir d'une seule définition de module.

---

## Comparaison des approches

| Critère | Bash | Ansible | OpenTofu |
|---------|------|---------|----------|
| Idempotence | ❌ | ✅ | ✅ |
| State Management | ❌ | ❌ | ✅ |
| Lisibilité | ⚠️ | ✅ | ✅ |
| Courbe d'apprentissage | Faible | Moyenne | Moyenne |

<!-- 
## À compléter

- Ajoutez vos observations personnelles
- Captures d'écran des résultats
- Difficultés rencontrées
-->
