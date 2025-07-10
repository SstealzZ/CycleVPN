# CycleVPN v2.0 - Advanced VPN Rotation Tool

CycleVPN est un outil avancé de rotation automatique de serveurs VPN qui permet de changer automatiquement de serveur VPN à intervalles réguliers tout en gérant les services réseau associés.

## ✨ Nouvelles Fonctionnalités v2.0

### 🔧 Architecture Modulaire
- **Configuration centralisée** : Fichier `config.json` pour tous les paramètres
- **Logging avancé** : Utilisation de Loguru pour des logs structurés
- **Kill Switch amélioré** : Protection réseau avancée en cas de défaillance VPN
- **Gestion de services** : Contrôle automatique des services système

### 🛡️ Sécurité Renforcée
- **Vérification d'IP** : Validation automatique des changements d'IP
- **Gestion sécurisée des identifiants** : Fichiers temporaires avec permissions restreintes
- **Arrêt d'urgence** : Fermeture sécurisée en cas de problème critique
- **Blocage de services** : Empêche les fuites de données en cas d'échec VPN

### 📊 Monitoring et Logging
- **Logs rotatifs** : Gestion automatique de la taille des logs
- **Logging coloré** : Interface utilisateur améliorée
- **Métriques de session** : Suivi des connexions et des échecs
- **Debugging avancé** : Logs détaillés pour le diagnostic

## 🚀 Installation

### Prérequis
- Python 3.8+
- OpenVPN installé
- Privilèges administrateur (pour la gestion des services)
- Accès Internet pour la vérification d'IP

### Installation des dépendances
```bash
pip install -r requirements.txt
```

## ⚙️ Configuration

### Fichier de Configuration (`config.json`)
```json
{
  "network": {
    "connection_timeout": 10,
    "vpn_establish_wait": 5,
    "ip_check_retries": 3,
    "ip_check_timeout": 5
  },
  "session": {
    "cooldown_seconds": 20,
    "max_connection_failures": 3,
    "kill_switch_enabled": true
  },
  "services": {
    "transmission_service": "transmission",
    "openvpn_service": "openvpn"
  },
  "paths": {
    "ovpn_directory": "./openvpn",
    "log_file": "cyclevpn.log",
    "temp_directory": "/tmp"
  },
  "logging": {
    "level": "INFO",
    "rotation": "10 MB",
    "retention": "7 days",
    "format": "{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}"
  },
  "security": {
    "clear_credentials_on_exit": true,
    "secure_temp_files": true,
    "verify_ip_change": true
  }
}
```

### Paramètres Configurables

#### Réseau
- `connection_timeout` : Timeout pour les connexions réseau
- `vpn_establish_wait` : Temps d'attente pour l'établissement VPN
- `ip_check_retries` : Nombre de tentatives de vérification d'IP
- `ip_check_timeout` : Timeout pour la vérification d'IP

#### Session
- `cooldown_seconds` : Durée de chaque session VPN
- `max_connection_failures` : Nombre maximum d'échecs avant arrêt
- `kill_switch_enabled` : Activation du kill switch

#### Services
- `transmission_service` : Nom du service Transmission
- `openvpn_service` : Nom du service OpenVPN

#### Chemins
- `ovpn_directory` : Répertoire des fichiers .ovpn
- `log_file` : Fichier de logs
- `temp_directory` : Répertoire temporaire

#### Logging
- `level` : Niveau de log (DEBUG, INFO, WARNING, ERROR)
- `rotation` : Taille de rotation des logs
- `retention` : Durée de conservation des logs
- `format` : Format des messages de log

#### Sécurité
- `clear_credentials_on_exit` : Effacer les identifiants à la fermeture
- `secure_temp_files` : Utiliser des fichiers temporaires sécurisés
- `verify_ip_change` : Vérifier les changements d'IP

## 🎯 Utilisation

### Démarrage Simple
```bash
python main.py
```

### Structure des Fichiers
```
CycleVPN/
├── main.py                 # Application principale
├── config.json            # Configuration
├── requirements.txt       # Dépendances
├── config_manager.py      # Gestionnaire de configuration
├── logger_manager.py      # Gestionnaire de logs
├── kill_switch.py         # Kill switch avancé
├── vpn_manager.py         # Gestionnaire VPN
├── openvpn/              # Fichiers de configuration VPN
│   ├── france.ovpn
│   ├── us_california.ovpn
│   └── ...
└── cyclevpn.log          # Fichier de logs
```

