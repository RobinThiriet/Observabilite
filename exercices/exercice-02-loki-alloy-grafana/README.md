# Exercice 2 - Loki, Alloy et Grafana

## Objectif

Cet exercice porte sur la centralisation et le traitement de logs avec la stack Grafana. Le but etait de faire collecter des logs par Alloy, de les envoyer vers Loki, puis de les exploiter dans Grafana.

Dans l'etat actuel du travail, le pipeline est base sur des logs JSON ecrits dans un fichier partage par un conteneur applicatif de demonstration.

## Contenu de la stack

- `loki` : stockage et interrogation des logs
- `grafana` : visualisation des logs et exploration via Loki
- `alloy` : collecte et traitement des logs
- `app` : conteneur de test qui ecrit des logs JSON dans un volume partage

## Fichiers principaux

- `docker-compose.yml` : definition de la stack
- `config.alloy` : pipeline de collecte et de transformation des logs
- `grafana/provisioning/datasources/datasource.yml` : source de donnees Loki preconfiguree
- `doc/grafana_loki_docker.docx` : document associe a l'exercice

## Demarrage

```bash
docker compose up -d
```

## Services exposes

- Grafana : `http://localhost:3000`
- Loki : `http://localhost:3100`
- Alloy : `http://localhost:12345`

Identifiants Grafana par defaut :

- utilisateur : `admin`
- mot de passe : `admin`

## Fonctionnement du pipeline

Le flux de logs est le suivant :

1. le conteneur `app` ecrit des logs JSON dans `/var/log/apps/app.log`
2. Alloy lit ce fichier via `loki.source.file`
3. le stage `json` extrait plusieurs champs utiles
4. le stage `drop` elimine les lignes de niveau `debug`
5. le stage `labels` promeut `user_id` en label Loki
6. Alloy envoie le resultat vers Loki
7. Grafana interroge Loki pour visualiser les logs

## Ce qui a ete mis en place

### 1. Stack Loki/Grafana

Le compose lance une stack minimale mais complete pour tester localement la collecte et l'exploration de logs.

### 2. Source Grafana preconfiguree

Grafana charge automatiquement Loki comme source de donnees, ce qui permet d'utiliser directement `Explore` sans configuration manuelle supplementaire.

### 3. Collecte de logs par fichier

Dans `config.alloy`, j'utilise `local.file_match` et `loki.source.file` pour suivre les fichiers `*.log` du dossier `/var/log/apps`.

### 4. Traitement de logs JSON

Le pipeline Alloy extrait :

- `level`
- `user_id`
- `message`

Ensuite :

- les logs `debug` sont exclus
- `user_id` est ajoute comme label pour faciliter le filtrage dans Loki

### 5. Generation de logs de test

Le conteneur `app` produit en boucle :

- des logs `info`
- des logs `debug`
- des logs `error`

Cela permet de verifier facilement :

- l'ingestion dans Loki
- le filtrage des logs `debug`
- l'ajout du label `user_id`

## Verifications utiles

Verifier les conteneurs :

```bash
docker compose ps
```

Verifier les logs du conteneur de test :

```bash
docker logs app
```

Verifier Alloy :

```bash
docker logs alloy
```

## Requetes LogQL utiles

Tous les logs du job :

```logql
{job="json-processing-test"}
```

Filtrer par utilisateur :

```logql
{job="json-processing-test", user_id="user-3"}
```

Observer uniquement les erreurs :

```logql
{job="json-processing-test"} |= "error"
```

## Resultat attendu

Une fois la stack lancee, Grafana doit permettre d'observer les logs non `debug` collectes par Alloy, stockes dans Loki et filtrables par `user_id`.
