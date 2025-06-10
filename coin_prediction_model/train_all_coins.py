#!/usr/bin/env python3
"""
Tüm Coinler için ML Model Eğitimi
Coin listesindeki tüm coinler için ML modellerini eğitir
"""

import asyncio
import json
import time
from datetime import datetime
import sys
import os
import logging

# Parent dizini path'e ekle (config.py için)
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ml_models.model_trainer import ModelTrainer
import config

# Logging ayarla
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class AllCoinsTrainer:
    """Tüm coinler için ML model eğitimi"""
    
    def __init__(self):
        self.trainer = ModelTrainer()  # Client içeride oluşturuluyor
        self.results = {}
        self.failed_coins = []
        
    def load_all_coins(self):
        """Tüm coinleri yükle"""
        with open(config.COIN_LIST_FILE, 'r') as f:
            coin_data = json.load(f)
            
        if 'coins' in coin_data:
            # "/" karakterini kaldır (BTCUSDT formatına çevir)
            coins = [coin.replace('/', '') for coin in coin_data['coins']]
        else:
            coins = [coin['symbol'] for coin in coin_data]
            
        # Problematik coinleri filtrele
        filtered_coins = []
        skip_coins = ['SUSDT', 'IPUSDT', 'WALUSDT']  # Problematik semboller
        
        for coin in coins:
            if not any(skip in coin for skip in skip_coins):
                filtered_coins.append(coin)
        
        logger.info(f"Toplam {len(filtered_coins)} coin yüklenecek")
        return filtered_coins
    
    async def train_single_coin(self, symbol, index, total):
        """Tek coin için model eğit"""
        start_time = time.time()
        
        try:
            logger.info(f"[{index+1}/{total}] {symbol} eğitimi başlıyor...")
            
            # Yeni API kullan
            result = await self.trainer.train_single_coin(symbol)
            
            if result['success']:
                duration = time.time() - start_time
                
                self.results[symbol] = {
                    'success': True,
                    'test_mape': result['best_mape'],
                    'best_model': result['best_model'],
                    'duration': duration,
                    'train_samples': result['train_samples'],
                    'test_samples': result['test_samples'],
                    'trained_at': datetime.now().isoformat()
                }
                
                logger.info(f"✅ {symbol} başarılı! MAPE: {result['best_mape']:.2f}%, Model: {result['best_model']}, Süre: {duration:.1f}s")
                
            else:
                self.results[symbol] = {
                    'success': False,
                    'error': result['error'],
                    'duration': time.time() - start_time
                }
                self.failed_coins.append(symbol)
                logger.error(f"❌ {symbol} başarısız: {result['error']}")
                
        except Exception as e:
            duration = time.time() - start_time
            error_msg = str(e)[:100]
            
            self.results[symbol] = {
                'success': False,
                'error': error_msg,
                'duration': duration
            }
            self.failed_coins.append(symbol)
            logger.error(f"❌ {symbol} hatası: {error_msg}")
    
    async def train_all_coins(self, batch_size=1):
        """Tüm coinleri eğit"""
        
        coins = self.load_all_coins()
        total_coins = len(coins)
        
        logger.info(f"🚀 {total_coins} coin için ML model eğitimi başlıyor...")
        logger.info(f"⏱️  Tahmini süre: {total_coins * 1.5 / 60:.1f} dakika")
        
        start_time = time.time()
        
        # Batch halinde eğit (API limitlerini aşmamak için)
        for i in range(0, len(coins), batch_size):
            batch = coins[i:i+batch_size]
            
            # Batch'teki coinleri eğit
            tasks = []
            for j, symbol in enumerate(batch):
                global_index = i + j
                task = self.train_single_coin(symbol, global_index, total_coins)
                tasks.append(task)
            
            # Batch'i çalıştır
            await asyncio.gather(*tasks, return_exceptions=True)
            
            # Batch arası kısa mola (API limiti için)
            if i + batch_size < len(coins):
                await asyncio.sleep(2)
        
        total_duration = time.time() - start_time
        
        # Sonuçları özetle
        await self.print_summary(total_duration)
        
        # Sonuçları kaydet
        self.save_results()
    
    async def print_summary(self, total_duration):
        """Eğitim özetini yazdır"""
        
        successful = sum(1 for r in self.results.values() if r['success'])
        failed = len(self.failed_coins)
        total = successful + failed
        
        print("\n" + "="*80)
        print("🎯 ML MODEL EĞİTİMİ TAMAMLANDI!")
        print("="*80)
        print(f"📊 Toplam Coin: {total}")
        print(f"✅ Başarılı: {successful}")
        print(f"❌ Başarısız: {failed}")
        print(f"📈 Başarı Oranı: {successful/total*100:.1f}%")
        print(f"⏱️  Toplam Süre: {total_duration/60:.1f} dakika")
        print(f"⚡ Ortalama Süre/Coin: {total_duration/total:.1f} saniye")
        
        if successful > 0:
            # En iyi performanslar
            successful_results = {k: v for k, v in self.results.items() if v['success']}
            
            best_mape = min(successful_results.values(), key=lambda x: x['test_mape'])
            worst_mape = max(successful_results.values(), key=lambda x: x['test_mape'])
            avg_mape = sum(r['test_mape'] for r in successful_results.values()) / len(successful_results)
            
            print(f"\n📊 PERFORMANS İSTATİSTİKLERİ:")
            print(f"🏆 En İyi MAPE: {best_mape['test_mape']:.2f}% ({[k for k, v in successful_results.items() if v == best_mape][0]})")
            print(f"📉 En Kötü MAPE: {worst_mape['test_mape']:.2f}% ({[k for k, v in successful_results.items() if v == worst_mape][0]})")
            print(f"📊 Ortalama MAPE: {avg_mape:.2f}%")
            
            # Model dağılımı
            model_counts = {}
            for result in successful_results.values():
                model = result['best_model']
                model_counts[model] = model_counts.get(model, 0) + 1
            
            print(f"\n🤖 MODEL DAĞILIMI:")
            for model, count in sorted(model_counts.items(), key=lambda x: x[1], reverse=True):
                print(f"   {model}: {count} coin ({count/successful*100:.1f}%)")
        
        if failed > 0:
            print(f"\n❌ BAŞARISIZ COİNLER ({failed} adet):")
            for coin in self.failed_coins[:10]:  # İlk 10'unu göster
                error = self.results[coin]['error'][:50]
                print(f"   {coin}: {error}")
            if failed > 10:
                print(f"   ... ve {failed-10} coin daha")
        
        print("\n✅ Tüm modeller ml_models/saved_models/ klasöründe kaydedildi")
        print("🔄 Modelleri kullanmak için: python quick_prediction.py COINUSDT")
        print("="*80)
    
    def save_results(self):
        """Sonuçları dosyaya kaydet"""
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        results_file = f"training_results_{timestamp}.json"
        
        summary = {
            'training_completed_at': datetime.now().isoformat(),
            'total_coins': len(self.results),
            'successful_coins': sum(1 for r in self.results.values() if r['success']),
            'failed_coins': len(self.failed_coins),
            'results': self.results,
            'failed_coin_list': self.failed_coins
        }
        
        with open(results_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        logger.info(f"📄 Sonuçlar kaydedildi: {results_file}")

async def main():
    """Ana fonksiyon"""
    
    print("🤖 TÜM COİNLER İÇİN ML MODEL EĞİTİMİ")
    print("="*50)
    
    # Kullanıcı onayı al
    response = input("Bu işlem 1-2 saat sürebilir. Devam etmek istiyor musunuz? (y/N): ")
    
    if response.lower() not in ['y', 'yes', 'evet', 'e']:
        print("❌ İşlem iptal edildi")
        return
    
    trainer = AllCoinsTrainer()
    await trainer.train_all_coins(batch_size=1)

if __name__ == "__main__":
    asyncio.run(main()) 