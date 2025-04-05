from django.db import models
from django.utils import timezone
from datetime import timedelta
import json

class Category(models.Model):
    name = models.CharField('カテゴリ名', max_length=50)
    created_at = models.DateTimeField('作成日', default=timezone.now)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = 'カテゴリ'
        verbose_name_plural = 'カテゴリ'

class Task(models.Model):
    STATUS_CHOICES = [
        ('not_started', '未着手'),
        ('in_progress', '進行中'),
        ('completed', '完了'),
    ]
    
    title = models.CharField('タイトル', max_length=100)
    description = models.TextField('詳細', blank=True, null=True)
    category = models.ForeignKey(Category, verbose_name='カテゴリ', on_delete=models.CASCADE)
    status = models.CharField('ステータス', max_length=20, choices=STATUS_CHOICES, default='not_started')
    due_date = models.DateField('期限日', blank=True, null=True)
    created_at = models.DateTimeField('作成日', default=timezone.now)
    updated_at = models.DateTimeField('更新日', auto_now=True)
    
    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name = 'タスク'
        verbose_name_plural = 'タスク'


class SearchCache(models.Model):
    """検索結果をキャッシュするモデル"""
    keyword = models.CharField('検索キーワード', max_length=100)
    source = models.CharField('ソースサイト', max_length=50)  # サイト名
    results_json = models.JSONField('検索結果JSON')  # 検索結果をJSON形式で保存
    created_at = models.DateTimeField('作成日時', auto_now_add=True)
    expires_at = models.DateTimeField('有効期限')
    
    def __str__(self):
        return f"{self.keyword} - {self.source}"
    
    @property
    def is_expired(self):
        """キャッシュが期限切れかどうか"""
        return timezone.now() > self.expires_at
    
    @property
    def results(self):
        """JSONから結果リストを取得"""
        try:
            if isinstance(self.results_json, str):
                return json.loads(self.results_json)
            return self.results_json
        except (json.JSONDecodeError, TypeError):
            return []
    
    @classmethod
    def create_cache(cls, keyword, source, results, cache_duration=timedelta(hours=1)):
        """キャッシュを作成"""
        expires_at = timezone.now() + cache_duration
        
        # 既存のキャッシュがあれば更新
        cache, created = cls.objects.update_or_create(
            keyword=keyword,
            source=source,
            defaults={
                'results_json': results,
                'expires_at': expires_at
            }
        )
        return cache
    
    @classmethod
    def get_valid_cache(cls, keyword, source):
        """有効なキャッシュを取得"""
        try:
            cache = cls.objects.get(keyword=keyword, source=source)
            if cache.is_expired:
                cache.delete()
                return None
            return cache
        except cls.DoesNotExist:
            return None
    
    class Meta:
        verbose_name = '検索キャッシュ'
        verbose_name_plural = '検索キャッシュ'
        indexes = [
            models.Index(fields=['keyword', 'source']),
        ]
