# Exercice 3 - Preparation Alloy, OTLP et application Flask

## Objectif

Cet exercice correspond a une preparation autour d'Alloy, d'OpenTelemetry et d'une application Flask instrumentee pour envoyer des signaux OTLP.

L'idee etait de poser une base de travail simple avec :

- un recepteur OTLP dans Alloy
- une application Flask instrumentee
- des manifestes Kubernetes minimaux pour deployer l'application

## Etat d'avancement

J'ai prepare les fichiers necessaires pour demarrer l'exercice, mais je ne suis pas alle au bout de toute la mise en oeuvre.

Point important pour la relecture :

- la partie 3 de l'exercice a ete realisee avec l'aide d'une IA
- je trouve cette partie encore trop compliquee a faire seul pour le moment
- je prefere donc m'arreter a cette etape, puis mieux comprendre le contexte et la technologie avant d'aller plus loin

Je laisse donc ici une base de travail documentee plutot que de pretendre maitriser completement une mise en place que je ne comprends pas encore assez bien.

## Fichiers presents

- `config.alloy` : recepteur OTLP Alloy avec export `debug`
- `values-alloy.yaml` : valeurs Helm minimales pour exposer Alloy
- `exercice-3/app.py` : petite application Flask de demonstration
- `exercice-3/requirements.txt` : dependances Python et instrumentation OpenTelemetry
- `exercice-3/Dockerfile` : image de l'application instrumentee
- `exercice-3/demo-configmap.yaml` : variables d'environnement OpenTelemetry
- `exercice-3/demo-deployment.yaml` : deploiement Kubernetes
- `exercice-3/demo-service.yaml` : service Kubernetes

## Ce qui a ete prepare

### 1. Application de demonstration

L'application Flask expose :

- `/` : reponse JSON simple avec une latence simulee
- `/health` : endpoint de sante

Elle utilise `opentelemetry-instrument` au lancement pour emettre traces, logs et metriques via OTLP.

### 2. Reception OTLP dans Alloy

Le fichier `config.alloy` ouvre :

- le port `4317` pour OTLP gRPC
- le port `4318` pour OTLP HTTP

Les signaux recus sont ensuite rediriges vers un exporter `debug` pour verifier la reception.

### 3. Base Kubernetes

Les manifestes fournis permettent de preparer :

- la configuration OpenTelemetry de l'application
- le deploiement du conteneur Flask
- l'exposition du service dans le cluster

## Limite actuelle

Le dossier represente une preparation technique et un point d'arret assume. Il ne faut pas le lire comme un exercice totalement finalise.

Mon objectif pour la suite serait d'abord de mieux comprendre :

- le role exact d'Alloy dans la chaine
- le fonctionnement OTLP
- la logique d'instrumentation et d'export des signaux

Ensuite seulement, je pourrais reprendre l'exercice de maniere plus autonome.
