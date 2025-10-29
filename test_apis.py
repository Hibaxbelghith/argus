"""
Script de test des APIs REST d'Argus
Utilisation: python test_apis.py
"""

import requests
import json
from datetime import datetime

# Configuration
BASE_URL = 'http://localhost:8000'
USERNAME = 'admin'  # Modifier avec vos identifiants
PASSWORD = 'admin'  # Modifier avec vos identifiants

class ArgusAPITester:
    def __init__(self, base_url, username, password):
        self.base_url = base_url
        self.session = requests.Session()
        self.username = username
        self.password = password
        
    def login(self):
        """Connexion à l'application"""
        print("🔐 Connexion en cours...")
        
        # Récupérer le token CSRF
        response = self.session.get(f'{self.base_url}/auth/login/')
        
        # Se connecter
        login_data = {
            'username': self.username,
            'password': self.password,
        }
        
        response = self.session.post(f'{self.base_url}/auth/login/', data=login_data)
        
        if response.status_code == 200:
            print("✅ Connexion réussie")
            return True
        else:
            print(f"❌ Échec de connexion: {response.status_code}")
            return False
    
    def test_analytics_stats(self):
        """Test: Récupérer les statistiques analytics"""
        print("\n📊 Test: Analytics Stats Summary")
        
        response = self.session.get(f'{self.base_url}/analytics/api/stats/summary/')
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Status: {data['status']}")
            print(f"   Total détections: {data['data']['total_detections']}")
            print(f"   Total objets: {data['data']['total_objects']}")
            print(f"   Alertes non lues: {data['data']['alerts']['unread']}")
            return True
        else:
            print(f"❌ Erreur: {response.status_code}")
            return False
    
    def test_trends_list(self):
        """Test: Récupérer les tendances"""
        print("\n📈 Test: Trends List")
        
        response = self.session.get(f'{self.base_url}/analytics/api/trends/?limit=5')
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Status: {data['status']}")
            print(f"   Nombre de tendances: {data['count']}")
            
            for trend in data['data'][:3]:
                print(f"   - {trend['object_class']}: {trend['detection_count']} détections")
            return True
        else:
            print(f"❌ Erreur: {response.status_code}")
            return False
    
    def test_alerts_list(self):
        """Test: Récupérer les alertes"""
        print("\n🚨 Test: Alerts List")
        
        response = self.session.get(f'{self.base_url}/analytics/api/alerts/?limit=5')
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Status: {data['status']}")
            print(f"   Nombre d'alertes: {data['count']}")
            
            for alert in data['data'][:3]:
                print(f"   - [{alert['severity']}] {alert['title']}")
            return True
        else:
            print(f"❌ Erreur: {response.status_code}")
            return False
    
    def test_chart_data(self):
        """Test: Données pour graphiques"""
        print("\n📊 Test: Chart Data")
        
        response = self.session.get(f'{self.base_url}/analytics/api/charts/detections/?days=7')
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Status: {data['status']}")
            chart = data['chart_data']
            print(f"   Jours: {', '.join(chart['labels'])}")
            print(f"   Détections: {chart['datasets']['detections']}")
            return True
        else:
            print(f"❌ Erreur: {response.status_code}")
            return False
    
    def test_health_analytics(self):
        """Test: Health check analytics"""
        print("\n💚 Test: Analytics Health Check")
        
        response = self.session.get(f'{self.base_url}/analytics/api/health/')
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Status: {data['status']}")
            print(f"   Module: {data['module']}")
            print(f"   Analytics: {data['stats']['analytics_count']}")
            print(f"   Tendances: {data['stats']['trends_count']}")
            print(f"   Alertes: {data['stats']['alerts_count']}")
            return True
        else:
            print(f"❌ Erreur: {response.status_code}")
            return False
    
    def test_notifications_list(self):
        """Test: Liste des notifications"""
        print("\n🔔 Test: Notifications List")
        
        response = self.session.get(f'{self.base_url}/notifications/api/list/?limit=5')
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Status: {data['status']}")
            print(f"   Nombre de notifications: {data['count']}")
            
            for notif in data['data'][:3]:
                read_status = "✓" if notif['is_read'] else "✗"
                print(f"   {read_status} [{notif['severity']}] {notif['title']}")
            return True
        else:
            print(f"❌ Erreur: {response.status_code}")
            return False
    
    def test_notifications_stats(self):
        """Test: Statistiques notifications"""
        print("\n📊 Test: Notifications Stats")
        
        response = self.session.get(f'{self.base_url}/notifications/api/stats/')
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Status: {data['status']}")
            stats = data['stats']['global']
            print(f"   Total: {stats['total']}")
            print(f"   Non lues: {stats['unread']}")
            print(f"   Critiques: {stats['by_severity_critical']}")
            return True
        else:
            print(f"❌ Erreur: {response.status_code}")
            return False
    
    def test_preferences_get(self):
        """Test: Récupérer préférences"""
        print("\n⚙️  Test: Get Preferences")
        
        response = self.session.get(f'{self.base_url}/notifications/api/preferences/')
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Status: {data['status']}")
            prefs = data['preferences']
            print(f"   Méthodes actives: {', '.join(prefs['enabled_methods'])}")
            print(f"   Sévérité min (email): {prefs['min_severity_email']}")
            print(f"   Heures silencieuses: {prefs['quiet_hours_enabled']}")
            return True
        else:
            print(f"❌ Erreur: {response.status_code}")
            return False
    
    def test_rules_list(self):
        """Test: Liste des règles"""
        print("\n📋 Test: Rules List")
        
        response = self.session.get(f'{self.base_url}/notifications/api/rules/')
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Status: {data['status']}")
            print(f"   Nombre de règles: {data['count']}")
            
            for rule in data['data'][:3]:
                active = "✓" if rule['is_active'] else "✗"
                print(f"   {active} {rule['name']} (priorité: {rule['priority']})")
            return True
        else:
            print(f"❌ Erreur: {response.status_code}")
            return False
    
    def test_health_notifications(self):
        """Test: Health check notifications"""
        print("\n💚 Test: Notifications Health Check")
        
        response = self.session.get(f'{self.base_url}/notifications/api/health/')
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Status: {data['status']}")
            print(f"   Module: {data['module']}")
            print(f"   Notifications: {data['stats']['notifications_count']}")
            print(f"   Non lues: {data['stats']['unread_count']}")
            print(f"   Règles actives: {data['stats']['active_rules_count']}")
            return True
        else:
            print(f"❌ Erreur: {response.status_code}")
            return False
    
    def test_create_notification(self):
        """Test: Créer notification de test"""
        print("\n🧪 Test: Create Test Notification")
        
        payload = {
            "method": "web",
            "message": "Test automatique de l'API"
        }
        
        response = self.session.post(
            f'{self.base_url}/notifications/api/test/',
            json=payload,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Status: {data['status']}")
            print(f"   Message: {data['message']}")
            print(f"   Notification ID: {data['notification_id']}")
            return True
        else:
            print(f"❌ Erreur: {response.status_code}")
            return False
    
    def run_all_tests(self):
        """Exécute tous les tests"""
        print("=" * 60)
        print("🧪 TESTS DES APIs REST - ARGUS")
        print("=" * 60)
        
        if not self.login():
            print("\n❌ Impossible de se connecter. Tests annulés.")
            return
        
        results = {
            'Analytics Stats': self.test_analytics_stats(),
            'Trends List': self.test_trends_list(),
            'Alerts List': self.test_alerts_list(),
            'Chart Data': self.test_chart_data(),
            'Analytics Health': self.test_health_analytics(),
            'Notifications List': self.test_notifications_list(),
            'Notifications Stats': self.test_notifications_stats(),
            'Preferences': self.test_preferences_get(),
            'Rules List': self.test_rules_list(),
            'Notifications Health': self.test_health_notifications(),
            'Test Notification': self.test_create_notification(),
        }
        
        print("\n" + "=" * 60)
        print("📊 RÉSULTATS DES TESTS")
        print("=" * 60)
        
        passed = sum(results.values())
        total = len(results)
        
        for test_name, result in results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{status} - {test_name}")
        
        print("-" * 60)
        print(f"Total: {passed}/{total} tests réussis ({passed/total*100:.1f}%)")
        print("=" * 60)


def main():
    """Point d'entrée principal"""
    print("\n🚀 Démarrage des tests API...\n")
    
    tester = ArgusAPITester(BASE_URL, USERNAME, PASSWORD)
    tester.run_all_tests()
    
    print("\n✨ Tests terminés !\n")


if __name__ == '__main__':
    main()
