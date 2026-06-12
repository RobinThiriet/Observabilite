# Exercice 1 - Prometheus, Alertmanager et API instrumentee

## Objectif

Cet exercice correspond a la partie Prometheus du TP. Mon but etait de construire progressivement une petite stack locale d'observabilite, puis d'aller au-dela du simple demarrage en travaillant la decouverte de cibles, l'instrumentation applicative, les recording rules et les alertes.

Le resultat final de cet exercice repose sur quatre briques :

- `prometheus` pour collecter et interroger les metriques
- `node_exporter` pour exposer des metriques systeme
- `alertmanager` pour recevoir les alertes de Prometheus
- `demo-api` pour disposer d'une application Flask instrumentee et produire des metriques metier et techniques

## Fichiers importants

- `docker-compose.yml` : definition des services
- `prometheus.yml` : configuration principale de Prometheus
- `targets.json` : cibles chargees dynamiquement via `file_sd_configs`
- `rules/api_rules.yml` : recording rules
- `alerts/api_alerts.yml` : regle d'alerte
- `alertmanager/alertmanager.yml` : configuration minimale d'Alertmanager
- `app.py` : API Flask instrumentee avec `prometheus_client`
- `traffic.sh` : script de generation de trafic
- `image/` : captures d'ecran du TP et verifications

## Demarrage

```bash
docker compose up --build
```

Services accessibles :

- Prometheus : `http://localhost:9090`
- Alertmanager : `http://localhost:9093`
- Demo API : `http://localhost:8000`

Pour generer du trafic sur l'API :

```bash
./traffic.sh
```

## Detail du travail realise

### Exercice 1 - Installation de Prometheus

J'ai commence par deployer un conteneur Prometheus expose sur le port `9090`.

Dans `docker-compose.yml`, cela correspond au service :

```yaml
prometheus:
  image: prom/prometheus:latest
  container_name: prometheus
  ports:
    - "9090:9090"
```

L'objectif etait de verifier que l'interface etait bien accessible et que la cible Prometheus etait joignable.

Capture utile :

- `image/Screenshot_3.png` montre l'interface `Status > Target health`

### Exercice 2 - Ecriture de `prometheus.yml`

J'ai ensuite ajoute la configuration principale de Prometheus avec :

- un `scrape_interval`
- un `external label`
- le support du rechargement sans redemarrage grace a `--web.enable-lifecycle`

Configuration mise en place :

```yaml
global:
  scrape_interval: 10s
  external_labels:
    environment: lab
```

Et dans `docker-compose.yml` :

```yaml
command:
  - "--config.file=/etc/prometheus/prometheus.yml"
  - "--web.enable-lifecycle"
```

Captures d'appui :

- `image/Screenshot_7.png` montre la documentation que j'ai utilisee comme reference de structure

### Exercice 3 - Ajout de `node_exporter`

J'ai ajoute un second exporteur pour exposer des metriques systeme.

Service ajoute :

```yaml
node:
  image: prom/node-exporter:latest
  container_name: node
  ports:
    - "9100:9100"
```

Cela m'a permis d'avoir plusieurs cibles dans Prometheus et de commencer a travailler la notion de `job` et `instance`.

Captures d'appui :

- `image/Screenshot_3.png` montre la cible `node:9100`
- `image/Screenshot_26.png` rappelle la notion de `job` et `instance`

### Exercice 4 - Service discovery par fichier

Au lieu de declarer les cibles en dur dans `prometheus.yml`, j'ai mis en place une decouverte via fichier avec `file_sd_configs`.

Dans `prometheus.yml` :

```yaml
scrape_configs:
  - job_name: "file-discovery"
    file_sd_configs:
      - files:
          - /etc/prometheus/sd/*.json
        refresh_interval: 5s
```

Dans `targets.json` :

```json
[
  {
    "targets": ["prometheus:9090"],
    "labels": {
      "service": "prometheus"
    }
  },
  {
    "targets": ["node:9100"],
    "labels": {
      "service": "node"
    }
  },
  {
    "targets": ["demo-api:8000"],
    "labels": {
      "service": "demo-api"
    }
  }
]
```

Cette partie est visible dans l'interface Prometheus avec trois endpoints `UP` et les labels associes.

Captures d'appui :

- `image/Screenshot_2.png` montre la documentation `file_sd_configs`
- `image/Screenshot_12.png` montre les trois targets `prometheus`, `node` et `demo-api` en `UP`
- `image/Screenshot_25.png` met en evidence les valeurs d'`instance`

### Exercice 5 - Instrumentation de l'application Flask

Pour disposer de vraies metriques applicatives, j'ai ajoute une petite API Flask dans `app.py`.

L'application expose :

- `/` pour un test simple
- `/api/users`
- `/api/orders`
- `/metrics`

Instrumentation ajoutee :

- `Counter` pour `demo_http_requests_total`
- `Histogram` pour `demo_http_request_duration_seconds`
- `Gauge` pour `demo_http_requests_in_flight`
- `Gauge` pour `demo_active_users`

