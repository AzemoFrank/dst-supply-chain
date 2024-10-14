# dst-supply-chain

---
<style>
hr {
    border-width:2px;
    border-color:#75DFC1;
}
</style>
---

<center> <h1> Projet - Supply Chain </h1> </center>
<center> <h2> Étape : Scrape les données à partir du site : fr.trustpilot.com </h2></center>

---

# Informations explicatives

## Catégorie ciblée : Services aux entreprises
## Sous catégorie ciblée : Transport et logistique

Avec cette URL [https://fr.trustpilot.com/categories/business_services](https://fr.trustpilot.com/categories/business_services), on doit scraper les informations nécessaires.

Deux DataFrames vont être générés :

1. `df_Entreprise.csv` contient les informations suivantes pour chaque entreprise :
   - Nom de l'entreprise
   - url de l'entreprise
   - Location/Lieu
   - Trust score
   - Nombre d'avis
   - Services proposés (liste)

2. `Df_avis.csv` : contient les informations suivantes pour chaque entreprise :
   - Nom de l'entreprise
   - Nom de l'utilisateur (s'il existe)
   - La date de l'avis
   - La note donnée
   - Commentaire_client
   - Réponse de l'entreprise
   - source de l'avis