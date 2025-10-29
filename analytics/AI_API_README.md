# API IA et Système de Recommandations - Argus Analytics

## Vue d'ensemble

L'API IA d'Argus fournit des fonctionnalités avancées d'intelligence artificielle pour l'analyse des détections, incluant :

- 🤖 **Recommandations intelligentes** basées sur les patterns de détection
- 📊 **Insights IA** avec analyse prédictive
- 🔍 **Recherche intelligente** avec traitement du langage naturel (NLP)
- ⚠️ **Évaluation des risques** en temps réel
- 📈 **Prédictions d'activité** avec machine learning
- 🎯 **Suggestions d'optimisation** personnalisées

## Endpoints API

### 1. Recommandations Intelligentes

**Endpoint:** `GET /analytics/api/ai/recommendations/`

Génère des recommandations personnalisées basées sur l'analyse IA de vos données.

**Paramètres:**
- `days` (optionnel, défaut: 30) - Période d'analyse en jours
- `max_count` (optionnel, défaut: 10) - Nombre maximum de recommandations
- `min_confidence` (optionnel, défaut: 0.6) - Confiance minimale (0-1)
- `types` (optionnel) - Filtrer par types: `security,optimization,behavior,alert,monitoring`
- `actionable_only` (optionnel) - `true` pour recommandations actionnables uniquement

**Exemple de requête:**
```bash
curl -X GET "http://localhost:8000/analytics/api/ai/recommendations/?days=30&max_count=5&min_confidence=0.7" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Exemple de réponse:**
```json
{
  "status": "success",
  "data": {
    "recommendations": [
      {
        "type": "security",
        "priority": 5,
        "title": "Objets à risque détectés fréquemment",
        "description": "15 détections d'objets à risque dans les 100 dernières détections.",
        "action": "Envisager de renforcer la surveillance ou d'activer des alertes automatiques pour ces objets.",
        "impact": "high",
        "confidence": 0.95,
        "metadata": {
          "risky_count": 15,
          "suggested_actions": [
            "Configurer des alertes SMS pour objets dangereux",
            "Augmenter la fréquence de monitoring",
            "Revoir les zones de surveillance"
          ]
        }
      }
    ],
    "grouped": {
      "security": [...],
      "optimization": [...],
      "behavior": [...]
    },
    "statistics": {
      "total_recommendations": 8,
      "by_priority": {
        "5": 2,
        "4": 3,
        "3": 3
      },
      "by_type": {
        "security": 2,
        "optimization": 3,
        "behavior": 3
      },
      "average_confidence": 0.82
    }
  },
  "timestamp": "2025-10-29T10:30:00Z"
}
```

### 2. Insights IA

**Endpoint:** `GET /analytics/api/ai/insights/`

Génère des insights intelligents sur vos données de détection.

**Paramètres:**
- `days` (optionnel, défaut: 7) - Période d'analyse

**Exemple de requête:**
```bash
curl -X GET "http://localhost:8000/analytics/api/ai/insights/?days=7" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Exemple de réponse:**
```json
{
  "status": "success",
  "data": {
    "insights": [
      {
        "type": "anomaly",
        "title": "Anomalies détectées",
        "description": "8 anomalies identifiées par l'IA",
        "severity": "high",
        "data": {
          "anomaly_count": 8,
          "anomalies": [...]
        }
      },
      {
        "type": "trend",
        "title": "Objet le plus détecté",
        "description": "person avec 45 détections",
        "severity": "info",
        "data": {
          "object_class": "person",
          "count": 45,
          "is_anomaly": false
        }
      }
    ],
    "summary": {
      "total_insights": 5,
      "period_days": 7,
      "categories": {
        "anomalies": 2,
        "trends": 2,
        "alerts": 1
      }
    }
  }
}
```

### 3. Dashboard IA - Résumé Complet

**Endpoint:** `GET /analytics/api/ai/dashboard/`

Fournit un résumé complet pour le dashboard avec recommandations, métriques et score de santé.

