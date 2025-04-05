"""
ユーティリティ関数
"""
import asyncio
import csv
from io import StringIO
from typing import List, Dict, Any, Optional
from asgiref.sync import sync_to_async

from .scrapers.champcamera import ChampCameraScraper
from .scrapers.kitamura import KitamuraScraper
from .scrapers.jcamera import JCameraScraper
from .models import SearchCache

def get_all_scrapers():
    """
    利用可能な全スクレイパーインスタンスを取得
    
    Returns:
        List[BaseScraper]: スクレイパーインスタンスのリスト
    """
    return [
        ChampCameraScraper(),
        KitamuraScraper(),
        JCameraScraper(),
    ]

async def search_all_sites(keyword: str, use_cache: bool = True) -> Dict[str, List[Dict[str, Any]]]:
    """
    全サイトで検索を実行
    
    Args:
        keyword (str): 検索キーワード
        use_cache (bool, optional): キャッシュを使用するかどうか。デフォルトはTrue。
        
    Returns:
        Dict[str, List[Dict[str, Any]]]: サイト名をキーとした検索結果辞書
    """
    scrapers = get_all_scrapers()
    tasks = []
    results = {}
    
    for scraper in scrapers:
        if use_cache:
            # キャッシュ確認 - 非同期対応
            cache = await get_valid_cache_async(keyword, scraper.name)
            if cache:
                results[scraper.name] = cache
                continue
                
        # キャッシュがない場合は検索タスクを追加
        tasks.append(_search_with_scraper(scraper, keyword, use_cache))
    
    # 非同期で全てのタスクを実行
    if tasks:
        site_results = await asyncio.gather(*tasks)
        # 結果をマージ
        for name, site_result in site_results:
            results[name] = site_result
    
    return results

async def _search_with_scraper(scraper, keyword: str, save_cache: bool = True) -> tuple:
    """
    単一のスクレイパーで検索を実行しキャッシュを更新
    
    Args:
        scraper: スクレイパーインスタンス
        keyword (str): 検索キーワード
        save_cache (bool, optional): 結果をキャッシュするかどうか。デフォルトはTrue。
        
    Returns:
        tuple: (スクレイパー名, 検索結果リスト)
    """
    results = await scraper.search(keyword)
    
    if save_cache and results:
        # 検索結果をキャッシュ - 非同期対応
        await create_cache_async(keyword, scraper.name, results)
    
    return (scraper.name, results)

def merge_search_results(results_dict: Dict[str, List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
    """
    サイト別の検索結果を1つのリストにマージ
    
    Args:
        results_dict (Dict[str, List[Dict[str, Any]]]): サイト名をキーとした検索結果辞書
        
    Returns:
        List[Dict[str, Any]]: マージされた検索結果リスト
    """
    merged_results = []
    
    for site_name, site_results in results_dict.items():
        merged_results.extend(site_results)
    
    return merged_results

# 非同期対応キャッシュ関数
@sync_to_async
def get_valid_cache_async(keyword, source):
    """非同期キャッシュ取得"""
    cache = SearchCache.get_valid_cache(keyword, source)
    if cache:
        return cache.results
    return None

@sync_to_async
def create_cache_async(keyword, source, results):
    """非同期キャッシュ作成"""
    return SearchCache.create_cache(keyword, source, results)


def export_to_csv(results: List[Dict[str, Any]]) -> str:
    """
    検索結果をCSV形式に変換
    
    Args:
        results (List[Dict[str, Any]]): 検索結果リスト
        
    Returns:
        str: CSV形式の文字列
    """
    if not results:
        return ""
    
    output = StringIO()
    fieldnames = ['title', 'price', 'condition', 'source', 'product_url', 'image_url']
    
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    
    for result in results:
        # 必要なフィールドのみ抽出
        row = {field: result.get(field, '') for field in fieldnames}
        writer.writerow(row)
    
    return output.getvalue()
