# Noche Duo — Architecture

Version 28 · novembre 2026

## Vue d'ensemble

Noche Duo est une application web installable (PWA), hébergée sur GitHub Pages, qui synchronise deux téléphones par Firebase Realtime Database. Il n'y a pas de serveur à nous : tout tourne dans le navigateur, et Firebase sert de base de données temps réel et d'authentification.

| Élément | Rôle |
| --- | --- |
| `index.html` | Toute l'application : HTML, CSS et JavaScript dans un seul fichier |
| `sw.js` | Service worker : réseau d'abord pour la page, cache d'abord pour les fichiers ; le nom du cache change à chaque version |
| `manifest.webmanifest`, icônes | Installation sur l'écran d'accueil |
| `database.rules.json` | Règles de sécurité Firebase, à recopier dans la console |
| `privacy.html`, `delete.html` | Pages exigées par Google Play |
| `android/` | Coque Android (Trusted Web Activity) pour le Play Store, sans la clé de signature |
| `tests/` | Scénarios automatiques à deux téléphones simulés |

## Organisation de `index.html`

Le script est une seule fonction auto-exécutée. Les modules se suivent dans cet ordre :

1. Données fixes : missions, humeurs, défis, niveaux, badges, textes en 3 langues (`T.fr`, `T.kr`, `T.en`, lus par `t(clé)` ; les éléments `data-i` sont remplis par `applyText()`).
2. État : `S` (partie) et `P` (profil), sauvegardés dans `localStorage` (`nd-state`, `nd-profile`).
3. Jeux : Mission Secrète, Synchro, Tu me connais, Dessine et devine.
4. En ligne (`OL`) : connexion anonyme, lien du couple, présence, écoute des données (`olAttach`).
5. Appels (`CALL`) : WebRTC, signalisation par Firebase, écran d'appel plein écran.
6. Lettres, rêves, météo (Open-Meteo), musique (YouTube).
7. Navigation : onglets, bouton retour du téléphone (`popstate`), en-tête.
8. Chat (`CH`) : messages, réponses, réactions, emojis, photos, vocaux.
9. Médias du chat (`MEDIA`) : stockage à part, chargement à la demande, cache IndexedDB.
10. Activité (`FEED`) : cloche, « Pendant ton absence ».
11. Visages, câlin, jardin, toucher à distance, retrouvailles, invitation.
12. Démarrage : chargement de l'état, écran d'accueil, verrou PIN, accueil des nouveaux.

## Modèle de données (Firebase Realtime Database)

| Chemin | Contenu |
| --- | --- |
| `couples/{code}/members/{a\|b}` | Identifiant Firebase de chaque membre |
| `couples/{code}/live/{a\|b}` | État de chaque personne : en ligne, humeur, pensée, bonne nuit, écrit, lu, toucher, météo, lettres, dessin |
| `couples/{code}/live/shared` | Partagé : manche, dates, photo du couple, photo câlin, visages, jardin, rêves, musique |
| `couples/{code}/live/chat/{clé}` | Messages : `from`, `at`, puis `t` (texte) ou `mid`+`mk` (média) ou `hug` ou `call`, avec `re` (réponse) et `rx` (réactions) |
| `couples/{code}/live/media/{id}` | Photo ou vocal d'un message : `d` (données), `k` (`img` ou `aud`) |
| `couples/{code}/live/feed/{clé}` | Activité : `from`, `type`, `at`, `x` ; purgée après 60 jours |
| `couples/{code}/live/call`, `callIce` | Signalisation des appels |
| `users/{uid}` | Sauvegarde du profil (compte Google) |
| `stats/days/{jour}/{uid}`, `stats/couples/{code}` | Statistiques anonymes |

Les clés de messages commencent par `m` suivi de l'heure du serveur sur 14 chiffres : l'ordre alphabétique est l'ordre chronologique. Les anciens messages avec la photo ou le vocal intégrés (`img`, `aud`) restent affichés.

## Sécurité

- Seuls les deux membres d'un couple peuvent lire et écrire ses données ; la lecture sans compte est refusée (vérifié le 14 novembre 2026).
- Les règles limitent la taille des textes, photos, vocaux et entrées d'activité.
- Le code PIN protège l'écran du téléphone, pas les données.
- Points ouverts : App Check, vérification du champ `from`.

## Limites du plan Firebase gratuit

1 Go stocké, 10 Go téléchargés par mois, 100 connexions simultanées. Passer au plan Blaze avant d'avoir beaucoup d'utilisateurs.

## Mettre à jour l'application

1. Modifier `index.html`.
2. Augmenter la version dans `index.html` (« version N ») et le nom du cache dans `sw.js`.
3. Lancer `tests/run_all.sh` : tout doit être « OK ».
4. Publier sur la branche `main` ; GitHub Pages met le site à jour en une minute environ.
5. Si `database.rules.json` a changé, le recopier dans la console Firebase.