**Exemple de requête:**
```bash
curl -X GET "http://localhost:8000/analytics/api/ai/dashboard/" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Exemple de réponse:**
```json
{
  "status": "success",
  "data": {
    "health": {
      "score": 85,
      "status": "excellent",
      "label": "Excellent"
    },
    "quick_stats": {
      "detections_week": 42,
      "alerts_unread": 3,
      "alerts_critical": 0,
      "recommendations_count": 5
    },
    "top_recommendations": [
      {
        "type": "optimization",
        "priority": 4,
        "title": "Optimiser la surveillance",
        "description": "...",
        "action": "..."
      }
    ],
    "alerts": {
      "has_critical": false,
      "needs_attention": false
    }
  }
}
```

### 4. Prédiction d'Activité

**Endpoint:** `GET /analytics/api/ai/predict-activity/`

Prédit l'activité future basée sur les patterns historiques.

**Paramètres:**
- `periods` (optionnel, défaut: 7) - Nombre de périodes à prédire
- `interval` (optionnel, défaut: day) - Intervalle: `hour`, `day`, `week`

**Exemple de requête:**
```bash
curl -X GET "http://localhost:8000/analytics/api/ai/predict-activity/?periods=7&interval=day" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 5. Évaluation des Risques

**Endpoint:** `GET /analytics/api/ai/risk-assessment/`

Évalue le niveau de risque global basé sur l'analyse IA.

**Paramètres:**
- `days` (optionnel, défaut: 7) - Période d'analyse

**Exemple de requête:**
```bash
curl -X GET "http://localhost:8000/analytics/api/ai/risk-assessment/?days=7" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Exemple de réponse:**
```json
{
  "status": "success",
  "data": {
    "risk_score": 35,
    "risk_level": "medium",
    "risk_label": "Moyen",
    "color": "yellow",
    "factors": [
      {
        "factor": "anomalies",
        "weight": 20,
        "description": "4 patterns anormaux détectés"
      },
      {
        "factor": "high_alert_rate",
        "weight": 10,
        "description": "Taux d'alerte élevé: 35%"
      }
    ],
    "recommendations": [...],
    "period_days": 7,
    "metrics": {
      "total_detections": 50,
      "total_alerts": 8,
      "critical_alerts": 0,
      "anomalies": 4,
      "dangerous_objects": 2
    }
  }
}
```

### 6. Recherche Intelligente (NLP)

**Endpoint:** `POST /analytics/api/ai/smart-search/`

Recherche avec traitement du langage naturel.

**Body:**
```json
{
  "query": "show me suspicious detections from last week",
  "context": "security"
}
```

**Exemple de requête:**
```bash
curl -X POST "http://localhost:8000/analytics/api/ai/smart-search/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"query": "show me dangerous objects detected today"}'
```

### 7. Suggestions d'Optimisation

**Endpoint:** `GET /analytics/api/ai/optimization/`

Génère des suggestions d'optimisation personnalisées.

**Exemple de requête:**
```bash
curl -X GET "http://localhost:8000/analytics/api/ai/optimization/" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Exemple de réponse:**
```json
{
  "status": "success",
  "data": {
    "total_suggestions": 6,
    "by_category": {
      "surveillance": [
        {
          "title": "Augmenter la fréquence de surveillance",
          "description": "...",
          "action": "..."
        }
      ],
      "performance": [...],
      "coverage": [...],
      "alerts": [...]
    },
    "all_suggestions": [...],
    "priority_actions": [...]
  }
}
```

## Types de Recommandations

Le système génère 5 types de recommandations :

1. **SECURITY** - Recommandations liées à la sécurité
2. **OPTIMIZATION** - Suggestions d'optimisation du système
3. **BEHAVIOR** - Insights sur les patterns comportementaux
4. **ALERT** - Recommandations sur la gestion des alertes
5. **MONITORING** - Suggestions pour améliorer la surveillance

## Niveaux de Priorité

Les recommandations sont classées par priorité (1-5) :

