# Exercice 2 - Loki, Alloy et Grafana

## Objectif

Cet exercice correspond a la partie logs de mon travail. Le but etait de mettre en place une stack locale capable de collecter, traiter et visualiser des logs avec l'ecosysteme Grafana.

L'exercice a eu deux etapes importantes :

- une premiere version qui collectait directement les logs Docker
- une version plus avancee, qui traite des logs JSON ecrits dans un fichier puis enrichis par Alloy avant envoi vers Loki

Le README ci-dessous decrit l'etat actuel du projet tout en conservant la trace de cette progression.

## Stack mise en place

- `loki` : recoit et stocke les logs
- `grafana` : permet d'interroger Loki et d'explorer les logs
- `alloy` : collecte les logs et applique les transformations
- `app` : conteneur de demonstration qui ecrit des logs JSON dans un volume partage

## Fichiers importants

- `docker-compose.yml` : definition de la stack
- `config.alloy` : pipeline de collecte et de traitement
- `grafana/provisioning/datasources/datasource.yml` : declaration automatique de Loki dans Grafana
- `doc/grafana_loki_docker.docx` : document du TP

## Demarrage

```bash
docker compose up -d
```

Services accessibles :

- Grafana : `http://localhost:3000`
- Loki : `http://localhost:3100`
- Alloy : `http://localhost:12345`

Identifiants Grafana par defaut :

- utilisateur : `admin`
- mot de passe : `admin`

## Ce que j'avais fait au depart

La premiere version du projet reposait sur la collecte de logs Docker directement depuis le socket Docker.

Le pipeline initial fonctionnait ainsi :

1. `discovery.docker` detectait les conteneurs
2. `loki.source.docker` lisait leurs logs
3. un `stage.regex` extrayait le niveau de log
4. un `stage.labels` ajoutait `loglevel`
5. un `stage.static_labels` ajoutait `environment=development`
6. un `loki.relabel` supprimait des labels techniques comme `container_id` et `filename`
7. Alloy envoyait le tout vers Loki

Cette version etait documentee dans le README d'origine du depot `loki-alloy-grafana`.

## Evolution vers la version actuelle

J'ai ensuite fait evoluer l'exercice vers un pipeline plus interessant pedagogiquement, base sur des logs JSON.

### 1. Passage d'une source Docker a une source fichier

Au lieu de lire les logs via le socket Docker, Alloy suit maintenant les fichiers `*.log` du dossier `/var/log/apps`.

Dans `config.alloy` :

```hcl
local.file_match "json_app_logs" {
  path_targets = [
    {
      __path__    = "/var/log/apps/*.log",
      job         = "json-processing-test",
      app         = "json-app",
      environment = "development",
    },
  ]
}

loki.source.file "json_app_logs" {
  targets    = local.file_match.json_app_logs.targets
  forward_to = [loki.process.json_pipeline.receiver]
}
```

Cette approche permet de travailler un cas frequent : des applications qui produisent des logs structures dans des fichiers.

### 2. Traitement de logs JSON dans Alloy

Le coeur de l'exercice est dans `loki.process "json_pipeline"`.

J'y ai defini trois etapes :

1. `stage.json` pour extraire `level`, `user_id` et `message`
2. `stage.drop` pour supprimer les logs de niveau `debug`
3. `stage.labels` pour promouvoir `user_id` en label Loki

Configuration :

```hcl
loki.process "json_pipeline" {
  forward_to = [loki.write.local.receiver]

  stage.json {
    expressions = {
      level   = "level",
      user_id = "user_id",
      message = "message",
    }
  }

  stage.drop {
    source = "level"
    value  = "debug"
  }

  stage.labels {
    values = {
      user_id = "user_id",
    }
  }
}
```

Cela montre que je n'ai pas seulement envoye des logs bruts vers Loki : j'ai mis en place un petit pipeline de parsing et de filtrage.

### 3. Ajout d'un generateur de logs JSON

Le service `app` ecrit en boucle des lignes JSON dans `/var/log/apps/app.log`.

Exemples de logs produits :

- un log `info` pour un login reussi
- un log `debug` volontairement present pour tester le filtrage
- un log `error` pour simuler un echec de paiement

Le conteneur partage un volume `app-logs` avec Alloy, ce qui permet a Alloy de lire le fichier en continu.

Extrait du `docker-compose.yml` :

```yaml
app:
  image: busybox
  container_name: app
  volumes:
    - app-logs:/var/log/apps
```

Et Alloy dispose egalement :

- du volume `app-logs` pour lire les fichiers
- du volume `alloy-data` pour son stockage local

### 4. Provisioning automatique de Grafana

Grafana est preconfigure avec Loki comme source de donnees grace a :

```yaml
datasources:
  - name: Loki
    type: loki
    access: proxy
    url: http://loki:3100
    isDefault: true
```

L'interet est simple : une fois la stack lancee, je peux aller directement dans `Explore` sans avoir a configurer la source a la main.

## Pipeline final

Dans sa version actuelle, le flux complet est le suivant :

1. le conteneur `app` ecrit des logs JSON dans `app.log`
2. Alloy detecte ce fichier via `local.file_match`
3. Alloy lit les lignes avec `loki.source.file`
4. Alloy parse le JSON
5. Alloy ignore les lignes `debug`
6. Alloy ajoute `user_id` comme label
7. Alloy pousse les logs vers Loki
8. Grafana interroge Loki pour afficher et filtrer les logs

## Ce que cet exercice montre

Cet exercice montre plusieurs choses :

- mise en place d'une stack Loki / Grafana / Alloy complete
- collecte de logs sans configuration manuelle dans Grafana
- transformation de logs dans Alloy
- filtrage par contenu avant ingestion
- enrichment des logs avec des labels utiles pour les requetes

## Verifications utiles

Verifier les conteneurs :

```bash
docker compose ps
```

Verifier les logs du generateur :

```bash
docker logs app
```

Verifier Alloy :

```bash
docker logs alloy
```

## Requetes LogQL utiles

Afficher tous les logs de ce pipeline :

```logql
{job="json-processing-test"}
```

Filtrer par utilisateur :

```logql
{job="json-processing-test", user_id="user-3"}
```

Afficher les lignes contenant une erreur :

```logql
{job="json-processing-test"} |= "error"
```

## Conclusion

Par rapport a une simple demo d'ingestion, cet exercice montre que j'ai travaille la chaine complete des logs :

- generation
- collecte
- parsing
- filtrage
- labellisation
- visualisation dans Grafana

Il s'agit donc d'un exercice de centralisation de logs, mais aussi d'un premier travail de traitement de logs structures avec Alloy.
