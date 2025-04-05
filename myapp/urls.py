from django.urls import path
from . import views

urlpatterns = [
    # 元のパス
    path('items/', views.item_list, name='item_list'),
    
    # タスク関連のパス
    path('', views.task_list, name='task_list'),
    path('tasks/', views.task_list, name='task_list'),
    path('tasks/<int:pk>/', views.task_detail, name='task_detail'),
    path('tasks/new/', views.task_create, name='task_create'),
    path('tasks/<int:pk>/edit/', views.task_update, name='task_update'),
    path('tasks/<int:pk>/delete/', views.task_delete, name='task_delete'),
    
    # カテゴリ関連のパス
    path('categories/', views.category_list, name='category_list'),
    
    # カメラ検索関連のパス
    path('camera-search/', views.camera_search, name='camera_search'),
    path('api/search/', views.search_api, name='search_api'),
    path('search-results-html/', views.search_results_html, name='search_results_html'),
    path('export-csv/', views.export_search_results, name='export_csv'),
]