- **5 - CRITICAL** : Action immédiate requise
- **4 - HIGH** : Important, à traiter rapidement
- **3 - MEDIUM** : Moyen, à traiter sous quelques jours
- **2 - LOW** : Faible priorité
- **1 - INFO** : Information seulement

## Score de Confiance

Chaque recommandation inclut un score de confiance (0-1) :

- **0.9-1.0** : Très haute confiance
- **0.8-0.9** : Haute confiance
- **0.7-0.8** : Confiance moyenne-haute
- **0.6-0.7** : Confiance moyenne
- **< 0.6** : Confiance faible (filtré par défaut)

## Système de Recommandations

### Moteur d'Analyse

Le `RecommendationEngine` analyse plusieurs aspects :

1. **Patterns de sécurité** - Détecte les objets dangereux et patterns à risque
2. **Fréquence de détection** - Analyse la régularité et les pics d'activité
3. **Patterns d'objets** - Identifie les concentrations inhabituelles
4. **Anomalies** - Détecte les comportements anormaux via ML
5. **Lacunes de couverture** - Identifie les périodes sans surveillance
6. **Efficacité des alertes** - Analyse le temps de réponse
7. **Patterns temporels** - Détecte les tendances horaires/hebdomadaires

### Filtres Intelligents

Le `SmartRecommendationFilter` offre :

- **Filtrage par confiance** - Élimine les recommandations peu fiables
- **Groupement par type** - Organise les recommandations
- **Sélection des actionnables** - Filtre pour actions prioritaires

## Intégration

### Python/Django

```python
from analytics.ai_recommendation_system import RecommendationEngine

# Générer des recommandations
engine = RecommendationEngine(user)
recommendations = engine.analyze_and_recommend(days=30)

# Filtrer
from analytics.ai_recommendation_system import SmartRecommendationFilter
filtered = SmartRecommendationFilter.filter_recommendations(
    recommendations, 
    max_count=5, 
    min_confidence=0.7
)
```

### JavaScript/Frontend

```javascript
// Récupérer les recommandations
fetch('/analytics/api/ai/recommendations/?days=30&max_count=10')
  .then(response => response.json())
  .then(data => {
    console.log('Recommandations:', data.data.recommendations);
    console.log('Statistiques:', data.data.statistics);
  });

// Dashboard complet
fetch('/analytics/api/ai/dashboard/')
  .then(response => response.json())
  .then(data => {
    console.log('Score de santé:', data.data.health.score);
    console.log('Top recommandations:', data.data.top_recommendations);
  });
```

## Exemples d'Utilisation

### 1. Obtenir les recommandations prioritaires

```bash
curl -X GET "http://localhost:8000/analytics/api/ai/recommendations/?actionable_only=true&max_count=5" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 2. Analyser les risques de sécurité

```bash
curl -X GET "http://localhost:8000/analytics/api/ai/risk-assessment/?days=30" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 3. Obtenir des suggestions d'optimisation

```bash
curl -X GET "http://localhost:8000/analytics/api/ai/optimization/" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 4. Dashboard complet

```bash
curl -X GET "http://localhost:8000/analytics/api/ai/dashboard/" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## Bonnes Pratiques

1. **Vérifier régulièrement** - Consultez les recommandations au moins une fois par semaine
2. **Prioriser les actions** - Traitez d'abord les recommandations CRITICAL et HIGH
3. **Suivre la confiance** - Concentrez-vous sur les recommandations avec confiance > 0.8
4. **Agir sur les insights** - Utilisez les recommandations pour améliorer votre système
5. **Surveiller le score de santé** - Maintenez un score > 70

## Dépendances

- Django 3.2+
- scikit-learn (pour ML et anomalies)
- numpy, pandas (pour analyse de données)
- Prophet (optionnel, pour prédictions avancées)

## Support

Pour plus d'informations ou support :
- Documentation API complète : `/analytics/api/`
- Email : support@argus-security.com
- GitHub : https://github.com/your-repo/argus
