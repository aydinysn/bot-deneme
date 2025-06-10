"""
Main Whale Tracker
Tüm whale tracking bileşenlerini yöneten ana sınıf
"""

import logging
import time
import threading
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import json

# Absolute imports
try:
    # Paket içinden çalışıyorsa
    from .whale_api import WhaleAPI
    from .whale_analyzer import WhaleAnalyzer
    from .whale_signals import WhaleSignalGenerator
    from .whale_notifications import WhaleNotifier
    from . import whale_config as config
except ImportError:
    # Standalone çalışıyorsa
    from whale_api import WhaleAPI
    from whale_analyzer import WhaleAnalyzer
    from whale_signals import WhaleSignalGenerator
    from whale_notifications import WhaleNotifier
    import whale_config as config

logger = logging.getLogger(__name__)

class WhaleTracker:
    """
    Ana whale tracking sistemi
    """
    
    def __init__(self):
        # Bileşenleri başlat
        self.api = WhaleAPI()
        self.analyzer = WhaleAnalyzer()
        self.signal_generator = WhaleSignalGenerator()
        self.notifier = WhaleNotifier()
        
        # State variables
        self.is_running = False
        self.monitoring_thread = None
        self.whale_history = []
        self.last_check_time = 0
        
        # Performance metrics
        self.metrics = {
            'total_whales_detected': 0,
            'signals_generated': 0,
            'patterns_detected': 0,
            'notifications_sent': 0,
            'api_calls_made': 0,
            'last_api_health_check': None,
            'uptime_start': datetime.now()
        }
        
        logger.info("Whale Tracker initialized successfully")
    
    def start_monitoring(self):
        """
        Whale monitoring'i başlat
        """
        try:
            if self.is_running:
                logger.warning("Whale monitoring already running")
                return
            
            self.is_running = True
            
            # Monitoring thread'i başlat
            self.monitoring_thread = threading.Thread(
                target=self._monitoring_loop,
                daemon=True
            )
            self.monitoring_thread.start()
            
            logger.info("Whale monitoring started")
            
            # Test notification gönder
            if config.ENABLE_WHALE_NOTIFICATIONS:
                self.notifier.test_notification_system()
            
        except Exception as e:
            logger.error(f"Failed to start whale monitoring: {e}")
            self.is_running = False
    
    def stop_monitoring(self):
        """
        Whale monitoring'i durdur
        """
        try:
            self.is_running = False
            
            if self.monitoring_thread and self.monitoring_thread.is_alive():
                logger.info("Stopping whale monitoring...")
                # Thread'in durmasını bekle
                self.monitoring_thread.join(timeout=10)
            
            logger.info("Whale monitoring stopped")
            
        except Exception as e:
            logger.error(f"Error stopping whale monitoring: {e}")
    
    def _monitoring_loop(self):
        """
        Ana monitoring loop'u
        """
        logger.info("Whale monitoring loop started")
        
        while self.is_running:
            try:
                current_time = time.time()
                
                # Check interval kontrolü
                if current_time - self.last_check_time < config.CHECK_INTERVAL_SECONDS:
                    time.sleep(1)
                    continue
                
                # Whale verilerini al ve analiz et
                self._perform_monitoring_cycle()
                
                self.last_check_time = current_time
                
                # API health check (her 10 dakikada bir)
                if (not self.metrics['last_api_health_check'] or 
                    current_time - self.metrics['last_api_health_check'] > 600):
                    self._check_api_health()
                    self.metrics['last_api_health_check'] = current_time
                
                # Kısa bekleme
                time.sleep(5)
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                time.sleep(30)  # Hata durumunda daha uzun bekle
        
        logger.info("Whale monitoring loop ended")
    
    def _perform_monitoring_cycle(self):
        """
        Tek bir monitoring döngüsünü gerçekleştir
        """
        try:
            # 1. Son whale hareketlerini al
            recent_whales = self._get_recent_whale_movements()
            
            if not recent_whales:
                return
            
            self.metrics['total_whales_detected'] += len(recent_whales)
            self.metrics['api_calls_made'] += 1
            
            # 2. Whale'leri analiz et
            analysis_results = self._analyze_whale_movements(recent_whales)
            
            # 3. Pattern tespiti
            pattern_analysis = self._detect_patterns(recent_whales)
            
            # 4. Sentiment analizi
            sentiment_analysis = self._analyze_sentiment(recent_whales)
            
            # 5. Sinyaller üret
            signals = self._generate_signals(analysis_results, pattern_analysis, sentiment_analysis)
            
            # 6. Bildirimleri gönder
            self._send_notifications(recent_whales, analysis_results, pattern_analysis, signals)
            
            # 7. History'yi güncelle
            self._update_whale_history(recent_whales)
            
            logger.info(f"Monitoring cycle completed: {len(recent_whales)} whales, {len(signals)} signals")
            
        except Exception as e:
            logger.error(f"Error in monitoring cycle: {e}")
    
    def _get_recent_whale_movements(self) -> List[Dict]:
        """
        Son whale hareketlerini al
        """
        try:
            recent_whales = self.api.get_all_recent_whales(hours_back=config.MAX_LOOKBACK_HOURS)
            
            # Yeni whale'leri filtrele (daha önce işlenmeyen)
            processed_hashes = {w.get('hash', '') for w in self.whale_history}
            new_whales = [w for w in recent_whales 
                         if w.get('data', {}).get('hash', '') not in processed_hashes]
            
            return new_whales
            
        except Exception as e:
            logger.error(f"Error getting whale movements: {e}")
            return []
    
    def _analyze_whale_movements(self, whale_list: List[Dict]) -> Dict:
        """
        Whale hareketlerini analiz et
        """
        try:
            if not whale_list:
                return {}
            
            # Her whale'i tek tek analiz et
            whale_data_list = [w.get('data', {}) for w in whale_list]
            
            # Multiple whale analizi
            analysis_results = self.analyzer.analyze_multiple_whales(whale_data_list)
            
            return analysis_results
            
        except Exception as e:
            logger.error(f"Error analyzing whale movements: {e}")
            return {}
    
    def _detect_patterns(self, whale_list: List[Dict]) -> Dict:
        """
        Whale hareketlerinde pattern tespit et
        """
        try:
            whale_data_list = [w.get('data', {}) for w in whale_list]
            
            # Son 24 saatteki tüm whale history'yi kullan
            all_whale_data = whale_data_list + [w.get('data', {}) for w in self.whale_history[-100:]]
            
            pattern_analysis = self.analyzer.detect_whale_patterns(
                all_whale_data, 
                hours_lookback=24
            )
            
            if pattern_analysis.get('pattern_confidence', 0) > 0.6:
                self.metrics['patterns_detected'] += 1
            
            return pattern_analysis
            
        except Exception as e:
            logger.error(f"Error detecting patterns: {e}")
            return {}
    
    def _analyze_sentiment(self, whale_list: List[Dict]) -> Dict:
        """
        Whale sentiment analizi
        """
        try:
            whale_data_list = [w.get('data', {}) for w in whale_list]
            
            sentiment_analysis = self.analyzer.get_whale_sentiment(whale_data_list)
            
            return sentiment_analysis
            
        except Exception as e:
            logger.error(f"Error analyzing sentiment: {e}")
            return {}
    
    def _generate_signals(self, analysis_results: Dict, pattern_analysis: Dict, sentiment_analysis: Dict) -> List[Dict]:
        """
        Analiz sonuçlarından sinyaller üret
        """
        try:
            all_signals = []
            
            # Ana analiz sinyalleri
            if analysis_results and config.GENERATE_SIGNALS:
                signals = self.signal_generator.generate_signals(analysis_results)
                all_signals.extend(signals)
            
            # Pattern sinyalleri
            if pattern_analysis and pattern_analysis.get('pattern_confidence', 0) > 0.6:
                pattern_signals = self.signal_generator.generate_pattern_signals(pattern_analysis)
                all_signals.extend(pattern_signals)
            
            # Sentiment sinyalleri
            if sentiment_analysis and sentiment_analysis.get('confidence', 0) > 0.6:
                sentiment_signals = self.signal_generator.generate_sentiment_signals(sentiment_analysis)
                all_signals.extend(sentiment_signals)
            
            self.metrics['signals_generated'] += len(all_signals)
            
            return all_signals
            
        except Exception as e:
            logger.error(f"Error generating signals: {e}")
            return []
    
    def _send_notifications(self, whale_list: List[Dict], analysis_results: Dict, 
                          pattern_analysis: Dict, signals: List[Dict]):
        """
        Bildirimleri gönder
        """
        try:
            # Whale movement bildirimleri
            for whale in whale_list:
                whale_data = whale.get('data', {})
                individual_analysis = self.analyzer.analyze_whale_movement(whale_data)
                
                self.notifier.notify_whale_movement(whale_data, individual_analysis)
                self.metrics['notifications_sent'] += 1
            
            # Pattern bildirimleri
            if (pattern_analysis and pattern_analysis.get('pattern_confidence', 0) > 0.7):
                self.notifier.notify_pattern_detected(pattern_analysis)
                self.metrics['notifications_sent'] += 1
            
            # Signal bildirimleri
            if signals:
                strong_signals = [s for s in signals if s.get('strength') in ['STRONG', 'VERY_STRONG']]
                if strong_signals:
                    self.notifier.notify_signal_generated(strong_signals)
                    self.metrics['notifications_sent'] += 1
            
        except Exception as e:
            logger.error(f"Error sending notifications: {e}")
    
    def _update_whale_history(self, new_whales: List[Dict]):
        """
        Whale history'yi güncelle
        """
        try:
            self.whale_history.extend(new_whales)
            
            # History limitini kontrol et
            if len(self.whale_history) > 1000:
                self.whale_history = self.whale_history[-500:]  # Son 500'ü tut
            
        except Exception as e:
            logger.error(f"Error updating whale history: {e}")
    
    def _check_api_health(self):
        """
        API'lerin sağlığını kontrol et
        """
        try:
            health_status = self.api.health_check()
            
            if not health_status.get('overall', False):
                logger.warning("API health check failed")
                
                # Market alert gönder
                self.notifier.notify_market_alert('api_health_issue', {
                    'health_status': health_status,
                    'timestamp': datetime.now().isoformat()
                })
            else:
                logger.debug("API health check passed")
            
        except Exception as e:
            logger.error(f"API health check error: {e}")
    
    # Public methods
    
    def get_active_signals(self, symbol: str = None) -> List[Dict]:
        """
        Aktif sinyalleri al
        """
        return self.signal_generator.get_active_signals(symbol)
    
    def get_recent_whales(self, hours_back: int = 6, limit: int = 20) -> List[Dict]:
        """
        Son whale hareketlerini al
        """
        try:
            cutoff_time = datetime.now().timestamp() - (hours_back * 3600)
            
            recent_whales = []
            for whale in reversed(self.whale_history):  # En yeni önce
                whale_data = whale.get('data', {})
                whale_time = whale_data.get('timestamp', 0)
                
                if whale_time >= cutoff_time:
                    recent_whales.append(whale_data)
                    
                    if len(recent_whales) >= limit:
                        break
            
            return recent_whales
            
        except Exception as e:
            logger.error(f"Error getting recent whales: {e}")
            return []
    
    def get_whale_summary(self) -> Dict:
        """
        Whale tracking özeti
        """
        try:
            recent_whales = self.get_recent_whales(hours_back=24)
            active_signals = self.get_active_signals()
            
            # Coin bazında istatistikler
            coin_stats = {}
            for whale in recent_whales:
                symbol = whale.get('symbol', 'UNKNOWN')
                if symbol not in coin_stats:
                    coin_stats[symbol] = {
                        'count': 0,
                        'total_volume_usd': 0,
                        'avg_volume_usd': 0
                    }
                
                coin_stats[symbol]['count'] += 1
                volume = whale.get('amount_usd', 0)
                coin_stats[symbol]['total_volume_usd'] += volume
            
            # Average hesapla
            for symbol, stats in coin_stats.items():
                if stats['count'] > 0:
                    stats['avg_volume_usd'] = stats['total_volume_usd'] / stats['count']
            
            # Signal istatistikleri
            signal_stats = {
                'bullish': len([s for s in active_signals if s.get('signal_type') == 'BULLISH']),
                'bearish': len([s for s in active_signals if s.get('signal_type') == 'BEARISH']),
                'neutral': len([s for s in active_signals if s.get('signal_type') == 'NEUTRAL'])
            }
            
            summary = {
                'status': 'RUNNING' if self.is_running else 'STOPPED',
                'uptime_hours': (datetime.now() - self.metrics['uptime_start']).total_seconds() / 3600,
                'whale_stats': {
                    'total_24h': len(recent_whales),
                    'by_coin': coin_stats
                },
                'signal_stats': signal_stats,
                'active_signals_count': len(active_signals),
                'performance_metrics': self.metrics.copy(),
                'last_update': datetime.now().isoformat()
            }
            
            return summary
            
        except Exception as e:
            logger.error(f"Error getting whale summary: {e}")
            return {'error': str(e)}
    
    def manual_scan(self) -> Dict:
        """
        Manuel whale tarama
        """
        try:
            logger.info("Starting manual whale scan...")
            
            # Zorunlu tarama yap
            self._perform_monitoring_cycle()
            
            # Sonuçları döndür
            summary = self.get_whale_summary()
            summary['scan_type'] = 'manual'
            summary['scan_time'] = datetime.now().isoformat()
            
            logger.info("Manual whale scan completed")
            return summary
            
        except Exception as e:
            logger.error(f"Manual scan error: {e}")
            return {'error': str(e)}
    
    def get_whale_analytics(self, hours_back: int = 24) -> Dict:
        """
        Detaylı whale analitikleri
        """
        try:
            recent_whales = self.get_recent_whales(hours_back=hours_back, limit=100)
            
            if not recent_whales:
                return {'no_data': True}
            
            # Analiz et
            analysis = self.analyzer.analyze_multiple_whales(recent_whales)
            patterns = self.analyzer.detect_whale_patterns(recent_whales, hours_back)
            sentiment = self.analyzer.get_whale_sentiment(recent_whales)
            
            # Exchange akışları
            exchange_flows = {}
            for whale in recent_whales:
                from_addr = whale.get('from', '')
                to_addr = whale.get('to', '')
                amount_usd = whale.get('amount_usd', 0)
                
                # Exchange detection (basit)
                for exchange in config.MAJOR_EXCHANGES:
                    if exchange in to_addr.lower():
                        if exchange not in exchange_flows:
                            exchange_flows[exchange] = {'inflow': 0, 'outflow': 0}
                        exchange_flows[exchange]['inflow'] += amount_usd
                    
                    if exchange in from_addr.lower():
                        if exchange not in exchange_flows:
                            exchange_flows[exchange] = {'inflow': 0, 'outflow': 0}
                        exchange_flows[exchange]['outflow'] += amount_usd
            
            analytics = {
                'time_range_hours': hours_back,
                'total_whales': len(recent_whales),
                'total_volume_usd': sum(w.get('amount_usd', 0) for w in recent_whales),
                'avg_volume_usd': sum(w.get('amount_usd', 0) for w in recent_whales) / len(recent_whales),
                'analysis': analysis,
                'patterns': patterns,
                'sentiment': sentiment,
                'exchange_flows': exchange_flows,
                'generated_at': datetime.now().isoformat()
            }
            
            return analytics
            
        except Exception as e:
            logger.error(f"Error getting whale analytics: {e}")
            return {'error': str(e)}
    
    def export_data(self, filepath: str = None) -> str:
        """
        Whale tracker verilerini export et
        """
        try:
            export_data = {
                'whale_history': self.whale_history[-100:],  # Son 100 whale
                'active_signals': self.get_active_signals(),
                'metrics': self.metrics,
                'summary': self.get_whale_summary(),
                'export_timestamp': datetime.now().isoformat()
            }
            
            if filepath:
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(export_data, f, indent=2, ensure_ascii=False)
                return filepath
            else:
                return json.dumps(export_data, indent=2, ensure_ascii=False)
            
        except Exception as e:
            logger.error(f"Export data error: {e}")
            return "{}"
    
    def cleanup(self):
        """
        Eski verileri temizle
        """
        try:
            # Eski sinyalleri temizle
            self.signal_generator.cleanup_old_signals(days_back=7)
            
            # Whale history temizle (30 günden eski)
            cutoff_time = datetime.now().timestamp() - (30 * 24 * 3600)
            self.whale_history = [
                w for w in self.whale_history
                if w.get('data', {}).get('timestamp', 0) >= cutoff_time
            ]
            
            logger.info("Whale tracker cleanup completed")
            
        except Exception as e:
            logger.error(f"Cleanup error: {e}") 