# 🎨 Guide Visuel - Interface Argus

Ce document décrit l'interface utilisateur du système Argus.

---

## 🏠 Page d'Accueil (Détection en Direct)

```
┌─────────────────────────────────────────────────────────────┐
│  🎥 Argus Security                                          │
│  [Détection en Direct] [Historique] [Statistiques] [...]   │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│  🎥 Détection en Temps Réel                                 │
│                                                              │
│  ┌───────────────────────────────────────────────────────┐  │
│  │                                                        │  │
│  │                  [Flux Vidéo en Direct]                │  │
│  │                                                        │  │
│  │  Heure: 2025-10-15 14:30:45                          │  │
│  │  MOUVEMENT DETECTE                                    │  │
│  │  Intensité: 0.75                                      │  │
│  │  Visages: 2                                           │  │
│  │                                                        │  │
│  └───────────────────────────────────────────────────────┘  │
│                                                              │
│  [▶️ Démarrer la Détection]                                 │
│                                                              │
│  ☐ Détection de mouvement    ☑ Détection de visages        │
│                                                              │
└─────────────────────────────────────────────────────────────┘

┌──────────────┬──────────────┬──────────────┬──────────────┐
│ État Système │  Mouvement   │   Visages    │  Intensité   │
│    ●Actif    │   ✅ Oui     │      2       │     75%      │
└──────────────┴──────────────┴──────────────┴──────────────┘

┌─────────────────────────────────────────────────────────────┐
│  📋 Derniers Événements                                     │
│  ┌───────────────────────────────────────────────────────┐  │
│  │ Type │ Heure │ Visages │ Intensité │                  │  │
│  │ Mvt  │ 14:30 │    0    │   65%     │                  │  │
│  │ Face │ 14:29 │    1    │   20%     │                  │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

---

## 📋 Page Historique

```
┌─────────────────────────────────────────────────────────────┐
│  📊 Historique des Détections                                │
│                                                              │
│  Filtres: [Tous les types ▼]  [Filtrer]                    │
│                                                              │
│  ┌──┬────────────┬────────────────┬────────┬──────┬──────┐ │
│  │ID│    Type    │  Date & Heure  │Visages │Inten.│Image │ │
│  ├──┼────────────┼────────────────┼────────┼──────┼──────┤ │
│  │45│ Mouvement  │ 15/10 14:30:00 │   0    │ 0.75 │ Voir │ │
│  │44│   Visage   │ 15/10 14:29:30 │   1    │ 0.20 │ Voir │ │
│  │43│    Les 2   │ 15/10 14:29:00 │   2    │ 0.85 │ Voir │ │
│  │42│ Mouvement  │ 15/10 14:28:30 │   0    │ 0.65 │ Voir │ │
│  └──┴────────────┴────────────────┴────────┴──────┴──────┘ │
│                                                              │
│  [◀ Première] [◀ Préc] [Page 1/5] [Suiv ▶] [Dernière ▶]   │
└─────────────────────────────────────────────────────────────┘
```

---

## 📊 Page Statistiques

```
┌─────────────────────────────────────────────────────────────┐
│  📊 Statistiques de Détection                                │
│                                                              │
│  ┌──────────────┬──────────────┬──────────────────────────┐ │
│  │    Total     │  Mouvements  │       Visages            │ │
│  │     150      │      85      │         45               │ │
│  └──────────────┴──────────────┴──────────────────────────┘ │
│                                                              │
│  ┌──────────────┬──────────────┬──────────────────────────┐ │
│  │  Les Deux    │ Dernières 24h│    Moy. Visages          │ │
│  │     20       │      35      │        1.5               │ │
│  └──────────────┴──────────────┴──────────────────────────┘ │
│                                                              │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│  📈 Répartition des Détections                               │
│                                                              │
│     Mouvements        Visages         Les Deux              │
│       ╭───╮           ╭───╮            ╭───╮               │
│       │57%│           │30%│            │13%│               │
│       ╰───╯           ╰───╯            ╰───╯               │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## ⚙️ Page Paramètres

```
┌─────────────────────────────────────────────────────────────┐
│  ⚙️ Paramètres de Détection                                  │
│                                                              │
│  Nom de la Configuration                                     │
│  [Default___________________]                                │
│                                                              │
│  Index de la Caméra                                          │
│  [0▼]  (0 = caméra par défaut, 1 = deuxième...)            │
│                                                              │
│  ☑ Activer la détection de mouvement                        │
│  ☑ Activer la détection de visages                          │
│                                                              │
│  Seuil de Mouvement                                          │
│  Sensible ◄─────●─────────────► Moins sensible             │
│            5        25        50                             │
│                                                              │
│  Surface Minimale du Contour                                 │
│  [500______]  (ignorer mouvements < valeur)                 │
│                                                              │
│  ☑ Sauvegarder les images lors des détections               │
│                                                              │
│  Intervalle de Détection (secondes)                          │
│  [1____]  (temps minimum entre 2 enregistrements)           │
│                                                              │
│  [💾 Sauvegarder]  [↩️ Retour]                              │
│                                                              │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│  ℹ️ Informations                                             │
│  • Détection de mouvement: Différence entre frames          │
│  • Détection de visages: Haar Cascade (100% local)          │
│  • Seuil bas = plus sensible                                │
│  • Surface minimale = filtre le bruit                        │
└─────────────────────────────────────────────────────────────┘
```

---

## 🎨 Palette de Couleurs

### Couleurs Principales

- **Primaire (Violet)**: `#667eea` → `#764ba2`
- **Succès (Vert)**: `#48bb78` → `#38a169`
- **Danger (Rouge)**: `#f56565` → `#e53e3e`
- **Info (Bleu)**: `#4299e1` → `#3182ce`

