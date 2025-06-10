"""
Whale Signal Generator
Whale hareketlerinden trading sinyalleri üretir
"""

import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import json
from collections import defaultdict

try:
    from . import whale_config as config
except ImportError:
    import whale_config as config

logger = logging.getLogger(__name__)

class WhaleSignalGenerator:
    """
    Whale hareketlerinden trading sinyalleri üretir
    """
    
    def __init__(self):
        self.active_signals = {}
        self.signal_history = []
        self.last_signal_times = defaultdict(float)
        
    def generate_signals(self, whale_analysis: Dict) -> List[Dict]:
        """
        Whale analizinden trading sinyalleri üret
        """
        try:
            signals = []
            current_time = datetime.now()
            
            # Coin bazında sinyaller
            coin_signals = whale_analysis.get('coin_signals', {})
            
            for symbol, signal_data in coin_signals.items():
                # Minimum güven skoru kontrol
                if signal_data['confidence'] < config.SIGNAL_CONFIDENCE_THRESHOLD:
                    continue
                
                # Son sinyal zamanı kontrol (rate limiting)
                last_signal_time = self.last_signal_times.get(symbol, 0)
                if current_time.timestamp() - last_signal_time < config.MIN_SIGNAL_INTERVAL:
                    continue
                
                # Signal oluştur
                signal = self._create_signal(
                    symbol=symbol,
                    signal_type=signal_data['signal'],
                    confidence=signal_data['confidence'],
                    source='whale_movement'
                )
                
                if signal:
                    signals.append(signal)
                    self.last_signal_times[symbol] = current_time.timestamp()
            
            # Market genel sinyali
            market_signal = whale_analysis.get('market_signal', {})
            if (market_signal.get('confidence', 0) >= config.SIGNAL_CONFIDENCE_THRESHOLD and
                market_signal.get('signal') != 'NEUTRAL'):
                
                market_wide_signal = self._create_market_signal(market_signal)
                if market_wide_signal:
                    signals.append(market_wide_signal)
            
            # Sinyalleri kaydet
            for signal in signals:
                self._save_signal(signal)
            
            return signals
            
        except Exception as e:
            logger.error(f"Signal generation error: {e}")
            return []
    
    def generate_pattern_signals(self, pattern_analysis: Dict) -> List[Dict]:
        """
        Pattern analizinden sinyaller üret
        """
        try:
            signals = []
            
            if pattern_analysis.get('pattern_confidence', 0) < 0.6:
                return signals
            
            current_time = datetime.now()
            
            # Accumulation pattern
            if pattern_analysis.get('accumulation_pattern'):
                signal = self._create_signal(
                    symbol='MARKET',
                    signal_type='BULLISH',
                    confidence=pattern_analysis['pattern_confidence'],
                    source='accumulation_pattern',
                    description='Whale accumulation pattern detected'
                )
                signals.append(signal)
            
            # Distribution pattern
            if pattern_analysis.get('distribution_pattern'):
                signal = self._create_signal(
                    symbol='MARKET',
                    signal_type='BEARISH',
                    confidence=pattern_analysis['pattern_confidence'],
                    source='distribution_pattern',
                    description='Whale distribution pattern detected'
                )
                signals.append(signal)
            
            # Exchange exodus
            if pattern_analysis.get('exchange_exodus'):
                signal = self._create_signal(
                    symbol='MARKET',
                    signal_type='BULLISH',
                    confidence=pattern_analysis['pattern_confidence'],
                    source='exchange_exodus',
                    description='Large exchange outflows detected'
                )
                signals.append(signal)
            
            # Coordinated selling
            if pattern_analysis.get('coordinated_selling'):
                signal = self._create_signal(
                    symbol='MARKET',
                    signal_type='BEARISH',
                    confidence=pattern_analysis['pattern_confidence'],
                    source='coordinated_selling',
                    description='Coordinated whale selling detected'
                )
                signals.append(signal)
            
            for signal in signals:
                self._save_signal(signal)
            
            return signals
            
        except Exception as e:
            logger.error(f"Pattern signal generation error: {e}")
            return []
    
    def generate_sentiment_signals(self, sentiment_analysis: Dict) -> List[Dict]:
        """
        Sentiment analizinden sinyaller üret
        """
        try:
            signals = []
            
            overall_sentiment = sentiment_analysis.get('overall_sentiment', 'NEUTRAL')
            confidence = sentiment_analysis.get('confidence', 0)
            
            if confidence < config.SIGNAL_CONFIDENCE_THRESHOLD or overall_sentiment == 'NEUTRAL':
                return signals
            
            signal = self._create_signal(
                symbol='MARKET',
                signal_type=overall_sentiment,
                confidence=confidence,
                source='whale_sentiment',
                description=f'Whale sentiment: {overall_sentiment.lower()}'
            )
            
            if signal:
                signals.append(signal)
                self._save_signal(signal)
            
            return signals
            
        except Exception as e:
            logger.error(f"Sentiment signal generation error: {e}")
            return []
    
    def _create_signal(self, 
                      symbol: str,
                      signal_type: str,
                      confidence: float,
                      source: str,
                      description: str = None) -> Optional[Dict]:
        """
        Tek bir sinyal oluştur
        """
        try:
            current_time = datetime.now()
            expiry_time = current_time + timedelta(hours=config.SIGNAL_DECAY_HOURS)
            
            signal = {
                'id': f"whale_{symbol}_{int(current_time.timestamp())}",
                'symbol': symbol,
                'signal_type': signal_type,
                'confidence': confidence,
                'source': source,
                'description': description or f"Whale {signal_type.lower()} signal for {symbol}",
                'timestamp': current_time.isoformat(),
                'expiry': expiry_time.isoformat(),
                'status': 'ACTIVE',
                'strength': self._calculate_signal_strength(confidence),
                'recommended_action': self._get_recommended_action(signal_type, confidence),
                'risk_level': self._get_risk_level(confidence),
                'metadata': {
                    'whale_source': True,
                    'auto_generated': True,
                    'algorithm_version': '1.0'
                }
            }
            
            return signal
            
        except Exception as e:
            logger.error(f"Signal creation error: {e}")
            return None
    
    def _create_market_signal(self, market_data: Dict) -> Optional[Dict]:
        """
        Market geneli sinyal oluştur
        """
        try:
            signal_type = market_data.get('signal', 'NEUTRAL')
            confidence = market_data.get('confidence', 0)
            
            if signal_type == 'NEUTRAL':
                return None
            
            current_time = datetime.now()
            
            signal = {
                'id': f"whale_market_{int(current_time.timestamp())}",
                'symbol': 'MARKET',
                'signal_type': signal_type,
                'confidence': confidence,
                'source': 'whale_market_analysis',
                'description': f'Market-wide whale {signal_type.lower()} signal',
                'timestamp': current_time.isoformat(),
                'expiry': (current_time + timedelta(hours=config.SIGNAL_DECAY_HOURS)).isoformat(),
                'status': 'ACTIVE',
                'strength': self._calculate_signal_strength(confidence),
                'recommended_action': self._get_market_action(signal_type, confidence),
                'risk_level': self._get_risk_level(confidence),
                'metadata': {
                    'whale_source': True,
                    'market_wide': True,
                    'auto_generated': True
                }
            }
            
            return signal
            
        except Exception as e:
            logger.error(f"Market signal creation error: {e}")
            return None
    
    def _calculate_signal_strength(self, confidence: float) -> str:
        """
        Güven skorundan sinyal gücü hesapla
        """
        if confidence >= 0.8:
            return 'VERY_STRONG'
        elif confidence >= 0.7:
            return 'STRONG'
        elif confidence >= 0.6:
            return 'MODERATE'
        elif confidence >= 0.4:
            return 'WEAK'
        else:
            return 'VERY_WEAK'
    
    def _get_recommended_action(self, signal_type: str, confidence: float) -> Dict:
        """
        Sinyal tipine göre önerilen aksiyonlar
        """
        actions = {
            'BULLISH': {
                'primary': 'BUY' if confidence > 0.7 else 'CONSIDER_BUY',
                'secondary': 'HOLD_LONG',
                'risk_management': 'SET_STOP_LOSS',
                'position_size': 'MODERATE' if confidence > 0.7 else 'SMALL'
            },
            'BEARISH': {
                'primary': 'SELL' if confidence > 0.7 else 'CONSIDER_SELL',
                'secondary': 'AVOID_LONG',
                'risk_management': 'TAKE_PROFIT',
                'position_size': 'MODERATE' if confidence > 0.7 else 'SMALL'
            },
            'NEUTRAL': {
                'primary': 'HOLD',
                'secondary': 'WAIT',
                'risk_management': 'MAINTAIN_POSITIONS',
                'position_size': 'CURRENT'
            }
        }
        
        return actions.get(signal_type, actions['NEUTRAL'])
    
    def _get_market_action(self, signal_type: str, confidence: float) -> Dict:
        """
        Market sinyali için önerilen aksiyonlar
        """
        actions = {
            'BULLISH': {
                'primary': 'INCREASE_EXPOSURE',
                'secondary': 'BUY_DIPS',
                'risk_management': 'REDUCE_SHORTS',
                'portfolio_allocation': 'INCREASE_CRYPTO_ALLOCATION'
            },
            'BEARISH': {
                'primary': 'REDUCE_EXPOSURE',
                'secondary': 'TAKE_PROFITS',
                'risk_management': 'INCREASE_CASH',
                'portfolio_allocation': 'DECREASE_CRYPTO_ALLOCATION'
            }
        }
        
        return actions.get(signal_type, {})
    
    def _get_risk_level(self, confidence: float) -> str:
        """
        Güven skorundan risk seviyesi hesapla
        """
        if confidence >= 0.8:
            return 'LOW'
        elif confidence >= 0.6:
            return 'MEDIUM'
        else:
            return 'HIGH'
    
    def _save_signal(self, signal: Dict):
        """
        Sinyali kaydet
        """
        try:
            # Active signals dict'e ekle
            self.active_signals[signal['id']] = signal
            
            # History'e ekle
            self.signal_history.append(signal)
            
            # History limitini kontrol et
            if len(self.signal_history) > 1000:
                self.signal_history = self.signal_history[-500:]  # Son 500'ü tut
            
            logger.info(f"Signal saved: {signal['id']} - {signal['symbol']} {signal['signal_type']}")
            
        except Exception as e:
            logger.error(f"Signal save error: {e}")
    
    def get_active_signals(self, symbol: str = None) -> List[Dict]:
        """
        Aktif sinyalleri al
        """
        try:
            current_time = datetime.now()
            active_signals = []
            
            for signal_id, signal in self.active_signals.items():
                # Expired signals'ı kontrol et
                expiry_time = datetime.fromisoformat(signal['expiry'].replace('Z', '+00:00'))
                
                if expiry_time.replace(tzinfo=None) > current_time:
                    if symbol is None or signal['symbol'] == symbol:
                        active_signals.append(signal)
                else:
                    # Expired signal'ı kaldır
                    signal['status'] = 'EXPIRED'
            
            # Expired sinyalleri temizle
            self.active_signals = {
                sid: sig for sid, sig in self.active_signals.items()
                if datetime.fromisoformat(sig['expiry'].replace('Z', '+00:00')).replace(tzinfo=None) > current_time
            }
            
            return active_signals
            
        except Exception as e:
            logger.error(f"Get active signals error: {e}")
            return []
    
    def get_signal_history(self, 
                          symbol: str = None,
                          hours_back: int = 24,
                          limit: int = 50) -> List[Dict]:
        """
        Sinyal geçmişini al
        """
        try:
            cutoff_time = datetime.now() - timedelta(hours=hours_back)
            
            filtered_signals = []
            
            for signal in reversed(self.signal_history):  # En yeni önce
                signal_time = datetime.fromisoformat(signal['timestamp'].replace('Z', '+00:00'))
                
                if signal_time.replace(tzinfo=None) >= cutoff_time:
                    if symbol is None or signal['symbol'] == symbol:
                        filtered_signals.append(signal)
                        
                        if len(filtered_signals) >= limit:
                            break
            
            return filtered_signals
            
        except Exception as e:
            logger.error(f"Get signal history error: {e}")
            return []
    
    def cancel_signal(self, signal_id: str) -> bool:
        """
        Bir sinyali iptal et
        """
        try:
            if signal_id in self.active_signals:
                self.active_signals[signal_id]['status'] = 'CANCELLED'
                del self.active_signals[signal_id]
                logger.info(f"Signal cancelled: {signal_id}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Cancel signal error: {e}")
            return False
    
    def get_signal_performance(self, hours_back: int = 24) -> Dict:
        """
        Sinyal performansını analiz et
        """
        try:
            recent_signals = self.get_signal_history(hours_back=hours_back, limit=100)
            
            if not recent_signals:
                return {'total_signals': 0}
            
            performance = {
                'total_signals': len(recent_signals),
                'bullish_signals': 0,
                'bearish_signals': 0,
                'neutral_signals': 0,
                'avg_confidence': 0.0,
                'strength_distribution': defaultdict(int),
                'source_distribution': defaultdict(int),
                'symbol_distribution': defaultdict(int)
            }
            
            total_confidence = 0
            
            for signal in recent_signals:
                signal_type = signal.get('signal_type', 'NEUTRAL')
                
                if signal_type == 'BULLISH':
                    performance['bullish_signals'] += 1
                elif signal_type == 'BEARISH':
                    performance['bearish_signals'] += 1
                else:
                    performance['neutral_signals'] += 1
                
                confidence = signal.get('confidence', 0)
                total_confidence += confidence
                
                strength = signal.get('strength', 'UNKNOWN')
                performance['strength_distribution'][strength] += 1
                
                source = signal.get('source', 'UNKNOWN')
                performance['source_distribution'][source] += 1
                
                symbol = signal.get('symbol', 'UNKNOWN')
                performance['symbol_distribution'][symbol] += 1
            
            performance['avg_confidence'] = total_confidence / len(recent_signals)
            
            return performance
            
        except Exception as e:
            logger.error(f"Signal performance analysis error: {e}")
            return {'total_signals': 0, 'error': str(e)}
    
    def cleanup_old_signals(self, days_back: int = 7):
        """
        Eski sinyalleri temizle
        """
        try:
            cutoff_time = datetime.now() - timedelta(days=days_back)
            
            # History'den eski sinyalleri kaldır
            self.signal_history = [
                signal for signal in self.signal_history
                if datetime.fromisoformat(signal['timestamp'].replace('Z', '+00:00')).replace(tzinfo=None) >= cutoff_time
            ]
            
            # Active signals'dan expired olanları kaldır (zaten yapılıyor ama kontrol)
            current_time = datetime.now()
            self.active_signals = {
                sid: sig for sid, sig in self.active_signals.items()
                if datetime.fromisoformat(sig['expiry'].replace('Z', '+00:00')).replace(tzinfo=None) > current_time
            }
            
            logger.info(f"Cleaned up signals older than {days_back} days")
            
        except Exception as e:
            logger.error(f"Signal cleanup error: {e}")
    
    def export_signals(self, filepath: str = None) -> str:
        """
        Sinyalleri JSON formatında export et
        """
        try:
            export_data = {
                'active_signals': list(self.active_signals.values()),
                'signal_history': self.signal_history[-100:],  # Son 100 sinyal
                'export_timestamp': datetime.now().isoformat(),
                'total_active': len(self.active_signals),
                'total_history': len(self.signal_history)
            }
            
            if filepath:
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(export_data, f, indent=2, ensure_ascii=False)
                return filepath
            else:
                return json.dumps(export_data, indent=2, ensure_ascii=False)
            
        except Exception as e:
            logger.error(f"Signal export error: {e}")
            return "{}" 