## 🔄 Fonctionnement

1. **Initialisation** : Chargement de la configuration et vérification des prérequis
2. **Authentification** : Saisie des identifiants VPN
3. **Rotation** : Cycle automatique à travers les serveurs VPN
4. **Monitoring** : Surveillance continue des connexions
5. **Protection** : Activation du kill switch en cas de problème

## 🛡️ Kill Switch Avancé

Le kill switch v2.0 offre plusieurs niveaux de protection :

### Protection Automatique
- **Vérification d'IP** : Contrôle que l'IP a bien changé
- **Monitoring des processus** : Surveillance des processus OpenVPN
- **Arrêt des services** : Fermeture automatique des services en cas d'échec

### Activation Manuelle
- **Blocage immédiat** : Fermeture de tous les services réseau
- **Arrêt d'urgence** : Fermeture sécurisée de l'application
- **Nettoyage** : Suppression des fichiers temporaires

## 📋 Architecture du Code

### Modules Principaux

#### ConfigManager
- Gestion centralisée de la configuration
- Validation des paramètres
- Création automatique des répertoires

#### LoggerManager  
- Logging avec Loguru
- Rotation et rétention automatiques
- Logs colorés pour la console

#### KillSwitch
- Protection réseau avancée
- Vérification d'IP multi-services
- Gestion des processus système

#### VPNManager
- Gestion des connexions VPN
- Rotation automatique des serveurs
- Intégration avec les services système

#### CycleVPNApplication
- Orchestration des composants
- Gestion des signaux système
- Interface utilisateur

## 🔧 Développement

### Ajout de Nouveaux Fournisseurs VPN
1. Ajouter les fichiers `.ovpn` dans le répertoire `openvpn/`
2. Modifier la configuration si nécessaire
3. Tester la connexion

### Personnalisation des Services
1. Modifier `services` dans `config.json`
2. Adapter les commandes dans `VPNManager`
3. Tester la gestion des services

### Extension du Kill Switch
1. Ajouter de nouvelles méthodes dans `KillSwitch`
2. Intégrer avec `VPNManager`
3. Tester les scénarios d'échec

## 📊 Monitoring

### Logs Disponibles
- **Connexions VPN** : Établissement et fermeture
- **Changements d'IP** : Vérification et validation
- **Gestion des services** : Démarrage et arrêt
- **Erreurs** : Diagnostic et debugging

### Métriques
- Taux de succès des connexions
- Temps de réponse des services
- Historique des changements d'IP
- Statistiques d'utilisation

## 🚨 Dépannage

### Problèmes Courants
1. **Pas de fichiers .ovpn** : Vérifier le répertoire `openvpn/`
2. **Permissions insuffisantes** : Exécuter avec privilèges administrateur
3. **Services non trouvés** : Vérifier les noms dans `config.json`
4. **Pas de connexion Internet** : Vérifier la connectivité réseau

### Logs de Debug
```bash
# Modifier le niveau de log dans config.json
"logging": {
    "level": "DEBUG"
}
```

## 🔒 Sécurité

### Bonnes Pratiques
- Utiliser des identifiants uniques pour chaque service VPN
- Activer le kill switch pour toutes les sessions
- Vérifier régulièrement les logs
- Maintenir les fichiers de configuration sécurisés

### Fichiers Sensibles
- `config.json` : Paramètres de configuration
- Fichiers temporaires : Supprimés automatiquement
- Logs : Peuvent contenir des informations sensibles

## 📞 Support

Pour toute question ou problème :
1. Consulter les logs dans `cyclevpn.log`
2. Vérifier la configuration dans `config.json`
3. Tester manuellement les connexions VPN
4. Augmenter le niveau de debug si nécessaire

## 🎉 Fonctionnalités Avancées

### Rotation Intelligente
- Mélange aléatoire des serveurs
- Évitement des serveurs défaillants
- Optimisation des temps de connexion

### Gestion d'Erreurs
- Récupération automatique des échecs
- Retry logic configurables
- Escalade des erreurs critiques

### Intégration Système
- Gestion des signaux Unix
- Arrêt propre sur interruption
- Nettoyage automatique des ressources 