#!/usr/bin/env python
"""
Script rapide pour générer des recommandations IA
Usage: py generate_ai_recommendations.py
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'argus.settings')
django.setup()

from analytics.ai_recommendation_system import RecommendationEngine
from analytics.models import AIRecommendation
from django.contrib.auth import get_user_model

User = get_user_model()

def main():
    print("🤖 Génération de recommandations IA...\n")
    
    # Récupérer le premier utilisateur
    try:
        user = User.objects.first()
        if not user:
            print("❌ Aucun utilisateur trouvé. Créez un utilisateur d'abord.")
            return
        
        print(f"👤 Utilisateur: {user.username}")
    except Exception as e:
        print(f"❌ Erreur lors de la récupération de l'utilisateur: {e}")
        return
    
    # Créer le moteur de recommandations
    print("\n🔄 Initialisation du moteur IA...")
    engine = RecommendationEngine(user=user)
    
    # Générer les recommandations
    try:
        print("🧠 Analyse en cours...\n")
        recommendations = engine.analyze_and_recommend()
        print(f"✅ {len(recommendations)} recommandations générées\n")
        
        if not recommendations:
            print("ℹ️ Aucune recommandation générée. Cela peut être normal si :")
            print("   - Il n'y a pas assez de détections")
            print("   - Toutes les alertes sont déjà traitées")
            print("   - Le système ne détecte pas d'anomalies")
            return
        
        # Afficher les recommandations
        print("=" * 80)
        for i, rec in enumerate(recommendations, 1):
            priority_icon = "🔴" if rec['priority'] == 5 else "🟠" if rec['priority'] == 4 else "🟡" if rec['priority'] == 3 else "🟢"
            print(f"\n{priority_icon} {i}. [{rec['type'].upper()}] {rec['title']}")
            print(f"   Priorité: {rec['priority']}/5 | Confiance: {rec['confidence']:.0%} | Impact: {rec['impact']}")
            print(f"   📝 {rec['description']}")
            print(f"   💡 Action: {rec['action']}")
        
        print("\n" + "=" * 80)
        
        # Sauvegarder les recommandations de haute priorité
        saved_count = 0
        for rec in recommendations:
            if rec['priority'] >= 3:  # Priorité moyenne ou plus
                try:
                    ai_rec = AIRecommendation.objects.create(
                        user=user,
                        recommendation_type=rec['type'],
                        title=rec['title'],
                        description=rec['description'],
                        action=rec['action'],
                        priority=rec['priority'],
                        confidence=rec['confidence'],
                        impact=rec['impact'],
                        metadata=rec.get('context', {}),
                        status='pending'
                    )
                    saved_count += 1
                    print(f"💾 Sauvegardé: {ai_rec.title} (ID: {ai_rec.id})")
                except Exception as e:
                    print(f"⚠️ Erreur lors de la sauvegarde: {e}")
        
        print(f"\n✅ {saved_count}/{len(recommendations)} recommandations sauvegardées en base de données")
        print(f"\n🌐 Accédez au dashboard IA: http://localhost:8000/analytics/ai-dashboard/")
        
    except Exception as e:
        print(f"❌ Erreur lors de la génération: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
