"""
NLP Service for Natural Language Queries and Narrative Reports
Powered by GPT-4 and spaCy
"""
from django.conf import settings
from datetime import datetime, timedelta
from django.utils import timezone
import os
import logging
import re

logger = logging.getLogger(__name__)

# Conditional imports
try:
    import openai
    openai.api_key = os.getenv('OPENAI_API_KEY', '')
    OPENAI_AVAILABLE = bool(openai.api_key)
except ImportError:
    OPENAI_AVAILABLE = False
    logger.warning("OpenAI not installed. GPT-4 features disabled.")

try:
    import spacy
    # Try to load English model
    try:
        nlp = spacy.load("en_core_web_sm")
        SPACY_AVAILABLE = True
    except OSError:
        SPACY_AVAILABLE = False
        logger.warning("spaCy model not found. Run: python -m spacy download en_core_web_sm")
except ImportError:
    SPACY_AVAILABLE = False
    logger.warning("spaCy not installed. NLP queries disabled.")


class NarrativeReportGenerator:
    """
    Génère des rapports narratifs en langage naturel avec GPT-4
    """
    
    @staticmethod
    def generate_daily_summary(user, analytics_data, detections):
        """
        Génère un résumé quotidien narratif
        
        Args:
            user: User instance
            analytics_data: DetectionAnalytics instance
            detections: QuerySet de DetectionResult
            
        Returns:
            str: Résumé en langage naturel
        """
        if not OPENAI_AVAILABLE:
            return NarrativeReportGenerator._generate_fallback_summary(analytics_data)
        
        # Préparer le contexte pour GPT-4
        context = {
            'date': analytics_data.period_start.strftime('%Y-%m-%d'),
            'total_detections': analytics_data.total_detections,
            'total_objects': analytics_data.total_objects_detected,
            'avg_objects': round(analytics_data.avg_objects_per_detection, 2),
            'suspicious_count': analytics_data.suspicious_objects_count,
            'high_risk_count': analytics_data.high_risk_detections,
            'objects_by_class': analytics_data.get_objects_by_class(),
            'detections_by_hour': analytics_data.get_detections_by_hour(),
        }
        
        # Identifier les heures de pic
        hourly_data = context['detections_by_hour']
        if hourly_data:
            peak_hour = max(hourly_data.items(), key=lambda x: x[1])
            context['peak_hour'] = peak_hour[0]
            context['peak_count'] = peak_hour[1]
        
        # Prompt pour GPT-4
        prompt = f"""Generate a concise, professional daily security monitoring summary for {context['date']}.

Data:
- Total detections: {context['total_detections']}
- Objects detected: {context['total_objects']} ({context['avg_objects']} avg per detection)
- Suspicious objects: {context['suspicious_count']}
- High-risk detections: {context['high_risk_count']}
- Peak activity: {context.get('peak_hour', 'N/A')}:00 ({context.get('peak_count', 0)} detections)

Top detected objects: {', '.join([f"{k} ({v})" for k, v in list(context['objects_by_class'].items())[:5]])}

Write a 3-4 sentence summary highlighting:
1. Overall activity level
2. Notable patterns or concerns
3. Any security recommendations

Keep it professional and actionable."""

        try:
            response = openai.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a professional security analyst writing daily surveillance reports."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=200,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
        
        except Exception as e:
            logger.error(f"GPT-4 error: {e}")
            return NarrativeReportGenerator._generate_fallback_summary(analytics_data)
    
    @staticmethod
    def _generate_fallback_summary(analytics_data):
        """Résumé de base sans IA (fallback)"""
        summary = f"Daily Summary for {analytics_data.period_start.strftime('%Y-%m-%d')}:\n\n"
        summary += f"• Total Detections: {analytics_data.total_detections}\n"
        summary += f"• Objects Detected: {analytics_data.total_objects_detected}\n"
        summary += f"• Average per Detection: {analytics_data.avg_objects_per_detection:.1f}\n"
        
        if analytics_data.suspicious_objects_count > 0:
            summary += f"\n⚠️ Suspicious Objects: {analytics_data.suspicious_objects_count}\n"
        
        if analytics_data.high_risk_detections > 0:
            summary += f"🚨 High-Risk Detections: {analytics_data.high_risk_detections}\n"
        
        # Top objets
        objects_by_class = analytics_data.get_objects_by_class()
        if objects_by_class:
            top_3 = sorted(objects_by_class.items(), key=lambda x: x[1], reverse=True)[:3]
            summary += f"\nMost Detected: {', '.join([f'{k} ({v})' for k, v in top_3])}\n"
        
        return summary
    
    @staticmethod
    def generate_weekly_report(user, weekly_analytics, anomalies=None, trends=None):
        """
        Génère un rapport hebdomadaire détaillé
        
        Args:
            user: User instance
            weekly_analytics: List de DetectionAnalytics (7 jours)
            anomalies: Dict d'anomalies détectées
            trends: Dict de tendances
            
        Returns:
            str: Rapport hebdomadaire narratif
        """
        if not OPENAI_AVAILABLE:
            return NarrativeReportGenerator._generate_fallback_weekly(weekly_analytics)
        
        # Agréger les données hebdomadaires
        total_detections = sum(a.total_detections for a in weekly_analytics)
        total_objects = sum(a.total_objects_detected for a in weekly_analytics)
        suspicious_total = sum(a.suspicious_objects_count for a in weekly_analytics)
        
        # Identifier les jours les plus actifs
        days_sorted = sorted(weekly_analytics, key=lambda x: x.total_detections, reverse=True)
        busiest_day = days_sorted[0] if days_sorted else None
        
        prompt = f"""Generate a comprehensive weekly security monitoring report.

Weekly Stats (Last 7 Days):
- Total Detections: {total_detections}
- Total Objects: {total_objects}
- Suspicious Objects: {suspicious_total}
- Busiest Day: {busiest_day.period_start.strftime('%A, %B %d') if busiest_day else 'N/A'} ({busiest_day.total_detections if busiest_day else 0} detections)

"""
        
        if anomalies:
            prompt += f"- Anomalies Detected: {anomalies.get('anomaly_count', 0)}\n"
        
        if trends:
            prompt += f"- Object Trends Tracked: {len(trends.get('trends', []))}\n"
        
        prompt += """
Write a professional weekly summary (5-6 sentences) covering:
1. Overall security posture
2. Week-over-week trends
3. Notable incidents or anomalies
4. Strategic recommendations
5. Upcoming focus areas

Format as a cohesive narrative report."""

        try:
            response = openai.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a senior security operations manager writing weekly executive reports."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=400,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
        
        except Exception as e:
            logger.error(f"GPT-4 error: {e}")
            return NarrativeReportGenerator._generate_fallback_weekly(weekly_analytics)
    
    @staticmethod
    def _generate_fallback_weekly(weekly_analytics):
        """Rapport hebdomadaire de base sans IA"""
        total = sum(a.total_detections for a in weekly_analytics)
        avg_daily = total / len(weekly_analytics) if weekly_analytics else 0
        
        report = "=== WEEKLY SECURITY REPORT ===\n\n"
        report += f"Period: {weekly_analytics[0].period_start.strftime('%Y-%m-%d')} to {weekly_analytics[-1].period_end.strftime('%Y-%m-%d')}\n\n"
        report += f"Total Detections: {total}\n"
        report += f"Daily Average: {avg_daily:.1f}\n\n"
        
        report += "Daily Breakdown:\n"
        for analytics in weekly_analytics:
            report += f"  {analytics.period_start.strftime('%A')}: {analytics.total_detections} detections\n"
        
        return report
    
    @staticmethod
    def generate_insight_explanation(insight_data):
        """
        Génère une explication narrative pour un insight analytique
        
        Args:
            insight_data: Dict avec les données de l'insight
            
        Returns:
            str: Explication en langage naturel
        """
        if not OPENAI_AVAILABLE:
            return f"Insight: {insight_data.get('title', 'Analytics Insight')}"
        
        prompt = f"""Explain this security analytics insight in 2-3 clear sentences for a non-technical user:

Title: {insight_data.get('title', 'Analytics Insight')}
Type: {insight_data.get('type', 'Unknown')}
Confidence: {insight_data.get('confidence', 0):.0%}
Data: {insight_data.get('summary', 'N/A')}

Make it actionable and easy to understand."""

        try:
            response = openai.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are explaining security analytics to non-technical users."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=150,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
        
        except Exception as e:
            logger.error(f"GPT-4 error: {e}")
            return f"{insight_data.get('title', 'Insight')}: {insight_data.get('summary', 'See details for more information.')}"


