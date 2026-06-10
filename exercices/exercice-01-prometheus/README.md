# Exercice 1 - Prometheus, Alertmanager et API instrumentee

## Objectif

Cet exercice regroupe le travail realise autour de Prometheus sur une stack locale. L'idee etait de mettre en place une collecte de metriques, d'ajouter une application instrumentee, puis de progresser sur les notions de service discovery, recording rules et alerting.

## Contenu de la stack

- `prometheus` : collecte et interroge les metriques
- `node_exporter` : expose des metriques systeme
- `alertmanager` : recoit les alertes envoyees par Prometheus
- `demo-api` : application Flask instrumentee avec `prometheus_client`

## Fichiers principaux

- `docker-compose.yml` : definition de la stack locale
- `prometheus.yml` : configuration principale de Prometheus
- `targets.json` : cibles chargees via `file_sd_configs`
- `rules/api_rules.yml` : recording rules
- `alerts/api_alerts.yml` : regles d'alerte
- `alertmanager/alertmanager.yml` : configuration minimale d'Alertmanager
- `app.py` : API Flask instrumentee
- `traffic.sh` : script de generation de trafic
- `image/` : captures d'ecran et sujet du TP

## Demarrage

```bash
docker compose up --build
```

## Services exposes

- Prometheus : `http://localhost:9090`
- Alertmanager : `http://localhost:9093`
- Demo API : `http://localhost:8000`

Generation de trafic :

```bash
./traffic.sh
```

## Ce qui a ete mis en place

### 1. Mise en route de Prometheus

Le premier objectif etait d'exposer Prometheus localement puis de verifier que l'instance etait bien accessible.

### 2. Configuration principale

Dans `prometheus.yml`, j'ai defini :

- un `scrape_interval` global
- un `external label` pour identifier l'environnement
- le chargement des recording rules et des alertes
- l'integration avec Alertmanager

### 3. Ajout d'une cible supplementaire

`node_exporter` a ete ajoute pour exposer des metriques systeme et verifier le bon fonctionnement du scraping multi-cibles.

### 4. Service discovery par fichier

Au lieu de declarer les cibles en dur dans `prometheus.yml`, j'ai utilise `file_sd_configs` avec `targets.json`. Cela rend la configuration plus souple et plus proche d'un fonctionnement realiste.

### 5. Recording rules

Le fichier `rules/api_rules.yml` contient :

- une metrique pre-calculee de debit de requetes
- des agregations par endpoint
- un ratio d'erreurs HTTP
- un top 3 par instance
- des calculs de latence `p95`
- des predictions basees sur `predict_linear`

### 6. Alerting

Le fichier `alerts/api_alerts.yml` declare une alerte `HighErrorRate` envoyee a Alertmanager si le taux d'erreurs HTTP 5xx depasse 5 % pendant plus de 2 minutes.

### 7. Application instrumentee

L'application `app.py` expose :

- un endpoint `/metrics`
- des compteurs HTTP
- un histogramme de latence
- des gauges pour les requetes en cours et les utilisateurs actifs

Cela permet d'avoir une cible de test simple mais suffisante pour les exercices de Prometheus.

## Points d'attention

- Le compose de cet exercice expose Prometheus, Alertmanager, `node_exporter` et l'API de demo.
- Il n'y a pas de conteneur Grafana dans cet exercice dans son etat actuel.
- Les captures du dossier `image/` servent d'appui pour montrer les etapes du TP et les verifications effectuees.

## Captures et support

Le dossier `image/` contient :

- des captures d'ecran des differentes etapes
- le document du TP fourni

## Resultat attendu

Une fois la stack demarree, on peut :

- verifier les targets dans Prometheus
- generer du trafic sur l'API
- observer les metriques de l'application
- tester les recording rules
- verifier le chargement des alertes
