# CycleVPN v2.0 - Rotation Automatique de Serveurs VPN

Un outil avancé de rotation automatique de serveurs VPN avec kill switch intégré et gestion sécurisée des connexions.

## ⚡ Fonctionnalités Principales

- **🔄 Rotation automatique** : Change de serveur VPN à intervalles réguliers
- **🛡️ Kill Switch avancé** : Protège contre les fuites de données en cas de panne VPN
- **🔒 Sécurité renforcée** : Gestion sécurisée des identifiants et vérification d'IP
- **📝 Logs avancés** : Système de logging avec rotation automatique
- **⚙️ Configuration flexible** : Paramètres personnalisables via JSON
- **🔧 Gestion de services** : Contrôle automatique des services système (Transmission)

## 🚀 Installation Rapide

### Prérequis
```bash
# Vérifiez que vous avez :
- Python 3.8+
- OpenVPN installé
- Privilèges administrateur
```

### Installation
```bash
# Clonez le projet
git clone https://github.com/votre-repo/CycleVPN.git
cd CycleVPN

# Installez les dépendances
pip install -r requirements.txt

# Lancez l'application
python main.py
```

## 📁 Structure du Projet

```
CycleVPN/
├── main.py              # Application principale
├── config.json          # Configuration
├── config_manager.py    # Gestionnaire de configuration
├── logger_manager.py    # Gestionnaire de logs
├── kill_switch.py       # Kill switch avancé
├── vpn_manager.py       # Gestionnaire VPN
├── openvpn/            # Fichiers .ovpn
└── requirements.txt    # Dépendances
```

## ⚙️ Configuration

Le fichier `config.json` contient tous les paramètres configurables :

```json
{
  "session": {
    "cooldown_seconds": 3600,     // Durée de chaque session (1h)
    "max_connection_failures": 3,  // Échecs max avant arrêt
    "kill_switch_enabled": true   // Activer le kill switch
  },
  "network": {
    "connection_timeout": 15,     // Timeout de connexion
    "vpn_establish_wait": 20,     // Attente établissement VPN
    "ip_check_retries": 3         // Tentatives de vérification IP
  },
  "services": {
    "transmission_service": "transmission",
    "openvpn_service": "openvpn"
  },
  "logging": {
    "level": "INFO",              // Niveau de log
    "rotation": "10 MB",          // Rotation des logs
    "retention": "7 days"         // Rétention des logs
  }
}
```

## 🎯 Utilisation

### Démarrage Simple
```bash
python main.py
```

L'application vous demandera :
1. **Identifiants VPN** : Username et password
2. **Confirmation** : Vérification des prérequis
3. **Rotation** : Démarrage automatique de la rotation

### Fonctionnement
1. **Initialisation** : Vérification des fichiers .ovpn et connectivité
2. **Connexion** : Établissement VPN avec le premier serveur
3. **Vérification** : Contrôle du changement d'IP
4. **Rotation** : Changement automatique après le délai configuré
5. **Protection** : Kill switch en cas de problème

## 🛡️ Kill Switch

Le kill switch protège contre les fuites de données :

### Protection Automatique
- **Vérification d'IP** : Contrôle que l'IP a changé
- **Monitoring VPN** : Surveillance des processus OpenVPN
- **Arrêt des services** : Fermeture automatique si VPN échoue

### Activation d'Urgence
- **Ctrl+C** : Arrêt propre avec kill switch
- **Blocage réseau** : Fermeture de tous les services sensibles
- **Nettoyage** : Suppression sécurisée des fichiers temporaires

## 📊 Logs et Monitoring

Les logs sont disponibles dans `cyclevpn.log` :
- Connexions/déconnexions VPN
- Changements d'IP
- Erreurs et diagnostics
- Activité du kill switch

Pour plus de détails, changez le niveau de log :
```json
"logging": {
    "level": "DEBUG"
}
```

## 🔧 Personnalisation

### Ajouter des Serveurs VPN
1. Placez vos fichiers `.ovpn` dans le dossier `openvpn/`
2. Relancez l'application

### Modifier les Services
```json
"services": {
    "transmission_service": "votre-service",
    "openvpn_service": "openvpn"
}
```

### Ajuster les Timings
```json
"session": {
    "cooldown_seconds": 1800,  // 30 minutes
    "max_connection_failures": 5
}
```

## 🚨 Dépannage

### Problèmes Courants
| Problème | Solution |
|----------|----------|
| Pas de fichiers .ovpn | Placez vos fichiers dans `openvpn/` |
| Permissions refusées | Lancez avec privilèges administrateur |
| Service non trouvé | Vérifiez les noms dans `config.json` |
| IP inchangée | Vérifiez votre configuration VPN |

### Débuggage
```bash
# Activez les logs détaillés
# Dans config.json : "level": "DEBUG"

# Vérifiez les logs
tail -f cyclevpn.log
```

## 🔒 Sécurité

- **Identifiants** : Stockage temporaire sécurisé avec permissions restreintes
- **Nettoyage** : Suppression automatique des fichiers d'authentification
- **Vérification** : Contrôle obligatoire des changements d'IP
- **Kill Switch** : Protection contre les fuites de données

## 📋 Dépendances

```
colorama>=0.4.6    # Interface colorée
loguru>=0.7.2      # Logging avancé
requests>=2.31.0   # Vérification d'IP
psutil>=5.9.0      # Gestion des processus
```

## 🎉 Fonctionnalités Avancées

- **Mélange aléatoire** : Ordre des serveurs randomisé
- **Récupération automatique** : Retry en cas d'échec
- **Arrêt propre** : Gestion des signaux système
- **Monitoring continu** : Surveillance des processus VPN

---

**Version** : 2.0  
**Licence** : MIT  
**Support** : Consultez les logs pour le diagnostic 