Cela m'a permis de produire mes propres metriques, et pas seulement de collecter celles de Prometheus ou `node_exporter`.

### Exercice 6 - Recording rules

J'ai ensuite ajoute des recording rules pour precalculer des expressions PromQL et reutiliser plus facilement les resultats.

Chargement des fichiers de rules dans `prometheus.yml` :

```yaml
rule_files:
  - /etc/prometheus/rules/*.yml
  - /etc/prometheus/alerts/*.yml
```

Montages Docker associes :

```yaml
volumes:
  - ./rules:/etc/prometheus/rules
  - ./alerts:/etc/prometheus/alerts
```

Dans `rules/api_rules.yml`, j'ai defini plusieurs rules :

- `job:demo_http_requests:rate_5m`
- `demo_api:requests:rate_1m_by_endpoint`
- `demo_api:error_ratio:rate_1m_by_endpoint`
- `demo_api:requests:rate_1m_topk3_by_instance`
- `demo_api:orders_latency:p95_5m`
- `demo_api:requests:predict_1h_total`
- `demo_api:requests:predict_1h_by_endpoint`

Ce travail montre que je suis alle au-dela d'une simple requete ponctuelle :

- calcul de debit avec `rate`
- agregations avec `sum by`
- classement avec `topk`
- quantile d'histogramme avec `histogram_quantile`
- prediction avec `predict_linear`

Captures d'appui :

- `image/Screenshot_31.png` montre la documentation Prometheus sur les recording rules
- `image/Screenshot_21.png` montre l'exemple de `rate(...)`
- `image/Screenshot_22.png` et `image/Screenshot_23.png` montrent l'usage de `sum`
- `image/Screenshot_24.png` montre la documentation `topk`
- `image/Screenshot_20.png` montre un exemple de subquery utilisee comme support
- `image/Screenshot_27.png` montre les rules chargees et en etat `OK`

### Exercice 7 - Alertes et Alertmanager

J'ai mis en place une alerte simple basee sur le taux d'erreurs HTTP 5xx de l'API.

Regle definie dans `alerts/api_alerts.yml` :

```yaml
- alert: HighErrorRate
  expr: |
    sum(rate(demo_http_requests_total{status=~"5.."}[2m]))
    /
    sum(rate(demo_http_requests_total[2m]))
    > 0.05
  for: 2m
  labels:
    severity: warning
```

J'ai ensuite connecte Prometheus a Alertmanager :

```yaml
alerting:
  alertmanagers:
    - static_configs:
        - targets:
            - alertmanager:9093
```

Le fichier `alertmanager/alertmanager.yml` reste volontairement minimal, avec un receiver `default`, car l'objectif ici etait surtout de valider le chaînage Prometheus -> Alertmanager.

Captures d'appui :

- `image/Screenshot_8.png` montre la documentation Alertmanager consultee
- `image/Screenshot_10.png` montre la documentation des alerting rules
- `image/Screenshot_11.png` montre les rules et l'alerte chargees dans Prometheus
- `image/Screenshot_9.png` montre le detail de l'alerte `HighErrorRate`

### Exercice 8 - Requetes et agregations PromQL

J'ai travaille les agregations par endpoint et par instance, ce qui se voit dans les recording rules et les captures.

Ce que j'ai mis en pratique :

- `rate(...)` pour transformer un compteur en debit
- `sum by (endpoint)` pour agreger les requetes par endpoint
- `topk(3, ...)` pour faire ressortir les plus fortes valeurs

Cela correspond a une comprehension plus avancee de PromQL que la simple lecture d'une metrique brute.

### Exercice 9 - Latence p95 et prediction

J'ai egalement construit des rules plus avancees :

- calcul de la latence `p95` de `/api/orders` a partir de l'histogramme
- prediction du nombre de requetes a horizon 1 heure avec `predict_linear`

Exemple de requete pour la latence :

```promql
histogram_quantile(
  0.95,
  sum by (le, endpoint) (
    rate(demo_http_request_duration_seconds_bucket{endpoint="/api/orders"}[5m])
  )
)
```

Captures d'appui :

- `image/Screenshot_28.png` montre l'execution de la requete `histogram_quantile(...)`
- `image/Screenshot_29.png` montre la visualisation de `predict_linear(...)`
- `image/Screenshot_30.png` montre la documentation utilisee pour `predict_linear`

## Ce que cet exercice montre

Cet exercice ne se limite pas a lancer Prometheus. Il montre que j'ai :

- construit une stack locale multi-services
- configure une decouverte de cibles par fichier
- instrumente une application Python
- cree des recording rules utiles
- mis en place une alerte fonctionnelle
- travaille des requetes PromQL avancees

## Verification rapide

Une fois la stack demarree, on peut verifier :

- les targets dans `Status > Target health`
- les rules dans `Status > Rule health`
- l'alerte dans `Alerts`
- les metriques de l'API sur `http://localhost:8000/metrics`
