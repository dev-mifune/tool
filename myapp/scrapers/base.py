"""
ベーススクレイパークラス
全てのサイトスクレイパーの基底クラス
"""
import logging
import aiohttp
import asyncio
import traceback
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

class BaseScraperException(Exception):
    """スクレイピング関連の例外基底クラス"""
    pass

class BaseScraper(ABC):
    """スクレイパーの基底クラス"""
    
    def __init__(self, delay_seconds: float = 1.0):
        """
        初期化
        
        Args:
            delay_seconds (float): リクエスト間の待機時間（秒）
        """
        self.delay = delay_seconds
        self.name = self.__class__.__name__
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept-Language': 'ja,en-US;q=0.9,en;q=0.8',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Cache-Control': 'max-age=0',
            'Upgrade-Insecure-Requests': '1',
        }
    
    @abstractmethod
    async def search(self, keyword: str) -> List[Dict[str, Any]]:
        """
        キーワードで検索を実行
        
        Args:
            keyword (str): 検索キーワード
            
        Returns:
            List[Dict[str, Any]]: 検索結果リスト
        """
        pass
    
    async def get_html(self, url: str) -> Optional[str]:
        """
        指定URLからHTMLを取得
        
        Args:
            url (str): 取得対象URL
            
        Returns:
            Optional[str]: HTML文字列、エラー時はNone
        """
        try:
            async with aiohttp.ClientSession() as session:
                for attempt in range(3):  # 最大再試行回数03回
                    try:
                        async with session.get(url, headers=self.headers, timeout=30) as response:
                            if response.status == 200:
                                html = await response.text()
                                await asyncio.sleep(self.delay)  # サイトへの負荷軽減
                                return html
                            elif response.status == 429:  # Too Many Requests
                                logger.warning(f"Rate limited on {url}. Waiting before retry...")
                                await asyncio.sleep(self.delay * 2)  # 長めの待機時間
                                continue
                            else:
                                logger.error(f"Error fetching {url}: Status {response.status}")
                                return None
                    except asyncio.TimeoutError:
                        logger.warning(f"Timeout fetching {url}. Attempt {attempt+1}/3")
                        await asyncio.sleep(self.delay)
                    except Exception as e:
                        logger.exception(f"Exception on attempt {attempt+1}/3 while fetching {url}: {e}")
                        await asyncio.sleep(self.delay)
                        
                logger.error(f"Failed to fetch {url} after 3 attempts")
                return None
        except Exception as e:
            logger.exception(f"Exception while creating session for {url}: {e}")
            return None
    
    def parse_html(self, html: str) -> Optional[BeautifulSoup]:
        """
        HTML文字列をBeautifulSoupオブジェクトに変換
        
        Args:
            html (str): HTML文字列
            
        Returns:
            Optional[BeautifulSoup]: パース結果、エラー時はNone
        """
        try:
            return BeautifulSoup(html, 'html.parser')
        except Exception as e:
            logger.exception(f"Error parsing HTML: {e}")
            return None
    
    def format_result(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        スクレイピング結果を統一フォーマットに変換
        
        Args:
            items (List[Dict[str, Any]]): スクレイピング結果
            
        Returns:
            List[Dict[str, Any]]: フォーマット済み結果
        """
        formatted_items = []
        
        for item in items:
            formatted_item = {
                'title': item.get('title', ''),
                'price': item.get('price', 0),
                'condition': item.get('condition', ''),
                'image_url': item.get('image_url', ''),
                'product_url': item.get('product_url', ''),
                'source': self.name,
            }
            formatted_items.append(formatted_item)
        
        return formatted_items
