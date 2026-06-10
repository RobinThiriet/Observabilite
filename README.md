# Observabilite

Depot unique de rendu pour la matiere d'observabilite.

Ce repository regroupe mes exercices realises sur le module. L'objectif est de centraliser le travail dans un seul endroit propre, lisible et facile a evaluer, plutot que de conserver plusieurs depots separes.

## Organisation du depot

Le depot est decoupe par exercice pour que chaque sujet puisse etre relu independamment :

- [`exercices/exercice-01-prometheus/`](exercices/exercice-01-prometheus/README.md) : stack de monitoring autour de Prometheus, Alertmanager, `node_exporter` et une API Flask instrumentee
- [`exercices/exercice-02-loki-alloy-grafana/`](exercices/exercice-02-loki-alloy-grafana/README.md) : stack de logs avec Loki, Grafana et Alloy, incluant un pipeline de traitement de logs JSON
- [`exercices/exercice-03-a-preparer/`](exercices/exercice-03-a-preparer/README.md) : espace reserve pour le 3e et dernier exercice

## Avancement

- Exercice 1 : termine et documente
- Exercice 2 : termine et documente
- Exercice 3 : dossier prepare pour continuer le travail

## Lecture conseillee

Pour une evaluation rapide, l'ordre recommande est :

1. lire ce `README.md`
2. ouvrir le README de `exercices/exercice-01-prometheus/`
3. ouvrir le README de `exercices/exercice-02-loki-alloy-grafana/`
4. consulter les fichiers de configuration et les captures associees

## Lancer les exercices

Chaque exercice est autonome et se lance depuis son propre dossier.

### Exercice 1

```bash
cd exercices/exercice-01-prometheus
docker compose up --build
```

### Exercice 2

```bash
cd exercices/exercice-02-loki-alloy-grafana
docker compose up -d
```

## Remarques

- J'ai volontairement conserve les exercices dans des dossiers distincts pour separer les stacks, les objectifs et les fichiers de configuration.
- Les captures et documents fournis dans les exercices ont ete laisses au plus pres de leur sujet pour faciliter la relecture.
- Le dossier de l'exercice 3 est deja cree afin de pouvoir continuer le travail dans le meme depot sans casser l'organisation mise en place.