### Dégradés Utilisés

```
Violet:  #667eea → #764ba2  (Header, cartes principales)
Rose:    #f093fb → #f5576c  (Statistiques mouvement)
Bleu:    #4facfe → #00f2fe  (Statistiques visages)
Vert:    #43e97b → #38f9d7  (Statistiques combinées)
Orange:  #fa709a → #fee140  (Dernières 24h)
Indigo:  #30cfd0 → #330867  (Moyenne)
```

---

## 🖼️ Éléments Visuels

### Boutons

```
Primary:    [▶️ Démarrer]  (Violet avec hover)
Danger:     [⏹️ Arrêter]   (Rouge avec hover)
Success:    [💾 Sauvegarder] (Vert avec hover)
```

### Cartes (Cards)

```
┌─────────────────────────────┐
│  Titre                      │
│                             │
│  Contenu avec ombre         │
│  et coins arrondis          │
│                             │
└─────────────────────────────┘
```

### Indicateurs de Statut

```
● Actif    (Vert lumineux avec effet de pulsation)
● Inactif  (Gris)
```

### Barres de Progression / Sliders

```
Sensible ◄═════●══════════════► Moins sensible
         5      25            50
```

---

## 📱 Responsive Design

### Desktop (> 768px)

- Navigation horizontale
- Grilles multi-colonnes
- Vidéo large format

### Mobile (< 768px)

- Navigation verticale (menu hamburger)
- Grilles en une colonne
- Vidéo pleine largeur

---

## 🎯 Interactions Utilisateur

### Actions Principales

1. **Démarrer** : Clic → Animation → Changement de bouton
2. **Arrêter** : Clic → Confirmation → Reset des statuts
3. **Toggle détection** : Switch instantané sans rechargement
4. **Sauvegarder param** : Animation de succès + message

### Feedback Visuel

- ✅ Alertes vertes pour succès
- ❌ Alertes rouges pour erreurs
- ℹ️ Alertes bleues pour informations
- 🔄 Animations de chargement

---

## 🎬 Animations

### Transitions

```css
transition: all 0.3s ease; /* Boutons, cartes */
transition: opacity 0.5s; /* Fade in/out */
transform: translateY(-2px); /* Hover lift */
```

### Effets

- **Hover sur boutons** : Élévation + ombre
- **Indicateur actif** : Pulsation (box-shadow)
- **Chargement** : Rotation ou points animés
- **Apparition alertes** : Slide down + fade in

---

## 📐 Espacements et Tailles

### Padding Standards

- Cartes : `2rem` (32px)
- Boutons : `0.75rem 1.5rem` (12px 24px)
- Containers : `0 2rem` (0 32px)

### Gaps et Marges

- Entre cartes : `2rem`
- Entre éléments de grille : `1.5rem`
- Entre lignes de tableau : `1px border`

### Tailles de Police

- H1 (Logo) : `1.8rem` (28.8px)
- H2 (Titres pages) : `1.5rem` (24px)
- H3 (Sous-titres) : `1rem` (16px)
- Corps : `1rem` (16px)
- Petit : `0.875rem` (14px)

---

## 🖱️ États des Éléments

### Boutons

- **Normal** : Couleur de base
- **Hover** : Transformation + ombre accrue
- **Active** : Légère compression
- **Disabled** : Opacité 50% + cursor not-allowed

### Inputs

- **Normal** : Border grise claire
- **Focus** : Border colorée + outline
- **Error** : Border rouge
- **Success** : Border verte

### Checkboxes

- **Unchecked** : Gris clair
- **Checked** : Vert avec animation
- **Hover** : Légère élévation

---

## 🎪 Composants Réutilisables

### Alert Box

```html
<div class="alert alert-success">✅ Opération réussie !</div>

<div class="alert alert-danger">❌ Erreur lors de l'opération</div>

<div class="alert alert-info">ℹ️ Information importante</div>
```

### Status Card

```html
<div class="status-card">
  <h3>Titre</h3>
  <div class="value">42</div>
</div>
```

### Toggle Switch

```html
<label class="switch">
  <input type="checkbox" />
  <span class="slider"></span>
</label>
```

---

## 🌈 Thème Sombre (Futur)

Préparation pour un thème sombre optionnel :

```css
:root {
  /* Thème clair */
  --bg-primary: #ffffff;
  --text-primary: #333333;
  --card-bg: #ffffff;
}

[data-theme="dark"] {
  /* Thème sombre */
  --bg-primary: #1a1a1a;
  --text-primary: #e0e0e0;
  --card-bg: #2d2d2d;
}
```

---

## 📸 Captures d'Écran Suggérées

Pour la documentation complète, voici les captures recommandées :

1. **Page d'accueil** avec détection active
2. **Flux vidéo** avec rectangles de détection
3. **Historique** avec plusieurs événements
4. **Statistiques** avec graphiques colorés
5. **Paramètres** montrant toutes les options
6. **Admin Django** (optionnel)

---

## 🎨 Personnalisation

### Changer les Couleurs Principales

Dans `base.html`, modifier les dégradés :

```css
/* Ancien */
background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);

/* Nouveau (exemple bleu) */
background: linear-gradient(135deg, #4299e1 0%, #2c5282 100%);
```

### Changer les Polices

```css
font-family: "Roboto", sans-serif; /* Remplacer Segoe UI */
```

### Ajouter des Icônes

Utiliser une bibliothèque comme Font Awesome :

```html
<link
  rel="stylesheet"
  href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css"
/>

<!-- Utilisation -->
<i class="fas fa-camera"></i>
<i class="fas fa-chart-bar"></i>
```

---

Votre interface est maintenant bien documentée ! 🎨✨
