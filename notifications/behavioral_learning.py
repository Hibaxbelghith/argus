"""
Behavioral Learning System
Learns from user interactions to personalize notifications
"""
from django.db.models import Count, Avg, Q
from django.utils import timezone
from datetime import timedelta
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)


class BehavioralLearner:
    """
    Apprend des interactions utilisateur pour adapter les notifications
    """
    
    def __init__(self, user):
        self.user = user
    
    def analyze_interaction_patterns(self, lookback_days=30):
        """
        Analyse les patterns d'interaction avec les notifications
        
        Args:
            lookback_days: Nombre de jours à analyser
            
        Returns:
            Dict avec patterns appris
        """
        from notifications.models import Notification
        
        cutoff_date = timezone.now() - timedelta(days=lookback_days)
        
        notifications = Notification.objects.filter(
            user=self.user,
            created_at__gte=cutoff_date
        )
        
        if not notifications.exists():
            return {
                'patterns': [],
                'message': 'Insufficient interaction history'
            }
        
        patterns = {}
        
        # 1. Analyser les taux d'ouverture par type
        patterns['read_rates_by_type'] = self._analyze_read_rates(notifications)
        
        # 2. Analyser les délais de lecture
        patterns['response_times'] = self._analyze_response_times(notifications)
        
        # 3. Analyser les préférences horaires
        patterns['preferred_times'] = self._analyze_preferred_times(notifications)
        
        # 4. Analyser les sévérités ignorées
        patterns['ignored_severities'] = self._analyze_ignored_severities(notifications)
        
        # 5. Générer des recommandations
        patterns['recommendations'] = self._generate_preference_recommendations(patterns)
        
        return patterns
    
    def _analyze_read_rates(self, notifications):
        """Analyse les taux de lecture par type de notification"""
        type_stats = {}
        
        for notif_type in ['alert', 'insight', 'report', 'system']:
            type_notifs = notifications.filter(notification_type=notif_type)
            total = type_notifs.count()
            
            if total > 0:
                read_count = type_notifs.filter(read_at__isnull=False).count()
                read_rate = read_count / total
                
                type_stats[notif_type] = {
                    'total': total,
                    'read': read_count,
                    'read_rate': round(read_rate, 2),
                    'engagement': 'high' if read_rate > 0.7 else 'medium' if read_rate > 0.3 else 'low'
                }
        
        return type_stats
    
    def _analyze_response_times(self, notifications):
        """Analyse les délais moyens de lecture"""
        read_notifs = notifications.filter(read_at__isnull=False)
        
        response_times = []
        
        for notif in read_notifs:
            delay = (notif.read_at - notif.created_at).total_seconds() / 60  # en minutes
            response_times.append(delay)
        
        if not response_times:
            return {'message': 'No read notifications to analyze'}
        
        return {
            'avg_response_time_minutes': round(sum(response_times) / len(response_times), 1),
            'median_response_time_minutes': round(sorted(response_times)[len(response_times)//2], 1),
            'fast_responses': len([t for t in response_times if t < 5]),  # < 5 minutes
            'delayed_responses': len([t for t in response_times if t > 60]),  # > 1 heure
        }
    
    def _analyze_preferred_times(self, notifications):
        """Identifie les heures préférées pour lire les notifications"""
        read_notifs = notifications.filter(read_at__isnull=False)
        
        hourly_reads = defaultdict(int)
        
        for notif in read_notifs:
            hour = notif.read_at.hour
            hourly_reads[hour] += 1
        
        if not hourly_reads:
            return {'message': 'No read pattern data'}
        
        # Trouver les heures les plus actives
        sorted_hours = sorted(hourly_reads.items(), key=lambda x: x[1], reverse=True)
        
        return {
            'most_active_hours': [h for h, _ in sorted_hours[:3]],
            'least_active_hours': [h for h, _ in sorted_hours[-3:]],
            'hourly_distribution': dict(hourly_reads),
            'peak_hour': sorted_hours[0][0] if sorted_hours else None
        }
    
    def _analyze_ignored_severities(self, notifications):
        """Identifie les sévérités fréquemment ignorées"""
        severity_stats = {}
        
        for severity in ['low', 'medium', 'high', 'critical']:
            sev_notifs = notifications.filter(severity=severity)
            total = sev_notifs.count()
            
            if total > 0:
                unread = sev_notifs.filter(read_at__isnull=True).count()
                ignore_rate = unread / total
                
                severity_stats[severity] = {
                    'total': total,
                    'unread': unread,
                    'ignore_rate': round(ignore_rate, 2),
                    'should_filter': ignore_rate > 0.7  # Si >70% ignorés
                }
        
        return severity_stats
    
    def _generate_preference_recommendations(self, patterns):
        """Génère des recommandations basées sur les patterns"""
        recommendations = []
        
        # Recommandations basées sur taux de lecture
        read_rates = patterns.get('read_rates_by_type', {})
        for notif_type, stats in read_rates.items():
            if stats['engagement'] == 'low':
                recommendations.append({
                    'type': 'reduce_frequency',
                    'target': f"{notif_type}_notifications",
                    'reason': f"Low engagement with {notif_type} notifications ({stats['read_rate']*100:.0f}% read rate)",
                    'action': f"Consider reducing {notif_type} notification frequency"
                })
        
        # Recommandations basées sur sévérités ignorées
        ignored = patterns.get('ignored_severities', {})
        for severity, stats in ignored.items():
            if stats.get('should_filter'):
                recommendations.append({
                    'type': 'adjust_severity_threshold',
                    'target': f"{severity}_severity",
                    'reason': f"{stats['ignore_rate']*100:.0f}% of {severity} notifications are ignored",
                    'action': f"Consider disabling or reducing {severity} severity notifications"
                })
        
        # Recommandations basées sur heures préférées
        preferred_times = patterns.get('preferred_times', {})
        if 'most_active_hours' in preferred_times:
            active_hours = preferred_times['most_active_hours']
            recommendations.append({
                'type': 'optimize_timing',
                'target': 'notification_schedule',
                'reason': f"Most active during hours: {active_hours}",
                'action': f"Consider batching non-urgent notifications for peak hours: {active_hours}"
            })
        
        return recommendations
    
    def adapt_preferences(self, auto_apply=False):
        """
        Adapte automatiquement les préférences selon l'apprentissage
        
        Args:
            auto_apply: Si True, applique automatiquement les changements
            
        Returns:
            Dict avec changements suggérés/appliqués
        """
        patterns = self.analyze_interaction_patterns()
        recommendations = patterns.get('recommendations', [])
        
        if not recommendations:
            return {
                'changes': [],
                'message': 'No adaptation needed based on current patterns'
            }
        
        suggested_changes = []
        
        for rec in recommendations:
            change = {
                'recommendation': rec,
                'applied': False
            }
            
            if auto_apply:
                # Appliquer les changements
                success = self._apply_recommendation(rec)
                change['applied'] = success
            
            suggested_changes.append(change)
        
        return {
            'changes': suggested_changes,
            'total_recommendations': len(recommendations),
            'applied_count': sum(1 for c in suggested_changes if c['applied']),
            'message': 'Preferences adapted based on behavioral patterns' if auto_apply else 'Recommendations generated'
        }
    
    def _apply_recommendation(self, recommendation):
        """Applique une recommandation aux préférences utilisateur"""
        from notifications.models import NotificationPreference
        
        try:
            prefs, created = NotificationPreference.objects.get_or_create(user=self.user)
            
            rec_type = recommendation['type']
            
            if rec_type == 'adjust_severity_threshold':
                # Ajuster le seuil de sévérité
                target = recommendation['target']
                if 'low' in target:
                    prefs.min_severity_web = 'medium'
                elif 'medium' in target:
                    prefs.min_severity_email = 'high'
                
                prefs.save()
                return True
            
            elif rec_type == 'optimize_timing':
                # Activer l'agrégation
                prefs.enable_aggregation = True
                prefs.aggregation_window_minutes = 60  # 1 heure
                prefs.save()
                return True
            
            return False
        
        except Exception as e:
            logger.error(f"Failed to apply recommendation: {e}")
            return False
    
    def predict_engagement(self, notification_params):
        """
        Prédit la probabilité qu'une notification soit lue
        
        Args:
            notification_params: Dict avec paramètres de la notification
            
        Returns:
            Float entre 0-1 (probabilité de lecture)
        """
        patterns = self.analyze_interaction_patterns(lookback_days=30)
        
        # Facteurs d'engagement
        engagement_score = 0.5  # Base 50%
        
        # 1. Type de notification
        notif_type = notification_params.get('notification_type', 'alert')
        read_rates = patterns.get('read_rates_by_type', {})
        
        if notif_type in read_rates:
            type_rate = read_rates[notif_type].get('read_rate', 0.5)
            engagement_score = (engagement_score + type_rate) / 2
        
        # 2. Sévérité
        severity = notification_params.get('severity', 'medium')
        ignored = patterns.get('ignored_severities', {})
        
        if severity in ignored:
            severity_engagement = 1 - ignored[severity].get('ignore_rate', 0.5)
            engagement_score = (engagement_score + severity_engagement) / 2
        
        # 3. Heure d'envoi
        send_hour = notification_params.get('hour', timezone.now().hour)
        preferred_times = patterns.get('preferred_times', {})
        
        if 'most_active_hours' in preferred_times:
            if send_hour in preferred_times['most_active_hours']:
                engagement_score += 0.2
            elif send_hour in preferred_times.get('least_active_hours', []):
                engagement_score -= 0.2
        
        # Normaliser entre 0 et 1
        engagement_score = max(0, min(1, engagement_score))
        
        return round(engagement_score, 2)


class NotificationOptimizer:
    """
    Optimise le timing et le batching des notifications
    """
    
    @staticmethod
    def should_batch_notification(user, notification):
        """
        Détermine si une notification doit être batchée ou envoyée immédiatement
        
        Args:
            user: User instance
            notification: Notification params
            
        Returns:
            Bool
        """
        from notifications.models import NotificationPreference
        
        try:
            prefs = NotificationPreference.objects.get(user=user)
        except NotificationPreference.DoesNotExist:
            return False
        
        # Ne jamais batcher les notifications critiques
        if notification.get('severity') == 'critical':
            return False
        
        # Respecter les préférences d'agrégation
        if not prefs.enable_aggregation:
            return False
        
        # Batcher les notifications de faible sévérité
        if notification.get('severity') in ['low', 'medium']:
            return True
        
        return False
    
    @staticmethod
    def get_optimal_send_time(user):
        """
        Détermine le meilleur moment pour envoyer des notifications batchées
        
        Args:
            user: User instance
            
        Returns:
            datetime object
        """
        learner = BehavioralLearner(user)
        patterns = learner.analyze_interaction_patterns(lookback_days=14)
        
        preferred_times = patterns.get('preferred_times', {})
        
        if 'peak_hour' in preferred_times:
            peak_hour = preferred_times['peak_hour']
            
            # Programmer pour la prochaine heure de pic
            now = timezone.now()
            optimal_time = now.replace(hour=peak_hour, minute=0, second=0, microsecond=0)
            
            # Si l'heure est déjà passée aujourd'hui, programmer pour demain
            if optimal_time <= now:
                optimal_time += timedelta(days=1)
            
            return optimal_time
        
        # Par défaut, 9h le lendemain
        return timezone.now().replace(hour=9, minute=0, second=0, microsecond=0) + timedelta(days=1)
    
    @staticmethod
    def create_digest(user, notifications):
        """
        Crée un digest de notifications groupées
        
        Args:
            user: User instance
            notifications: List de Notification instances
            
        Returns:
            Dict avec le digest
        """
        if not notifications:
            return None
        
        # Grouper par sévérité
        by_severity = defaultdict(list)
        for notif in notifications:
            by_severity[notif.severity].append(notif)
        
        # Grouper par type
        by_type = defaultdict(list)
        for notif in notifications:
            by_type[notif.notification_type].append(notif)
        
        # Créer le résumé
        digest = {
            'user': user.username,
            'period': f"{notifications[0].created_at.strftime('%Y-%m-%d')} to {notifications[-1].created_at.strftime('%Y-%m-%d')}",
            'total_notifications': len(notifications),
            'by_severity': {
                sev: len(notifs) for sev, notifs in by_severity.items()
            },
            'by_type': {
                typ: len(notifs) for typ, notifs in by_type.items()
            },
            'top_alerts': [
                {
                    'title': n.title,
                    'severity': n.severity,
                    'created_at': n.created_at.isoformat()
                }
                for n in sorted(notifications, key=lambda x: ['low', 'medium', 'high', 'critical'].index(x.severity), reverse=True)[:5]
            ],
            'summary': NotificationOptimizer._generate_digest_summary(by_severity, by_type)
        }
        
        return digest
    
    @staticmethod
    def _generate_digest_summary(by_severity, by_type):
        """Génère un résumé textuel du digest"""
        total = sum(len(notifs) for notifs in by_severity.values())
        critical = len(by_severity.get('critical', []))
        high = len(by_severity.get('high', []))
        
        summary = f"You have {total} notifications. "
        
        if critical > 0:
            summary += f"{critical} CRITICAL alerts require immediate attention. "
        
        if high > 0:
            summary += f"{high} high-priority items. "
        
        # Type le plus fréquent
        if by_type:
            most_common = max(by_type.items(), key=lambda x: len(x[1]))
            summary += f"Most notifications are {most_common[0]} ({len(most_common[1])})."
        
        return summary
