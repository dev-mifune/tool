# カメラ専門店横断検索スクレイピングツール 要件定義書

## 1. プロジェクト概要
複数のカメラ専門店Webサイトをスクレイピングし、キーワード検索により商品情報を横断的に取得・一覧表示するDjangoアプリケーション。

## 2. 対象Webサイト
- チャンプカメラ (https://www.champcamera.co.jp)
- カメラのキタムラ (https://shop.kitamura.jp)
- J-Camera (https://j-camera.net)

## 3. 基本機能
- 対象サイト横断検索機能
- キーワードベースの検索
- 取得データ項目：
  - 商品名
  - 価格
  - 商品状態/ランク（可能な場合）
  - 画像URL（サムネイル）
  - 商品ページURL
  - 出品サイト名

## 4. ユーザーインターフェース
- シンプルな検索フォーム（キーワード入力欄）
- 結果一覧表示（テーブル形式）
- 価格順ソート機能
- サイト別フィルター機能

## 5. システム構成
- バックエンド：Django
  - スクレイピングロジック
  - API提供
- フロントエンド：既存のフロントエンドフレームワーク
  - 検索フォーム
  - 結果表示コンポーネント

## 6. スクレイピング実装
- Beautiful SoupまたはScrapyを使用
- 各サイト用のカスタムスクレイパー実装
- 非同期処理によるパフォーマンス最適化
- robots.txtポリシー遵守
- 適切なユーザーエージェント設定
- リクエスト間隔の調整（サーバー負荷軽減）

## 7. 追加機能
- 検索結果のCSVエクスポート
- キャッシュ機能（短時間内の同一検索の高速化）
- エラーハンドリング（サイト側の変更対応）

## 8. 実装計画
### アプリ構造
```
tool_project/
├── myapp/
│   ├── scrapers/
│   │   ├── __init__.py
│   │   ├── base.py         # 基本スクレイパークラス
│   │   ├── champcamera.py  # チャンプカメラ専用スクレイパー
│   │   ├── kitamura.py     # キタムラ専用スクレイパー
│   │   └── jcamera.py      # J-Camera専用スクレイパー
│   ├── views.py            # API・ビュー定義
│   ├── models.py           # データモデル（検索結果キャッシュ用）
│   └── utils.py            # ユーティリティ関数
└── frontend/               # フロントエンド（既存）
```

### データモデル
```python
# models.py
from django.db import models

class SearchCache(models.Model):
    """検索結果をキャッシュするモデル"""
    keyword = models.CharField(max_length=100)
    source = models.CharField(max_length=50)  # サイト名
    results_json = models.JSONField()  # 検索結果をJSON形式で保存
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()  # キャッシュ有効期限
    
    class Meta:
        indexes = [
            models.Index(fields=['keyword', 'source']),
        ]
```

### APIエンドポイント
- `POST /api/search/` - キーワード検索実行
  - リクエストパラメータ：`keyword`（検索キーワード）, `sources`（対象サイト、オプション）
  - レスポンス：統合された検索結果

## 9. 使用技術・ライブラリ
- Django
- Requests / aiohttp (HTTP通信)
- Beautiful Soup (HTML解析)
- pandas (データ整形・CSV出力)

## 10. 制約・考慮事項
- 各サイトのHTML構造変更への対応
- 過度な頻度でのアクセスを避ける
- パフォーマンス最適化（並列処理の検討）
- エラー発生時の適切なフォールバック
