# Noche Duo 🌙

Le jeu des amoureux, même à distance. En français, créole et anglais.

**Jouer :** https://payasec.github.io/Noche-duo/

- Jeux : Mission Secrète, Synchro, Tu me connais ?, Dessine et devine, Défi du jour
- Messages privés : texte, emojis, photos, messages vocaux, réponses, réactions, ✓✓ lu, « écrit… », appels manqués avec Rappeler
- Gros câlin avec votre photo ou vos visages, toucher à distance, Notre jardin, compte à rebours des retrouvailles
- Couple en ligne : Pensée, Bonne nuit, humeur, météo de nos deux villes, écouter ensemble, activité « Pendant ton absence »
- Appels vocaux et vidéo plein écran dans l'appli
- Souvenirs : lettres programmées, liste de rêves, notre histoire, carte du mois
- Progression : Flamme, niveaux, badges
- Appli installable, code PIN, économie de données, lien d'invitation

## Documentation

- [Guide d'utilisation](docs/GUIDE.md)
- [Architecture et modèle de données](docs/ARCHITECTURE.md)
- [Journal des versions](CHANGELOG.md)
- [Politique de confidentialité](https://payasec.github.io/Noche-duo/privacy.html)

## Tests

Huit scénarios à deux téléphones simulés (chat, médias, appels, câlin, visages, jardin, activité, accueil) :

```
pip install playwright && playwright install chromium
./tests/run_all.sh
```

Chaque scénario doit afficher « OK ».
