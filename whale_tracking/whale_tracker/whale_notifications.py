"""
Whale Notifications
Whale hareketleri için bildirim sistemi
"""

import logging
from datetime import datetime
from typing import List, Dict, Optional
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests
import time

try:
    from . import whale_config as config
except ImportError:
    import whale_config as config

logger = logging.getLogger(__name__)

class WhaleNotifier:
    """
    Whale hareketleri için bildirim sistemi
    """
    
    def __init__(self):
        self.notification_history = []
        self.enabled = config.ENABLE_WHALE_NOTIFICATIONS
        self.telegram_enabled = getattr(config, 'TELEGRAM_ENABLED', False)
        self.telegram_token = getattr(config, 'TELEGRAM_BOT_TOKEN', '')
        self.telegram_chat_id = getattr(config, 'TELEGRAM_CHAT_ID', '')
        
    def notify_whale_movement(self, whale_data: Dict, analysis: Dict):
        """
        Whale hareketi bildirimi gönder
        """
        try:
            if not self.enabled:
                return
            
            # Bildirim gerekip gerekmediğini kontrol et
            if not self._should_notify(whale_data, analysis):
                return
            
            # Bildirim mesajı oluştur
            message = self._create_whale_message(whale_data, analysis)
            
            # Bildirimleri gönder
            self._send_console_notification(message)
            
            # Telegram gönder
            if (self.telegram_enabled and 
                getattr(config, 'TELEGRAM_SEND_WHALE_MOVEMENTS', True)):
                telegram_message = self._create_telegram_whale_message(whale_data, analysis)
                self._send_telegram_notification(telegram_message)
            
            # E-posta gönder (opsiyonel)
            # self._send_email_notification(message)
            
            # Discord/Telegram gönder (opsiyonel)
            # self._send_discord_notification(message)
            
            # Bildirim geçmişine ekle
            self._save_notification(whale_data, analysis, message)
            
        except Exception as e:
            logger.error(f"Whale notification error: {e}")
    
    def notify_pattern_detected(self, pattern_data: Dict):
        """
        Pattern tespit bildirimi
        """
        try:
            if not self.enabled:
                return
            
            if pattern_data.get('pattern_confidence', 0) < 0.7:
                return
            
            message = self._create_pattern_message(pattern_data)
            
            self._send_console_notification(message, level="PATTERN")
            
            # Telegram pattern bildirimi
            if (self.telegram_enabled and 
                getattr(config, 'TELEGRAM_SEND_PATTERNS', True)):
                telegram_message = self._create_telegram_pattern_message(pattern_data)
                self._send_telegram_notification(telegram_message)
            
            # Pattern bildirimini kaydet
            notification_record = {
                'type': 'pattern',
                'data': pattern_data,
                'message': message,
                'timestamp': datetime.now().isoformat()
            }
            self.notification_history.append(notification_record)
            
        except Exception as e:
            logger.error(f"Pattern notification error: {e}")
    
    def notify_signal_generated(self, signals: List[Dict]):
        """
        Sinyal üretildi bildirimi
        """
        try:
            if not self.enabled or not signals:
                return
            
            # Sadece güçlü sinyaller için bildir
            strong_signals = [s for s in signals 
                            if s.get('strength') in ['STRONG', 'VERY_STRONG']]
            
            # Telegram ayarı - sadece güçlü sinyaller gönder?
            if getattr(config, 'TELEGRAM_SEND_ONLY_STRONG', False):
                signals_to_send = strong_signals
            else:
                signals_to_send = signals
            
            if not signals_to_send:
                return
            
            message = self._create_signals_message(signals_to_send)
            
            self._send_console_notification(message, level="SIGNAL")
            
            # Telegram sinyal bildirimi
            if (self.telegram_enabled and 
                getattr(config, 'TELEGRAM_SEND_SIGNALS', True)):
                telegram_message = self._create_telegram_signals_message(signals_to_send)
                self._send_telegram_notification(telegram_message)
            
            # Sinyal bildirimini kaydet
            notification_record = {
                'type': 'signals',
                'data': signals_to_send,
                'message': message,
                'timestamp': datetime.now().isoformat()
            }
            self.notification_history.append(notification_record)
            
        except Exception as e:
            logger.error(f"Signal notification error: {e}")
    
    def notify_market_alert(self, alert_type: str, data: Dict):
        """
        Market uyarısı bildirimi
        """
        try:
            if not self.enabled:
                return
            
            message = self._create_market_alert_message(alert_type, data)
            
            self._send_console_notification(message, level="ALERT")
            
            # Telegram market alert
            if (self.telegram_enabled and 
                getattr(config, 'TELEGRAM_SEND_ALERTS', True)):
                telegram_message = self._create_telegram_alert_message(alert_type, data)
                self._send_telegram_notification(telegram_message)
            
            notification_record = {
                'type': 'market_alert',
                'alert_type': alert_type,
                'data': data,
                'message': message,
                'timestamp': datetime.now().isoformat()
            }
            self.notification_history.append(notification_record)
            
        except Exception as e:
            logger.error(f"Market alert notification error: {e}")
    
    def _should_notify(self, whale_data: Dict, analysis: Dict) -> bool:
        """
        Bildirim gönderilip gönderilmeyeceğini belirle
        """
        try:
            amount_usd = whale_data.get('amount_usd', 0)
            
            # Minimum değer kontrolü
            if not config.NOTIFY_MINOR_WHALES and amount_usd < config.SIGNAL_STRENGTH['MODERATE']:
                return False
            
            # Exchange akışları kontrolü
            from_addr = whale_data.get('from', '')
            to_addr = whale_data.get('to', '')
            
            has_exchange = any([
                any(ex in from_addr.lower() for ex in config.MAJOR_EXCHANGES),
                any(ex in to_addr.lower() for ex in config.MAJOR_EXCHANGES)
            ])
            
            if not config.NOTIFY_EXCHANGE_FLOWS and has_exchange:
                return False
            
            # Unknown wallet kontrolü
            is_unknown = (from_addr == 'unknown' or to_addr == 'unknown' or 
                         'unknown' in from_addr or 'unknown' in to_addr)
            
            if not config.NOTIFY_UNKNOWN_WALLETS and is_unknown:
                return False
            
            # Confidence kontrolü
            confidence = analysis.get('confidence', 0)
            if confidence < 0.4:  # Çok düşük güven
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Should notify check error: {e}")
            return False
    
    def _create_whale_message(self, whale_data: Dict, analysis: Dict) -> str:
        """
        Whale hareketi mesajı oluştur
        """
        try:
            symbol = whale_data.get('symbol', 'UNKNOWN')
            amount = whale_data.get('amount', 0)
            amount_usd = whale_data.get('amount_usd', 0)
            from_addr = whale_data.get('from', 'unknown')
            to_addr = whale_data.get('to', 'unknown')
            
            signal_type = analysis.get('signal_type', 'NEUTRAL')
            confidence = analysis.get('confidence', 0)
            strength = analysis.get('strength', 'MINOR')
            
            # Emoji ve renk kodları
            emoji_map = {
                'BULLISH': '🐂',
                'BEARISH': '🐻',
                'NEUTRAL': '🔄',
                'UNCERTAIN': '❓'
            }
            
            strength_emoji = {
                'EXTREME': '🔥🔥🔥',
                'MAJOR': '🔥🔥',
                'MODERATE': '🔥',
                'MINOR': '💫'
            }
            
            emoji = emoji_map.get(signal_type, '📊')
            strength_em = strength_emoji.get(strength, '💫')
            
            message = f"""
🐋 WHALE HAREKET TESPİT EDİLDİ! {emoji}

💰 Coin: {symbol}
📊 Miktar: {amount:,.2f} {symbol} (${amount_usd:,.0f})
🎯 Signal: {signal_type} {emoji}
💪 Güç: {strength} {strength_em}
🎲 Güven: {confidence:.1%}

📍 Transfer:
   ↗️ Gönderen: {from_addr[:20]}{'...' if len(from_addr) > 20 else ''}
   ↘️ Alan: {to_addr[:20]}{'...' if len(to_addr) > 20 else ''}

🧠 Analiz:
"""
            
            # Reasoning ekle
            reasoning = analysis.get('reasoning', [])
            for reason in reasoning[:3]:  # İlk 3 sebep
                message += f"   • {reason}\n"
            
            # Önerilen aksiyon
            recommended = analysis.get('recommended_action', {})
            if recommended:
                primary_action = recommended.get('primary', 'HOLD')
                message += f"\n💡 Önerilen: {primary_action}"
            
            message += f"\n⏰ Zaman: {datetime.now().strftime('%H:%M:%S')}"
            
            return message
            
        except Exception as e:
            logger.error(f"Create whale message error: {e}")
            return f"Whale movement detected - Error formatting message: {str(e)}"
    
    def _create_pattern_message(self, pattern_data: Dict) -> str:
        """
        Pattern tespit mesajı oluştur
        """
        try:
            confidence = pattern_data.get('pattern_confidence', 0)
            
            message = f"""
🔍 WHALE PATTERN TESPİT EDİLDİ!

🎯 Güven Skoru: {confidence:.1%}

📊 Tespit Edilen Patternler:
"""
            
            patterns = [
                ('accumulation_pattern', 'Accumulation (Toplama)', '🟢'),
                ('distribution_pattern', 'Distribution (Dağıtım)', '🔴'),
                ('exchange_exodus', 'Exchange Exodus', '🚀'),
                ('coordinated_selling', 'Koordineli Satış', '⚠️'),
                ('whale_rotation', 'Whale Rotation', '🔄')
            ]
            
            for pattern_key, pattern_name, emoji in patterns:
                if pattern_data.get(pattern_key, False):
                    message += f"   {emoji} {pattern_name}\n"
            
            # Pattern'a göre tavsiye
            if pattern_data.get('accumulation_pattern'):
                message += "\n💡 Tavsiye: Potansiyel fiyat artışına hazır olun"
            elif pattern_data.get('distribution_pattern'):
                message += "\n💡 Tavsiye: Dikkatli olun, satış baskısı gelebilir"
            elif pattern_data.get('exchange_exodus'):
                message += "\n💡 Tavsiye: Büyük institutionlar accumulate ediyor olabilir"
            
            message += f"\n⏰ Zaman: {datetime.now().strftime('%H:%M:%S')}"
            
            return message
            
        except Exception as e:
            logger.error(f"Create pattern message error: {e}")
            return f"Pattern detected - Error formatting message: {str(e)}"
    
    def _create_signals_message(self, signals: List[Dict]) -> str:
        """
        Sinyal listesi mesajı oluştur
        """
        try:
            message = f"""
📈 WHALE SİNYALLER ÜRETİLDİ!

🎯 Toplam Sinyal: {len(signals)}

"""
            
            for signal in signals[:5]:  # İlk 5 sinyal
                symbol = signal.get('symbol', 'UNKNOWN')
                signal_type = signal.get('signal_type', 'NEUTRAL')
                confidence = signal.get('confidence', 0)
                strength = signal.get('strength', 'WEAK')
                
                emoji = '🐂' if signal_type == 'BULLISH' else '🐻' if signal_type == 'BEARISH' else '🔄'
                
                message += f"   {emoji} {symbol}: {signal_type} ({confidence:.1%}) - {strength}\n"
            
            if len(signals) > 5:
                message += f"   ... ve {len(signals) - 5} sinyal daha\n"
            
            message += f"\n⏰ Zaman: {datetime.now().strftime('%H:%M:%S')}"
            
            return message
            
        except Exception as e:
            logger.error(f"Create signals message error: {e}")
            return f"Signals generated - Error formatting message: {str(e)}"
    
    def _create_market_alert_message(self, alert_type: str, data: Dict) -> str:
        """
        Market uyarısı mesajı oluştur
        """
        try:
            alert_messages = {
                'massive_outflow': f"🚨 BÜYÜK EXCHANGE OUTFLOW!\n💰 Toplam: ${data.get('amount', 0):,.0f}",
                'whale_accumulation': f"🐋 WHALE ACCUMULATION TESPİT!\n📊 {data.get('count', 0)} büyük hareket",
                'coordinated_dump': f"⚠️ KOORDİNELİ SATIŞ UYARISI!\n🔴 {data.get('exchanges', 0)} exchange'de büyük deposit",
                'unusual_activity': f"🔍 OLAĞANDIŞI AKTİVİTE!\n📈 Normal seviyenin {data.get('multiplier', 1):.1f}x üzerinde"
            }
            
            message = alert_messages.get(alert_type, f"Market Alert: {alert_type}")
            message += f"\n⏰ Zaman: {datetime.now().strftime('%H:%M:%S')}"
            
            return message
            
        except Exception as e:
            logger.error(f"Create market alert message error: {e}")
            return f"Market alert - Error formatting message: {str(e)}"
    
    def _send_console_notification(self, message: str, level: str = "INFO"):
        """
        Konsola bildirim gönder
        """
        try:
            border = "=" * 60
            
            print(f"\n{border}")
            print(f"🐋 WHALE TRACKER NOTIFICATION - {level}")
            print(f"{border}")
            print(message)
            print(f"{border}\n")
            
            # Logging'e de yaz
            logger.info(f"Whale notification sent: {level}")
            
        except Exception as e:
            logger.error(f"Console notification error: {e}")
    
    def _send_email_notification(self, message: str):
        """
        E-posta bildirimi gönder (opsiyonel)
        """
        try:
            # E-posta konfigürasyonu gerekli
            # Bu kısım kullanıcı tarafından konfigüre edilmeli
            
            """
            smtp_server = "smtp.gmail.com"
            smtp_port = 587
            email_user = "your_email@gmail.com"
            email_password = "your_app_password"
            recipient = "your_email@gmail.com"
            
            msg = MIMEMultipart()
            msg['From'] = email_user
            msg['To'] = recipient
            msg['Subject'] = "Whale Tracker Alert"
            
            msg.attach(MIMEText(message, 'plain'))
            
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(email_user, email_password)
            server.send_message(msg)
            server.quit()
            
            logger.info("Email notification sent successfully")
            """
            
            logger.info("Email notification skipped (not configured)")
            
        except Exception as e:
            logger.error(f"Email notification error: {e}")
    
    def _send_discord_notification(self, message: str):
        """
        Discord webhook bildirimi gönder (opsiyonel)
        """
        try:
            # Discord webhook URL gerekli
            # import requests
            
            """
            webhook_url = "YOUR_DISCORD_WEBHOOK_URL"
            
            data = {
                "content": f"```{message}```",
                "username": "Whale Tracker Bot"
            }
            
            response = requests.post(webhook_url, json=data)
            
            if response.status_code == 204:
                logger.info("Discord notification sent successfully")
            else:
                logger.error(f"Discord notification failed: {response.status_code}")
            """
            
            logger.info("Discord notification skipped (not configured)")
            
        except Exception as e:
            logger.error(f"Discord notification error: {e}")
    
    def _send_telegram_notification(self, message: str) -> bool:
        """
        Telegram bildirimi gönder - return success status
        """
        try:
            if not self.telegram_enabled:
                logger.debug("Telegram notifications disabled")
                return False
            
            if not self.telegram_token or self.telegram_token == "your_telegram_bot_token":
                logger.error("Telegram bot token not configured")
                return False
            
            if not self.telegram_chat_id or self.telegram_chat_id == "your_chat_id":
                logger.error("Telegram chat ID not configured") 
                return False
            
            telegram_api_url = f"https://api.telegram.org/bot{self.telegram_token}/sendMessage"
            
            # Parse mode configuration'dan al
            parse_mode = getattr(config, 'TELEGRAM_PARSE_MODE', 'Markdown')
            disable_preview = getattr(config, 'TELEGRAM_DISABLE_PREVIEW', True)
            
            data = {
                "chat_id": self.telegram_chat_id,
                "text": message,
                "parse_mode": parse_mode,
                "disable_web_page_preview": disable_preview
            }
            
            response = requests.post(telegram_api_url, json=data, timeout=10)
            
            if response.status_code == 200:
                logger.info("Telegram notification sent successfully")
                return True
            else:
                logger.error(f"Telegram notification failed: {response.status_code} - {response.text}")
                return False
            
        except Exception as e:
            logger.error(f"Telegram notification error: {e}")
            return False
    
    def _save_notification(self, whale_data: Dict, analysis: Dict, message: str):
        """
        Bildirim geçmişine kaydet
        """
        try:
            notification_record = {
                'type': 'whale_movement',
                'whale_data': whale_data,
                'analysis': analysis,
                'message': message,
                'timestamp': datetime.now().isoformat()
            }
            
            self.notification_history.append(notification_record)
            
            # History limitini kontrol et
            if len(self.notification_history) > 500:
                self.notification_history = self.notification_history[-250:]  # Son 250'yi tut
            
        except Exception as e:
            logger.error(f"Save notification error: {e}")
    
    def get_notification_history(self, hours_back: int = 24) -> List[Dict]:
        """
        Bildirim geçmişini al
        """
        try:
            cutoff_time = datetime.now().timestamp() - (hours_back * 3600)
            
            recent_notifications = []
            
            for notification in self.notification_history:
                notification_time = datetime.fromisoformat(
                    notification['timestamp'].replace('Z', '+00:00')
                ).timestamp()
                
                if notification_time >= cutoff_time:
                    recent_notifications.append(notification)
            
            return recent_notifications
            
        except Exception as e:
            logger.error(f"Get notification history error: {e}")
            return []
    
    def enable_notifications(self):
        """Bildirimleri etkinleştir"""
        self.enabled = True
        logger.info("Whale notifications enabled")
    
    def disable_notifications(self):
        """Bildirimleri devre dışı bırak"""
        self.enabled = False
        logger.info("Whale notifications disabled")
    
    def get_notification_stats(self) -> Dict:
        """
        Bildirim istatistiklerini al
        """
        try:
            recent_notifications = self.get_notification_history(hours_back=24)
            
            stats = {
                'total_notifications_24h': len(recent_notifications),
                'whale_movements': 0,
                'patterns': 0,
                'signals': 0,
                'market_alerts': 0,
                'enabled': self.enabled
            }
            
            for notification in recent_notifications:
                notification_type = notification.get('type', 'unknown')
                if notification_type == 'whale_movement':
                    stats['whale_movements'] += 1
                elif notification_type == 'pattern':
                    stats['patterns'] += 1
                elif notification_type == 'signals':
                    stats['signals'] += 1
                elif notification_type == 'market_alert':
                    stats['market_alerts'] += 1
            
            return stats
            
        except Exception as e:
            logger.error(f"Notification stats error: {e}")
            return {'error': str(e)}
    
    def test_notification_system(self):
        """
        Bildirim sistemini test et
        """
        try:
            test_message = """
🧪 TEST BİLDİRİMİ

Bu bir test bildirimidir.
Whale Tracker bildirim sistemi çalışıyor! ✅

⏰ Test Zamanı: {datetime.now().strftime('%H:%M:%S')}
""".format(datetime=datetime)
            
            self._send_console_notification(test_message, level="TEST")
            
            # Telegram test
            if self.telegram_enabled:
                self.test_telegram_connection()
            
            logger.info("Notification system test completed")
            return True
            
        except Exception as e:
            logger.error(f"Notification test error: {e}")
            return False
    
    def test_telegram_connection(self):
        """
        Telegram bot bağlantısını test et
        """
        try:
            if not self.telegram_enabled:
                logger.warning("Telegram disabled - skipping test")
                return False
            
            if not self.telegram_token or self.telegram_token == "your_telegram_bot_token":
                logger.error("Telegram bot token not configured")
                return False
            
            if not self.telegram_chat_id or self.telegram_chat_id == "your_chat_id":
                logger.error("Telegram chat ID not configured")
                return False
            
            # Test mesajı gönder
            test_message = f"""🧪 *WHALE TRACKER TEST*

✅ Telegram bağlantısı başarılı!
🤖 Bot Token: `{self.telegram_token[:10]}...`
💬 Chat ID: `{self.telegram_chat_id}`

⏰ Test Zamanı: `{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}`

🐋 Whale Tracker sistemi aktif ve hazır!"""
            
            success = self._send_telegram_notification(test_message)
            
            if success:
                logger.info("Telegram test message sent successfully")
                return True
            else:
                logger.error("Telegram test message failed")
                return False
            
        except Exception as e:
            logger.error(f"Telegram test error: {e}")
            return False
    
    def get_telegram_bot_info(self):
        """
        Telegram bot bilgilerini al
        """
        try:
            if not self.telegram_enabled or not self.telegram_token:
                return {'enabled': False, 'error': 'Token not configured'}
            
            url = f"https://api.telegram.org/bot{self.telegram_token}/getMe"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                bot_info = response.json()
                return {
                    'enabled': True,
                    'bot_info': bot_info.get('result', {}),
                    'status': 'OK'
                }
            else:
                return {
                    'enabled': True,
                    'error': f'API error: {response.status_code}',
                    'status': 'ERROR'
                }
            
        except Exception as e:
            return {
                'enabled': True,
                'error': str(e),
                'status': 'ERROR'
            }

    # ================== TELEGRAM MESSAGE FORMATTERS ==================
    
    def _create_telegram_whale_message(self, whale_data: Dict, analysis: Dict) -> str:
        """
        Telegram için whale hareketi mesajı oluştur
        """
        try:
            symbol = whale_data.get('symbol', 'UNKNOWN')
            amount = whale_data.get('amount', 0)
            amount_usd = whale_data.get('amount_usd', 0)
            from_addr = whale_data.get('from', 'unknown')
            to_addr = whale_data.get('to', 'unknown')
            
            signal_type = analysis.get('signal_type', 'NEUTRAL')
            confidence = analysis.get('confidence', 0)
            strength = analysis.get('strength', 'MINOR')
            
            # Emoji ve formatlar
            emoji_map = {
                'BULLISH': '🐂',
                'BEARISH': '🐻', 
                'NEUTRAL': '🔄',
                'UNCERTAIN': '❓'
            }
            
            strength_emoji = {
                'EXTREME': '🔥🔥🔥',
                'MAJOR': '🔥🔥',
                'MODERATE': '🔥',
                'MINOR': '💫'
            }
            
            emoji = emoji_map.get(signal_type, '📊')
            strength_em = strength_emoji.get(strength, '💫')
            
            message = f"""🐋 *WHALE HAREKET* {emoji}

💰 *Coin:* `{symbol}`
📊 *Miktar:* `{amount:,.2f} {symbol}` (${amount_usd:,.0f})
🎯 *Signal:* `{signal_type}` {emoji}
💪 *Güç:* `{strength}` {strength_em}
🎲 *Güven:* `{confidence:.1%}`

📍 *Transfer:*
↗️ Gönderen: `{from_addr[:25]}{'...' if len(from_addr) > 25 else ''}`
↘️ Alan: `{to_addr[:25]}{'...' if len(to_addr) > 25 else ''}`

⏰ *Zaman:* `{datetime.now().strftime('%H:%M:%S')}`"""
            
            # Önerilen aksiyon
            recommended = analysis.get('recommended_action', {})
            if recommended:
                primary_action = recommended.get('primary', 'HOLD')
                message += f"\n💡 *Önerilen:* `{primary_action}`"
            
            return message
            
        except Exception as e:
            logger.error(f"Create telegram whale message error: {e}")
            return f"🐋 Whale movement detected\nError: {str(e)}"
    
    def _create_telegram_pattern_message(self, pattern_data: Dict) -> str:
        """
        Telegram için pattern tespit mesajı oluştur
        """
        try:
            confidence = pattern_data.get('pattern_confidence', 0)
            
            message = f"""🔍 *WHALE PATTERN TESPİT*

🎯 *Güven Skoru:* `{confidence:.1%}`

📊 *Tespit Edilen Patternler:*"""
            
            patterns = [
                ('accumulation_pattern', 'Accumulation (Toplama)', '🟢'),
                ('distribution_pattern', 'Distribution (Dağıtım)', '🔴'),
                ('exchange_exodus', 'Exchange Exodus', '🚀'),
                ('coordinated_selling', 'Koordineli Satış', '⚠️'),
                ('whale_rotation', 'Whale Rotation', '🔄')
            ]
            
            detected_patterns = []
            for pattern_key, pattern_name, emoji in patterns:
                if pattern_data.get(pattern_key, False):
                    detected_patterns.append(f"{emoji} {pattern_name}")
            
            if detected_patterns:
                message += "\n" + "\n".join(f"• {pattern}" for pattern in detected_patterns)
            
            # Pattern'a göre tavsiye
            if pattern_data.get('accumulation_pattern'):
                message += "\n\n💡 *Tavsiye:* Potansiyel fiyat artışına hazır olun"
            elif pattern_data.get('distribution_pattern'):
                message += "\n\n💡 *Tavsiye:* Dikkatli olun, satış baskısı gelebilir"
            elif pattern_data.get('exchange_exodus'):
                message += "\n\n💡 *Tavsiye:* Büyük institutionlar accumulate ediyor olabilir"
            
            message += f"\n\n⏰ *Zaman:* `{datetime.now().strftime('%H:%M:%S')}`"
            
            return message
            
        except Exception as e:
            logger.error(f"Create telegram pattern message error: {e}")
            return f"🔍 Pattern detected\nError: {str(e)}"
    
    def _create_telegram_signals_message(self, signals: List[Dict]) -> str:
        """
        Telegram için sinyal listesi mesajı oluştur
        """
        try:
            message = f"""📈 *WHALE SİNYALLER ÜRETİLDİ*

🎯 *Toplam Sinyal:* `{len(signals)}`

*Sinyaller:*"""
            
            for signal in signals[:5]:  # İlk 5 sinyal
                symbol = signal.get('symbol', 'UNKNOWN')
                signal_type = signal.get('signal_type', 'NEUTRAL')
                confidence = signal.get('confidence', 0)
                strength = signal.get('strength', 'WEAK')
                
                emoji = '🐂' if signal_type == 'BULLISH' else '🐻' if signal_type == 'BEARISH' else '🔄'
                
                message += f"\n{emoji} `{symbol}`: *{signal_type}* ({confidence:.1%}) - {strength}"
            
            if len(signals) > 5:
                message += f"\n... ve {len(signals) - 5} sinyal daha"
            
            message += f"\n\n⏰ *Zaman:* `{datetime.now().strftime('%H:%M:%S')}`"
            
            return message
            
        except Exception as e:
            logger.error(f"Create telegram signals message error: {e}")
            return f"📈 Signals generated\nError: {str(e)}"
    
    def _create_telegram_alert_message(self, alert_type: str, data: Dict) -> str:
        """
        Telegram için market uyarısı mesajı oluştur
        """
        try:
            alert_messages = {
                'massive_outflow': f"🚨 *BÜYÜK EXCHANGE OUTFLOW*\n💰 Toplam: `${data.get('amount', 0):,.0f}`",
                'whale_accumulation': f"🐋 *WHALE ACCUMULATION TESPİT*\n📊 `{data.get('count', 0)}` büyük hareket",
                'coordinated_dump': f"⚠️ *KOORDİNELİ SATIŞ UYARISI*\n🔴 `{data.get('exchanges', 0)}` exchange'de büyük deposit",
                'unusual_activity': f"🔍 *OLAĞANDIŞI AKTİVİTE*\n📈 Normal seviyenin `{data.get('multiplier', 1):.1f}x` üzerinde"
            }
            
            message = alert_messages.get(alert_type, f"*Market Alert:* {alert_type}")
            message += f"\n\n⏰ *Zaman:* `{datetime.now().strftime('%H:%M:%S')}`"
            
            return message
            
        except Exception as e:
            logger.error(f"Create telegram alert message error: {e}")
            return f"*Market Alert*\nError: {str(e)}" 