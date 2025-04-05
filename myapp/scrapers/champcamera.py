"""
チャンプカメラスクレイパー
https://www.champcamera.co.jp/ からの商品情報取得
"""
import re
from typing import List, Dict, Any, Optional
from urllib.parse import urljoin
from .base import BaseScraper

class ChampCameraScraper(BaseScraper):
    """チャンプカメラ専用スクレイパー"""
    
    def __init__(self):
        super().__init__(delay_seconds=1.5)  # サイトの負荷を考慮して遅延を設定
        self.base_url = "https://www.champcamera.co.jp/"
        self.search_url_template = "https://www.champcamera.co.jp/shop/used.php?keyword={keyword}"
    
    async def search(self, keyword: str) -> List[Dict[str, Any]]:
        """
        チャンプカメラで検索を実行
        
        Args:
            keyword (str): 検索キーワード
            
        Returns:
            List[Dict[str, Any]]: 検索結果リスト
        """
        search_url = self.search_url_template.format(keyword=keyword.replace(" ", "+"))
        # デバッグ用にログ出力
        print(f"Scraping ChampCamera with keyword: {keyword} URL: {search_url}")
        
        html = await self.get_html(search_url)
        
        if not html:
            print("Failed to get HTML from ChampCamera")
            return []
        
        soup = self.parse_html(html)
        if not soup:
            return []
        
        results = []
        
        # 商品一覧を取得（実際のサイト構造に合わせて調整）
        product_items = soup.select('.used_list .item')
        
        for item in product_items:
            try:
                # 商品名
                title_elem = item.select_one('.item_name')
                title = title_elem.text.strip() if title_elem else ''
                
                # 商品URL
                url_elem = item.select_one('a.item_link')
                product_url = urljoin(self.base_url, url_elem['href']) if url_elem and 'href' in url_elem.attrs else ''
                
                # 価格
                price_elem = item.select_one('.price')
                price_text = price_elem.text.strip() if price_elem else '0'
                price = self._extract_price(price_text)
                
                # 画像URL
                img_elem = item.select_one('img')
                image_url = urljoin(self.base_url, img_elem['src']) if img_elem and 'src' in img_elem.attrs else ''
                
                # コンディション
                condition_elem = item.select_one('.rank')
                condition = condition_elem.text.strip() if condition_elem else ''
                
                results.append({
                    'title': title,
                    'price': price,
                    'condition': condition,
                    'image_url': image_url,
                    'product_url': product_url,
                })
                
            except Exception as e:
                # 個別の商品解析エラーはスキップして続行
                continue
                
        return self.format_result(results)
    
    def _extract_price(self, price_text: str) -> int:
        """
        価格テキストから数値のみを抽出
        
        Args:
            price_text (str): 価格テキスト (例: "¥123,456")
            
        Returns:
            int: 価格 (例: 123456)
        """
        if not price_text:
            return 0
            
        # 数字のみを抽出
        numbers = re.sub(r'[^\d]', '', price_text)
        try:
            return int(numbers)
        except ValueError:
            return 0