class NaturalLanguageQueryProcessor:
    """
    Traite les requêtes en langage naturel sur les données de détection
    """
    
    def __init__(self):
        self.nlp = nlp if SPACY_AVAILABLE else None
    
    def process_query(self, query_text, user):
        """
        Traite une requête en langage naturel
        
        Args:
            query_text: str - Requête de l'utilisateur
            user: User instance
            
        Returns:
            Dict avec résultats et SQL query générée
        """
        query_text = query_text.lower().strip()
        
        # Patterns de requêtes courantes
        patterns = {
            r'(show|display|what|list).*(today|aujourd\'hui)': self._query_today,
            r'(show|display|what|list).*(this week|cette semaine|week)': self._query_this_week,
            r'(show|display|what|list).*(suspicious|suspect|danger)': self._query_suspicious,
            r'(how many|combien|count).*(detection|détection)': self._query_count,
            r'(peak|pic|max|most active).*(hour|heure|time)': self._query_peak_hours,
            r'(trend|tendance|pattern).*([a-z]+)': self._query_object_trend,
            r'(anomal|unusual|inhabituel|anormal)': self._query_anomalies,
        }
        
        # Matcher le pattern
        for pattern, handler in patterns.items():
            if re.search(pattern, query_text):
                return handler(user, query_text)
        
        # Fallback: recherche générique
        return self._generic_search(user, query_text)
    
    def _query_today(self, user, query):
        """Activité d'aujourd'hui"""
        from detection.models import DetectionResult
        
        today = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
        detections = DetectionResult.objects.filter(
            user=user,
            uploaded_at__gte=today
        )
        
        return {
            'query': query,
            'intent': 'today_activity',
            'results': {
                'count': detections.count(),
                'detections': list(detections.values('id', 'uploaded_at', 'objects_detected')[:10])
            },
            'summary': f"Found {detections.count()} detections today"
        }
    
    def _query_this_week(self, user, query):
        """Activité de cette semaine"""
        from detection.models import DetectionResult
        
        week_ago = timezone.now() - timedelta(days=7)
        detections = DetectionResult.objects.filter(
            user=user,
            uploaded_at__gte=week_ago
        )
        
        return {
            'query': query,
            'intent': 'weekly_activity',
            'results': {
                'count': detections.count(),
                'avg_daily': detections.count() / 7
            },
            'summary': f"Found {detections.count()} detections this week (avg {detections.count()/7:.1f}/day)"
        }
    
    def _query_suspicious(self, user, query):
        """Objets suspects"""
        from analytics.models import SecurityAlert
        
        alerts = SecurityAlert.objects.filter(
            user=user,
            alert_type='suspicious_object'
        ).order_by('-created_at')[:10]
        
        return {
            'query': query,
            'intent': 'suspicious_objects',
            'results': {
                'count': alerts.count(),
                'alerts': list(alerts.values('id', 'title', 'severity', 'created_at'))
            },
            'summary': f"Found {alerts.count()} suspicious object alerts"
        }
    
    def _query_count(self, user, query):
        """Nombre de détections"""
        from detection.models import DetectionResult
        
        total = DetectionResult.objects.filter(user=user).count()
        
        return {
            'query': query,
            'intent': 'detection_count',
            'results': {'total_detections': total},
            'summary': f"Total detections: {total}"
        }
    
    def _query_peak_hours(self, user, query):
        """Heures de pic d'activité"""
        from analytics.models import DetectionAnalytics
        
        recent_analytics = DetectionAnalytics.objects.filter(
            user=user,
            period_type='daily'
        ).order_by('-period_start').first()
        
        if recent_analytics:
            hourly = recent_analytics.get_detections_by_hour()
            if hourly:
                peak = max(hourly.items(), key=lambda x: x[1])
                return {
                    'query': query,
                    'intent': 'peak_hours',
                    'results': {
                        'peak_hour': peak[0],
                        'detection_count': peak[1],
                        'hourly_distribution': hourly
                    },
                    'summary': f"Peak activity at {peak[0]}:00 with {peak[1]} detections"
                }
        
        return {
            'query': query,
            'intent': 'peak_hours',
            'results': {},
            'summary': "No peak hour data available"
        }
    
    def _query_object_trend(self, user, query):
        """Tendance d'un objet spécifique"""
        from analytics.models import ObjectTrend
        
        # Extraire le nom de l'objet de la requête
        if self.nlp:
            doc = self.nlp(query)
            nouns = [token.text for token in doc if token.pos_ == "NOUN"]
        else:
            nouns = query.split()
        
        trends = ObjectTrend.objects.filter(user=user)
        
        if nouns:
            for noun in nouns:
                matched = trends.filter(object_class__icontains=noun).first()
                if matched:
                    return {
                        'query': query,
                        'intent': 'object_trend',
                        'results': {
                            'object_class': matched.object_class,
                            'detection_count': matched.detection_count,
                            'trend_direction': matched.trend_direction,
                            'is_anomaly': matched.is_anomaly
                        },
                        'summary': f"{matched.object_class}: {matched.detection_count} detections, trend: {matched.trend_direction}"
                    }
        
        return {
            'query': query,
            'intent': 'object_trend',
            'results': {'trends': list(trends.values('object_class', 'detection_count', 'trend_direction')[:5])},
            'summary': f"Top object trends available"
        }
    
    def _query_anomalies(self, user, query):
        """Anomalies détectées"""
        from analytics.models import SecurityAlert
        
        anomalies = SecurityAlert.objects.filter(
            user=user,
            alert_type='anomaly'
        ).order_by('-created_at')[:5]
        
        return {
            'query': query,
            'intent': 'anomalies',
            'results': {
                'count': anomalies.count(),
                'recent_anomalies': list(anomalies.values('title', 'severity', 'created_at'))
            },
            'summary': f"Found {anomalies.count()} recent anomalies"
        }
    
    def _generic_search(self, user, query):
        """Recherche générique"""
        return {
            'query': query,
            'intent': 'generic',
            'results': {},
            'summary': f"Unable to interpret query: '{query}'. Try asking about 'today', 'this week', 'suspicious objects', or 'anomalies'."
        }
