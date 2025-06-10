"""
Whale Analyzer
Whale hareketlerini analiz eder ve trading sinyalleri üretir
"""

import logging
from datetime import datetime, timedelta
from typing import List, Dict, Tuple, Optional
import numpy as np
from collections import defaultdict, Counter
import json

try:
    from . import whale_config as config
except ImportError:
    import whale_config as config

logger = logging.getLogger(__name__)

class WhaleAnalyzer:
    """
    Whale hareketlerini analiz eden sınıf
    """
    
    def __init__(self):
        self.recent_whales = []
        self.signal_history = {}
        self.confidence_scores = {}
        self.exchange_flows = defaultdict(list)
        
    def analyze_whale_movement(self, whale_data: Dict) -> Dict:
        """
        Tek bir whale hareketini analiz et
        """
        try:
            analysis = {
                'signal_type': None,
                'strength': 'MINOR',
                'confidence': 0.0,
                'direction': None,
                'impact_prediction': None,
                'reasoning': []
            }
            
            # Veri çıkarma
            amount_usd = whale_data.get('amount_usd', 0)
            symbol = whale_data.get('symbol', '').upper()
            from_addr = whale_data.get('from', '')
            to_addr = whale_data.get('to', '')
            timestamp = whale_data.get('timestamp', 0)
            
            reasoning = []
            confidence = 0.0
            
            # 1. Transfer büyüklüğü analizi
            if amount_usd >= config.SIGNAL_STRENGTH['EXTREME']:
                analysis['strength'] = 'EXTREME'
                confidence += 0.4
                reasoning.append(f"Çok büyük transfer: ${amount_usd:,.0f}")
            elif amount_usd >= config.SIGNAL_STRENGTH['MAJOR']:
                analysis['strength'] = 'MAJOR'
                confidence += 0.3
                reasoning.append(f"Büyük transfer: ${amount_usd:,.0f}")
            elif amount_usd >= config.SIGNAL_STRENGTH['MODERATE']:
                analysis['strength'] = 'MODERATE'
                confidence += 0.2
                reasoning.append(f"Orta büyüklük transfer: ${amount_usd:,.0f}")
            else:
                analysis['strength'] = 'MINOR'
                confidence += 0.1
                reasoning.append(f"Küçük transfer: ${amount_usd:,.0f}")
            
            # 2. Exchange analizi
            from_exchange = self._get_exchange_name(from_addr)
            to_exchange = self._get_exchange_name(to_addr)
            
            if from_exchange and not to_exchange:
                # Exchange'den çıkış = BULLISH (institutionlar accumulate ediyor)
                analysis['signal_type'] = 'BULLISH'
                analysis['direction'] = 'UP'
                confidence += 0.2
                reasoning.append(f"{from_exchange}'den withdrawal - Bullish signal")
                
            elif not from_exchange and to_exchange:
                # Exchange'e giriş = BEARISH (satış hazırlığı)
                analysis['signal_type'] = 'BEARISH'
                analysis['direction'] = 'DOWN'
                confidence += 0.3
                reasoning.append(f"{to_exchange}'e deposit - Bearish signal")
                
            elif from_exchange and to_exchange:
                # Exchange arası transfer - nötr
                analysis['signal_type'] = 'NEUTRAL'
                confidence += 0.1
                reasoning.append(f"Exchange arası transfer: {from_exchange} → {to_exchange}")
                
            else:
                # Wallet to wallet - belirsiz
                analysis['signal_type'] = 'UNCERTAIN'
                confidence += 0.05
                reasoning.append("Wallet to wallet transfer - belirsiz")
            
            # 3. Timing analizi
            current_time = datetime.now().timestamp()
            hours_since = (current_time - timestamp) / 3600
            
            if hours_since < 1:
                confidence += 0.1
                reasoning.append("Çok yeni transfer (< 1 saat)")
            elif hours_since < 6:
                confidence += 0.05
                reasoning.append("Yeni transfer (< 6 saat)")
            
            # 4. Coin spesifik analiz
            coin_multiplier = self._get_coin_impact_multiplier(symbol)
            confidence *= coin_multiplier
            
            if coin_multiplier > 1:
                reasoning.append(f"{symbol} yüksek impact coin")
            
            analysis['confidence'] = min(confidence, 1.0)
            analysis['reasoning'] = reasoning
            
            # Impact prediction
            if analysis['confidence'] > 0.7:
                analysis['impact_prediction'] = 'HIGH'
            elif analysis['confidence'] > 0.4:
                analysis['impact_prediction'] = 'MEDIUM'
            else:
                analysis['impact_prediction'] = 'LOW'
            
            return analysis
            
        except Exception as e:
            logger.error(f"Whale movement analysis error: {e}")
            return {
                'signal_type': 'ERROR',
                'strength': 'MINOR',
                'confidence': 0.0,
                'direction': None,
                'impact_prediction': 'LOW',
                'reasoning': [f"Analysis error: {str(e)}"]
            }
    
    def analyze_multiple_whales(self, whale_list: List[Dict]) -> Dict:
        """
        Birden fazla whale hareketini toplu analiz et
        """
        try:
            if not whale_list:
                return {'overall_signal': 'NEUTRAL', 'confidence': 0.0}
            
            # Coin bazında grupla
            coin_signals = defaultdict(list)
            
            for whale in whale_list:
                symbol = whale.get('symbol', '').upper()
                analysis = self.analyze_whale_movement(whale)
                coin_signals[symbol].append(analysis)
            
            # Her coin için overall signal hesapla
            coin_overall = {}
            
            for symbol, signals in coin_signals.items():
                overall = self._calculate_overall_signal(signals)
                coin_overall[symbol] = overall
            
            # Genel market signal
            market_signal = self._calculate_market_signal(coin_overall)
            
            return {
                'coin_signals': coin_overall,
                'market_signal': market_signal,
                'analysis_timestamp': datetime.now().isoformat(),
                'whales_analyzed': len(whale_list)
            }
            
        except Exception as e:
            logger.error(f"Multiple whale analysis error: {e}")
            return {'overall_signal': 'ERROR', 'confidence': 0.0}
    
    def detect_whale_patterns(self, whale_history: List[Dict], 
                            hours_lookback: int = 24) -> Dict:
        """
        Whale hareketlerinde pattern tespit et
        """
        try:
            patterns = {
                'accumulation_pattern': False,
                'distribution_pattern': False,
                'exchange_exodus': False,
                'whale_rotation': False,
                'coordinated_selling': False,
                'pattern_confidence': 0.0
            }
            
            if not whale_history:
                return patterns
            
            # Son X saatteki hareketleri filtrele
            cutoff_time = datetime.now().timestamp() - (hours_lookback * 3600)
            recent_whales = [w for w in whale_history 
                           if w.get('timestamp', 0) > cutoff_time]
            
            if len(recent_whales) < 3:
                return patterns
            
            # Exchange akışlarını analiz et
            exchange_flows = self._analyze_exchange_flows(recent_whales)
            
            # 1. Accumulation Pattern (exchange'lerden çıkış)
            total_outflow = sum(exchange_flows['outflows'].values())
            total_inflow = sum(exchange_flows['inflows'].values())
            
            if total_outflow > total_inflow * 2:
                patterns['accumulation_pattern'] = True
                patterns['pattern_confidence'] += 0.3
            
            # 2. Distribution Pattern (exchange'lere giriş)
            if total_inflow > total_outflow * 2:
                patterns['distribution_pattern'] = True
                patterns['pattern_confidence'] += 0.3
            
            # 3. Exchange Exodus (büyük çıkışlar)
            large_outflows = [w for w in recent_whales 
                            if w.get('amount_usd', 0) > 10000000 and 
                            self._get_exchange_name(w.get('from', ''))]
            
            if len(large_outflows) >= 3:
                patterns['exchange_exodus'] = True
                patterns['pattern_confidence'] += 0.4
            
            # 4. Koordineli satış
            large_deposits = [w for w in recent_whales 
                            if w.get('amount_usd', 0) > 5000000 and 
                            self._get_exchange_name(w.get('to', ''))]
            
            if len(large_deposits) >= 4:
                patterns['coordinated_selling'] = True
                patterns['pattern_confidence'] += 0.4
            
            # 5. Whale rotation (farklı coinler arası hareket)
            coin_counts = Counter([w.get('symbol', '') for w in recent_whales])
            if len(coin_counts) > 5 and max(coin_counts.values()) < len(recent_whales) * 0.4:
                patterns['whale_rotation'] = True
                patterns['pattern_confidence'] += 0.2
            
            patterns['pattern_confidence'] = min(patterns['pattern_confidence'], 1.0)
            
            return patterns
            
        except Exception as e:
            logger.error(f"Pattern detection error: {e}")
            return {'pattern_confidence': 0.0}
    
    def get_whale_sentiment(self, whale_data: List[Dict]) -> Dict:
        """
        Whale hareketlerinden sentiment analizi
        """
        try:
            sentiment = {
                'bullish_score': 0.0,
                'bearish_score': 0.0,
                'neutral_score': 0.0,
                'overall_sentiment': 'NEUTRAL',
                'confidence': 0.0
            }
            
            if not whale_data:
                return sentiment
            
            bullish_weight = 0
            bearish_weight = 0
            neutral_weight = 0
            total_weight = 0
            
            for whale in whale_data:
                analysis = self.analyze_whale_movement(whale)
                weight = whale.get('amount_usd', 0) / 1000000  # Million USD units
                
                if analysis['signal_type'] == 'BULLISH':
                    bullish_weight += weight * analysis['confidence']
                elif analysis['signal_type'] == 'BEARISH':
                    bearish_weight += weight * analysis['confidence']
                else:
                    neutral_weight += weight * 0.5
                
                total_weight += weight
            
            if total_weight > 0:
                sentiment['bullish_score'] = bullish_weight / total_weight
                sentiment['bearish_score'] = bearish_weight / total_weight
                sentiment['neutral_score'] = neutral_weight / total_weight
                
                # Overall sentiment
                if sentiment['bullish_score'] > sentiment['bearish_score'] * 1.5:
                    sentiment['overall_sentiment'] = 'BULLISH'
                    sentiment['confidence'] = sentiment['bullish_score']
                elif sentiment['bearish_score'] > sentiment['bullish_score'] * 1.5:
                    sentiment['overall_sentiment'] = 'BEARISH'
                    sentiment['confidence'] = sentiment['bearish_score']
                else:
                    sentiment['overall_sentiment'] = 'NEUTRAL'
                    sentiment['confidence'] = max(sentiment['neutral_score'], 0.3)
            
            return sentiment
            
        except Exception as e:
            logger.error(f"Sentiment analysis error: {e}")
            return {'overall_sentiment': 'ERROR', 'confidence': 0.0}
    
    def _get_exchange_name(self, address: str) -> Optional[str]:
        """Exchange adresini kontrol et"""
        if not address or address == 'unknown':
            return None
        
        # Basit exchange detection
        for exchange in config.MAJOR_EXCHANGES:
            if exchange.lower() in address.lower():
                return exchange
        
        return None
    
    def _get_coin_impact_multiplier(self, symbol: str) -> float:
        """Coin'in market impact çarpanı"""
        high_impact_coins = ['BTC', 'ETH', 'BNB']
        medium_impact_coins = ['XRP', 'ADA', 'SOL', 'DOT', 'MATIC']
        
        if symbol in high_impact_coins:
            return 1.5
        elif symbol in medium_impact_coins:
            return 1.2
        else:
            return 1.0
    
    def _calculate_overall_signal(self, signals: List[Dict]) -> Dict:
        """Bir coin için overall signal hesapla"""
        if not signals:
            return {'signal': 'NEUTRAL', 'confidence': 0.0}
        
        bullish_count = sum(1 for s in signals if s['signal_type'] == 'BULLISH')
        bearish_count = sum(1 for s in signals if s['signal_type'] == 'BEARISH')
        
        avg_confidence = np.mean([s['confidence'] for s in signals])
        
        if bullish_count > bearish_count:
            return {'signal': 'BULLISH', 'confidence': avg_confidence}
        elif bearish_count > bullish_count:
            return {'signal': 'BEARISH', 'confidence': avg_confidence}
        else:
            return {'signal': 'NEUTRAL', 'confidence': avg_confidence * 0.5}
    
    def _calculate_market_signal(self, coin_signals: Dict) -> Dict:
        """Genel market signal hesapla"""
        if not coin_signals:
            return {'signal': 'NEUTRAL', 'confidence': 0.0}
        
        bullish_coins = [c for c in coin_signals.values() 
                        if c['signal'] == 'BULLISH']
        bearish_coins = [c for c in coin_signals.values() 
                        if c['signal'] == 'BEARISH']
        
        if len(bullish_coins) > len(bearish_coins):
            avg_conf = np.mean([c['confidence'] for c in bullish_coins])
            return {'signal': 'BULLISH', 'confidence': avg_conf}
        elif len(bearish_coins) > len(bullish_coins):
            avg_conf = np.mean([c['confidence'] for c in bearish_coins])
            return {'signal': 'BEARISH', 'confidence': avg_conf}
        else:
            return {'signal': 'NEUTRAL', 'confidence': 0.5}
    
    def _analyze_exchange_flows(self, whale_data: List[Dict]) -> Dict:
        """Exchange akışlarını analiz et"""
        flows = {
            'inflows': defaultdict(float),
            'outflows': defaultdict(float),
            'net_flows': defaultdict(float)
        }
        
        for whale in whale_data:
            amount_usd = whale.get('amount_usd', 0)
            from_addr = whale.get('from', '')
            to_addr = whale.get('to', '')
            
            from_exchange = self._get_exchange_name(from_addr)
            to_exchange = self._get_exchange_name(to_addr)
            
            if to_exchange:
                flows['inflows'][to_exchange] += amount_usd
            
            if from_exchange:
                flows['outflows'][from_exchange] += amount_usd
        
        # Net flow hesapla
        all_exchanges = set(flows['inflows'].keys()) | set(flows['outflows'].keys())
        for exchange in all_exchanges:
            inflow = flows['inflows'][exchange]
            outflow = flows['outflows'][exchange]
            flows['net_flows'][exchange] = inflow - outflow
        
        return flows
    
    def generate_trading_signals(self, analysis_result: Dict) -> List[Dict]:
        """
        Analiz sonucundan trading sinyalleri üret
        """
        signals = []
        
        try:
            coin_signals = analysis_result.get('coin_signals', {})
            
            for symbol, signal_data in coin_signals.items():
                if signal_data['confidence'] >= config.SIGNAL_CONFIDENCE_THRESHOLD:
                    signal = {
                        'symbol': symbol,
                        'signal_type': signal_data['signal'],
                        'confidence': signal_data['confidence'],
                        'timestamp': datetime.now().isoformat(),
                        'source': 'whale_tracker',
                        'expiry': (datetime.now() + 
                                 timedelta(hours=config.SIGNAL_DECAY_HOURS)).isoformat()
                    }
                    
                    signals.append(signal)
            
            return signals
            
        except Exception as e:
            logger.error(f"Signal generation error: {e}")
            return [] 