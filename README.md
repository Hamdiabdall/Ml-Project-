# Analyse et Modélisation de la Consommation Énergétique Française

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Python](https://img.shields.io/badge/python-3.7+-yellow.svg)
![Framework](https://img.shields.io/badge/framework-PyQt5-brightgreen.svg)

Application d'analyse dynamique et interactive de la consommation électrique et de gaz des Français basée sur des données officielles. Permet le téléchargement direct depuis la plateforme OpenData Réseaux Énergies (ODRE).

## 📋 Description du Projet

Cette application Python propose un outil complet d'analyse et de visualisation des données de consommation énergétique en France. Développée dans le cadre d'un projet d'analyse de données énergétiques, elle permet d'explorer les tendances de consommation, d'effectuer des analyses statistiques et de générer des visualisations graphiques personnalisées.

### Contexte

L'évolution de la consommation énergétique (électricité et gaz) des Français est un enjeu majeur à la fois écologique, économique et politique. Comprendre et analyser ces données est essentiel pour:
- Évaluer l'efficacité des politiques énergétiques
- Anticiper les besoins futurs
- Étudier l'impact des saisons et événements exceptionnels
- Contribuer à la transition énergétique

### Objectifs

- Fournir un outil d'analyse interactif accessible aux non-spécialistes
- Permettre le chargement et la manipulation de données énergétiques officielles
- Offrir des analyses statistiques personnalisables
- Générer des visualisations graphiques claires et informatives
- Intégrer des fonctions d'approximation pour détecter les tendances

## 🛠️ Installation

### Prérequis

- Python 3.7 ou supérieur
- Pip (gestionnaire de paquets Python)
- Connexion internet pour le chargement de données en ligne (optionnel)

### Étapes d'installation

1. Clonez ou téléchargez ce dépôt
2. Installez les dépendances requises :

```bash
pip install -r requirements.txt
```

## 📦 Dépendances

Les bibliothèques suivantes sont nécessaires au fonctionnement de l'application :

- **pandas (≥1.3.0)** : Manipulation et analyse de données
- **numpy (≥1.20.0)** : Calculs numériques et traitement de tableaux
- **matplotlib (≥3.4.0)** : Visualisation de données
- **scikit-learn (≥1.0.0)** : Algorithmes d'apprentissage automatique pour l'approximation
- **PyQt5 (≥5.15.0)** : Interface graphique
- **requests (≥2.25.0)** : Requêtes HTTP pour le téléchargement de données

## 🚀 Démarrage

Pour lancer l'application, exécutez la commande suivante depuis le répertoire du projet :

```bash
python main.py
```

### Guide rapide d'utilisation

1. **Télécharger les données depuis OpenData**
   ```
   Fichier > Charger depuis une URL
   ```
   L'URL par défaut pour OpenData est déjà préremplie. Cliquez simplement sur OK pour télécharger les données les plus récentes.

2. **Lancer une analyse statistique**
   ```
   Bouton "Lancer l'analyse"
   ```
   Après le chargement des données, l'application configure automatiquement la plage de dates optimale.

3. **Visualiser les tendances**
   ```
   Bouton "Tracer le graphique"
   ```
   Sélectionnez le type de graphique et ajoutez une fonction d'approximation si nécessaire.

4. **Exporter les résultats**
   ```
   Fichier > Exporter le graphique
   ```
   Sauvegardez vos visualisations au format PNG, JPG ou PDF.

## 📊 Fonctionnalités et utilisation

### 1. Chargement des données
- **Fichier local** : Cliquez sur "Charger un fichier" pour sélectionner un fichier CSV local
- **Depuis OpenData** : Utilisez le menu "Fichier > Charger depuis une URL" pour importer directement depuis la plateforme officielle ODRE
- **Intégration OpenData** : L'application détecte automatiquement l'URL de la plateforme ODRE et effectue le téléchargement des données les plus récentes
- **Détection intelligente** : Support de multiples formats CSV (différents séparateurs, encodages et structures de colonnes)
- **Conservation des données** : Sauvegarde automatique dans le dossier ressources/exemples pour une utilisation future

### 2. Analyse statistique
- **Plage de dates** : Sélectionnez précisément la période à analyser
- **Type de consommation** : Choisissez entre électricité et gaz
- **Statistiques disponibles** :
  - Valeur minimale et date correspondante
  - Valeur maximale et date correspondante
  - Consommation moyenne sur la période
  - Nombre de jours dépassant un seuil défini
  - Nombre de jours sous un seuil défini

### 3. Visualisation graphique
- **Types de graphiques** :
  - Ligne : Idéal pour visualiser l'évolution temporelle
  - Barre : Pratique pour comparer des périodes
- **Fonctions d'approximation** :
  - Régression linéaire (degré 1)
  - Régression polynomiale (degrés 2 à 5)
- **Exportation** : Enregistrement du graphique en PNG, JPG ou PDF

### 4. Interface utilisateur
- **Menu principal** : Accès rapide aux fonctionnalités avec raccourcis clavier
- **Panneau de contrôle** : Configuration intuitive des paramètres d'analyse
- **Zone de résultats** : Affichage clair des statistiques calculées
- **Zone graphique** : Visualisation interactive des données
- **Barre d'état** : Informations sur l'état de l'application et les opérations en cours

## 🔍 Structure du projet

```
/projet/
│
├── main.py                    # Point d'entrée de l'application
├── ui_interface.ui           # Interface Qt Designer
├── interface.py              # Gestion de l'interface utilisateur
├── data_loader.py            # Chargement des données (local et API OpenData)
├── data_analysis.py          # Analyse statistique des données
├── visualisation.py          # Création et gestion des graphiques
├── utils.py                  # Fonctions utilitaires
├── README.md                 # Documentation du projet
├── requirements.txt          # Dépendances du projet
├── logs/                     # Journaux d'exécution
├── temp/                     # Fichiers temporaires
└── ressources/
     └── exemples/            # Fichiers CSV d'exemple et données téléchargées
```

## 📝 Format des données

L'application est conçue pour traiter des fichiers CSV structurés comme suit :
- Une colonne temporelle au format date (YYYY-MM-DD) ou horodatage (YYYY-MM-DDThh:mm:ss)
- Une ou plusieurs colonnes de données numériques représentant la consommation d'électricité et/ou de gaz
- Séparateur de colonnes : point-virgule (;) ou virgule (,)

Exemple de format compatible :
```
Date;Consommation brute électricité (MW);Consommation brute gaz (MW)
2024-01-01;54321;32154
2024-01-02;52345;31245
...
```

## 🔒 Gestion des erreurs et robustesse

L'application intègre une gestion exceptionnellement robuste des erreurs :
- **Validation multi-niveaux** des formats de fichiers (CSV, JSON, etc.)
- **Détection intelligente des colonnes** avec reconnaissance par pattern matching
- **Détection automatique des séparateurs** (virgule, point-virgule, tabulation)
- **Support multi-encodage** (UTF-8, Latin-1, etc.)
- **Traitement des valeurs manquantes** avec stratégies adaptatives
- **Messages d'erreur contextuels** guidés par l'analyse des données
- **Système de journalisation avancé** avec niveaux de détail configurables
- **Conservation des fichiers problématiques** pour analyse et correction

## 🔧 Personnalisation et extension

Le projet est conçu de manière modulaire et peut être facilement étendu :
- Ajout de nouveaux types d'analyses statistiques
- Intégration d'algorithmes de prédiction plus avancés
- Support de formats de données additionnels
- Personnalisation de l'interface utilisateur

## 📈 Cas d'utilisation

Cette application peut être utilisée pour :
- **Analyse des tendances temporelles** de consommation énergétique française
- **Étude comparative** des évolutions électricité/gaz sur différentes périodes
- **Détection de patterns saisonniers** et impact des conditions climatiques
- **Évaluation de l'efficacité** des politiques énergétiques
- **Anticipation des besoins futurs** grâce aux fonctions d'approximation
- **Identification des anomalies** et pics de consommation exceptionnels
- **Création de visualisations** pour rapports et présentations professionnelles
- **Suivi en temps réel** des données énergétiques nationales grâce à l'intégration OpenData
- **Analyse des corrélations** entre consommation électrique et gazière
- **Support à la décision** pour les acteurs du secteur énergétique

## 🔄 Mises à jour et améliorations

### Version 1.0.0 (Avril 2025)
- **Intégration complète de l'API OpenData** pour téléchargement direct des données
- **Refonte du système de chargement de données** avec détection intelligente des formats
- **Amélioration de la robustesse** face aux différentes structures de fichiers CSV
- **Mise à jour automatique des paramètres d'analyse** en fonction des données chargées
- **Optimisation des performances** pour le traitement de fichiers volumineux
- **Interface utilisateur améliorée** avec instructions contextuelles

## 🐛 Problèmes connus et solutions

- **Fichiers volumineux** : Les fichiers CSV de très grande taille peuvent ralentir l'application. 
  *Solution* : Utiliser la fonctionnalité de filtrage par date pour réduire le volume de données traitées.
  
- **Formats de date particuliers** : Certains formats de date très spécifiques peuvent poser problème. 
  *Solution* : L'application implémente désormais une détection multi-format qui résout la plupart des cas problématiques.
  
- **Compatibilité des graphiques** : Sur certains systèmes Windows, l'intégration matplotlib peut nécessiter des ajustements. 
  *Solution* : Mettre à jour matplotlib (`pip install -U matplotlib`) et PyQt5 (`pip install -U PyQt5`).
  
- **Accès à l'API OpenData** : Des limitations d'accès peuvent survenir en cas de trafic important. 
  *Solution* : L'application sauvegarde automatiquement les données téléchargées pour une utilisation hors-ligne.

## 📋 Contributions

Les contributions à ce projet sont les bienvenues. Pour contribuer :
1. Forker le projet
2. Créer une branche (`git checkout -b feature/nouvelle-fonctionnalite`)
3. Committer vos changements (`git commit -m 'Ajout d'une nouvelle fonctionnalité'`)
4. Pusher vers la branche (`git push origin feature/nouvelle-fonctionnalite`)
5. Ouvrir une Pull Request

## 📄 Licence

Ce projet est distribué sous licence MIT. Voir le fichier `LICENSE` pour plus d'informations.

## 📧 Contact

Pour toute question, suggestion ou rapport de bug, veuillez contacter :
- Email : hamdi.abdallah@polytechnicien.tn
- GitHub : (https://github.com/Hamdiabdall/Ml-Project-.git)

### Remerciements

Ce projet s'appuie sur les données ouvertes fournies par ODRE (OpenData Réseaux Énergies) qui met à disposition les données de consommation énergétique française. Nos remerciements vont à tous les acteurs qui contribuent à la transparence des données énergétiques.

---

Développé dans le cadre du projet "Analyse et modélisation dynamique de la consommation électrique et de gaz des Français" - 2025
