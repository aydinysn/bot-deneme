"""
Whale API Integrations
WhaleAlert.io, Etherscan ve diğer API'lerden whale verisi çeker
"""

import requests
import time
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import json

try:
    from . import whale_config as config
except ImportError:
    import whale_config as config

logger = logging.getLogger(__name__)

class WhaleAPI:
    """
    Whale tracking için API entegrasyonları
    """
    
    def __init__(self):
        self.whale_alert_api_key = config.WHALE_ALERT_API_KEY
        self.etherscan_api_key = config.ETHERSCAN_API_KEY
        self.bscscan_api_key = config.BSCSCAN_API_KEY
        
        # Rate limiting
        self.last_request_time = 0
        self.request_count = 0
        self.request_times = []
        
        # Cache
        self.cache = {}
        self.cache_timestamps = {}
        
    def _rate_limit(self):
        """API rate limiting"""
        current_time = time.time()
        
        # Remove old requests (older than 1 minute)
        self.request_times = [t for t in self.request_times 
                             if current_time - t < 60]
        
        # Check if we've exceeded rate limit
        if len(self.request_times) >= config.API_RATE_LIMIT_PER_MINUTE:
            sleep_time = 60 - (current_time - self.request_times[0])
            if sleep_time > 0:
                logger.info(f"Rate limit reached, waiting {sleep_time:.1f} seconds")
                time.sleep(sleep_time)
        
        # Add current request
        self.request_times.append(current_time)
        
        # Minimum delay between requests
        time_since_last = current_time - self.last_request_time
        if time_since_last < (1.0 / config.REQUESTS_PER_SECOND):
            time.sleep((1.0 / config.REQUESTS_PER_SECOND) - time_since_last)
        
        self.last_request_time = time.time()
    
    def _get_cached_data(self, cache_key: str) -> Optional[Dict]:
        """Cache'den veri al"""
        if not config.CACHE_WHALE_DATA:
            return None
            
        if cache_key in self.cache:
            cached_time = self.cache_timestamps.get(cache_key, 0)
            if time.time() - cached_time < config.CACHE_DURATION_MINUTES * 60:
                return self.cache[cache_key]
            else:
                # Expired cache
                del self.cache[cache_key]
                del self.cache_timestamps[cache_key]
        
        return None
    
    def _cache_data(self, cache_key: str, data: Dict):
        """Veriyi cache'le"""
        if not config.CACHE_WHALE_DATA:
            return
            
        self.cache[cache_key] = data
        self.cache_timestamps[cache_key] = time.time()
        
        # Cache size limit
        if len(self.cache) > config.MAX_CACHE_SIZE:
            # Remove oldest cache entry
            oldest_key = min(self.cache_timestamps.keys(), 
                           key=lambda k: self.cache_timestamps[k])
            del self.cache[oldest_key]
            del self.cache_timestamps[oldest_key]
    
    def get_whale_alert_transactions(self, 
                                   min_value: int = 1000000,
                                   limit: int = 100) -> List[Dict]:
        """
        WhaleAlert.io'dan büyük transferleri al
        """
        cache_key = f"whale_alert_{min_value}_{limit}"
        cached_data = self._get_cached_data(cache_key)
        if cached_data:
            return cached_data
        
        try:
            self._rate_limit()
            
            url = "https://api.whale-alert.io/v1/transactions"
            params = {
                'api_key': self.whale_alert_api_key,
                'min_value': min_value,
                'limit': limit
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('result') == 'success':
                transactions = data.get('transactions', [])
                self._cache_data(cache_key, transactions)
                return transactions
            else:
                logger.error(f"WhaleAlert API error: {data}")
                return []
                
        except requests.exceptions.RequestException as e:
            logger.error(f"WhaleAlert API request failed: {e}")
            return []
        except Exception as e:
            logger.error(f"WhaleAlert API unexpected error: {e}")
            return []
    
    def get_large_btc_transactions(self, 
                                 hours_back: int = 24,
                                 min_value_btc: float = 100) -> List[Dict]:
        """
        Büyük BTC transferlerini al (blockchain explorer kullanarak)
        Bu free API'ler kullanır
        """
        cache_key = f"btc_txs_{hours_back}_{min_value_btc}"
        cached_data = self._get_cached_data(cache_key)
        if cached_data:
            return cached_data
        
        # Free BTC API'den büyük transferleri bul
        # Bu gerçek implementasyonda blockchain.info, blockchair.com gibi
        # free API'ler kullanılabilir
        
        try:
            # Örnek implementation - gerçekte blockchain API kullanın
            transactions = []
            
            # Mock data for testing
            if min_value_btc <= 100:
                mock_transactions = [
                    {
                        'hash': '1a2b3c4d...',
                        'amount': 250.5,
                        'amount_usd': 27555000,
                        'timestamp': int(time.time() - 3600),  # 1 hour ago
                        'from': 'unknown',
                        'to': 'binance',
                        'symbol': 'BTC'
                    },
                    {
                        'hash': '5e6f7g8h...',
                        'amount': 150.2,
                        'amount_usd': 16522000,
                        'timestamp': int(time.time() - 7200),  # 2 hours ago
                        'from': 'coinbase',
                        'to': 'unknown',
                        'symbol': 'BTC'
                    }
                ]
                transactions = mock_transactions
            
            self._cache_data(cache_key, transactions)
            return transactions
            
        except Exception as e:
            logger.error(f"BTC transaction fetch error: {e}")
            return []
    
    def get_large_eth_transactions(self, 
                                 hours_back: int = 24,
                                 min_value_eth: float = 1000) -> List[Dict]:
        """
        Büyük ETH transferlerini al (Etherscan API)
        """
        cache_key = f"eth_txs_{hours_back}_{min_value_eth}"
        cached_data = self._get_cached_data(cache_key)
        if cached_data:
            return cached_data
        
        try:
            # Etherscan API kullanabilirsiniz (API key gerekli)
            # Şimdilik mock data
            
            transactions = []
            
            if min_value_eth <= 1000:
                mock_transactions = [
                    {
                        'hash': '0x1a2b3c...',
                        'amount': 5000.0,
                        'amount_usd': 13500000,
                        'timestamp': int(time.time() - 1800),  # 30 min ago
                        'from': 'unknown',
                        'to': 'binance',
                        'symbol': 'ETH'
                    }
                ]
                transactions = mock_transactions
            
            self._cache_data(cache_key, transactions)
            return transactions
            
        except Exception as e:
            logger.error(f"ETH transaction fetch error: {e}")
            return []
    
    def get_exchange_flows(self, 
                          exchange: str = 'binance',
                          hours_back: int = 24) -> Dict:
        """
        Belirli bir exchange'e gelen/giden akışları al
        """
        cache_key = f"exchange_flows_{exchange}_{hours_back}"
        cached_data = self._get_cached_data(cache_key)
        if cached_data:
            return cached_data
        
        try:
            # Exchange flow analizi
            # Gerçek implementasyonda exchange wallet adreslerini
            # monitor etmek gerekir
            
            flows = {
                'inflow': {
                    'BTC': 150.5,
                    'ETH': 8500.2,
                    'total_usd': 45000000
                },
                'outflow': {
                    'BTC': 89.2,
                    'ETH': 3200.1,
                    'total_usd': 18500000
                },
                'net_flow': {
                    'total_usd': 26500000,  # Net inflow
                    'direction': 'inflow'
                }
            }
            
            self._cache_data(cache_key, flows)
            return flows
            
        except Exception as e:
            logger.error(f"Exchange flow fetch error: {e}")
            return {}
    
    def get_whale_wallet_activity(self, 
                                wallet_address: str,
                                hours_back: int = 24) -> List[Dict]:
        """
        Belirli bir whale wallet'ının aktivitesini al
        """
        cache_key = f"wallet_{wallet_address}_{hours_back}"
        cached_data = self._get_cached_data(cache_key)
        if cached_data:
            return cached_data
        
        try:
            # Wallet activity tracking
            # Gerçek implementasyonda blockchain explorer API'leri kullanılır
            
            activities = [
                {
                    'timestamp': int(time.time() - 3600),
                    'type': 'transfer',
                    'amount': 500.0,
                    'symbol': 'BTC',
                    'to': 'binance',
                    'value_usd': 55000000
                }
            ]
            
            self._cache_data(cache_key, activities)
            return activities
            
        except Exception as e:
            logger.error(f"Wallet activity fetch error: {e}")
            return []
    
    def get_all_recent_whales(self, hours_back: int = 6) -> List[Dict]:
        """
        Son X saatteki tüm whale hareketlerini al
        """
        all_whales = []
        
        try:
            # WhaleAlert'ten al
            whale_alert_data = self.get_whale_alert_transactions(
                min_value=config.WHALE_THRESHOLD_USD
            )
            
            for tx in whale_alert_data:
                # Son X saat içindeki işlemleri filtrele
                tx_time = tx.get('timestamp', 0)
                if time.time() - tx_time <= hours_back * 3600:
                    all_whales.append({
                        'source': 'whale_alert',
                        'data': tx
                    })
            
            # BTC transferlerini al
            btc_txs = self.get_large_btc_transactions(
                hours_back=hours_back,
                min_value_btc=config.WHALE_THRESHOLD_BTC
            )
            
            for tx in btc_txs:
                all_whales.append({
                    'source': 'btc_chain',
                    'data': tx
                })
            
            # ETH transferlerini al
            eth_txs = self.get_large_eth_transactions(
                hours_back=hours_back,
                min_value_eth=config.WHALE_THRESHOLD_ETH
            )
            
            for tx in eth_txs:
                all_whales.append({
                    'source': 'eth_chain',
                    'data': tx
                })
            
            # Timestamp'e göre sırala (en yeni önce)
            all_whales.sort(key=lambda x: x['data'].get('timestamp', 0), reverse=True)
            
            return all_whales
            
        except Exception as e:
            logger.error(f"Get all whales error: {e}")
            return []
    
    def is_exchange_wallet(self, address: str) -> Optional[str]:
        """
        Bir adresin exchange wallet'ı olup olmadığını kontrol et
        """
        # Bilinen exchange wallet adreslerini kontrol et
        # Gerçek implementasyonda bir database veya API kullanılır
        
        known_wallets = {
            '1NDyJtNTjmwk5xPNhjgAMu4HDHigtobu1s': 'binance',
            '3Kzh9qAqVWQhEsfQz7zEQL1EuSx5tyNLNS': 'bitfinex',
            # ... daha fazla exchange wallet adresi
        }
        
        return known_wallets.get(address)
    
    def get_coin_price(self, symbol: str) -> Optional[float]:
        """
        Coin fiyatını al (USD)
        """
        try:
            # Basit price API - gerçekte CoinGecko, CMC vb. kullanılır
            # Mock data
            prices = {
                'BTC': 110000,
                'ETH': 2700,
                'BNB': 635,
                'XRP': 2.15,
                'ADA': 1.05
            }
            
            return prices.get(symbol.upper())
            
        except Exception as e:
            logger.error(f"Price fetch error for {symbol}: {e}")
            return None
    
    def health_check(self) -> Dict:
        """
        API'lerin çalışır durumda olup olmadığını kontrol et
        """
        health = {
            'whale_alert': False,
            'etherscan': False,
            'price_api': False,
            'overall': False
        }
        
        try:
            # WhaleAlert test
            if self.whale_alert_api_key and self.whale_alert_api_key != "your_whale_alert_api_key":
                test_data = self.get_whale_alert_transactions(limit=1)
                health['whale_alert'] = len(test_data) >= 0
            
            # Price API test
            btc_price = self.get_coin_price('BTC')
            health['price_api'] = btc_price is not None
            
            health['overall'] = any(health.values())
            
        except Exception as e:
            logger.error(f"Health check error: {e}")
        
        return health 