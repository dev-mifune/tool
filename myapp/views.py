import asyncio
import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.template.loader import render_to_string
from django.conf import settings

from .models import Category, Task, SearchCache
from .utils import search_all_sites, merge_search_results, export_to_csv

def task_list(request):
    tasks = Task.objects.all().order_by('-created_at')
    categories = Category.objects.all()
    context = {
        'tasks': tasks,
        'categories': categories,
    }
    return render(request, 'myapp/task_list.html', context)

def task_detail(request, pk):
    task = get_object_or_404(Task, pk=pk)
    return render(request, 'myapp/task_detail.html', {'task': task})

def task_create(request):
    if request.method == 'POST':
        # 処理は未実装。フォームを使用する予定
        title = request.POST.get('title')
        description = request.POST.get('description')
        category_id = request.POST.get('category')
        status = request.POST.get('status')
        due_date = request.POST.get('due_date') or None
        
        category = get_object_or_404(Category, pk=category_id)
        task = Task(
            title=title,
            description=description,
            category=category,
            status=status,
            due_date=due_date
        )
        task.save()
        messages.success(request, 'タスクが作成されました')
        return redirect('task_detail', pk=task.pk)
    
    categories = Category.objects.all()
    return render(request, 'myapp/task_form.html', {'categories': categories})

def task_update(request, pk):
    task = get_object_or_404(Task, pk=pk)
    
    if request.method == 'POST':
        # 処理は未実装。フォームを使用する予定
        task.title = request.POST.get('title')
        task.description = request.POST.get('description')
        category_id = request.POST.get('category')
        task.category = get_object_or_404(Category, pk=category_id)
        task.status = request.POST.get('status')
        task.due_date = request.POST.get('due_date') or None
        
        task.save()
        messages.success(request, 'タスクが更新されました')
        return redirect('task_detail', pk=task.pk)
    
    categories = Category.objects.all()
    return render(request, 'myapp/task_form.html', {
        'task': task,
        'categories': categories
    })

def task_delete(request, pk):
    task = get_object_or_404(Task, pk=pk)
    
    if request.method == 'POST':
        task.delete()
        messages.success(request, 'タスクが削除されました')
        return redirect('task_list')
    
    return render(request, 'myapp/task_confirm_delete.html', {'task': task})

def category_list(request):
    categories = Category.objects.all()
    return render(request, 'myapp/category_list.html', {'categories': categories})

# 元のビューも残しておきます
def item_list(request):
    return render(request, 'myapp/item_list.html')


# 以下スクレイピング機能用のビュー

def camera_search(request):
    """カメラ検索ページを表示"""
    return render(request, 'myapp/camera_search.html')

@csrf_exempt
def search_api(request):
    """検索APIエンドポイント"""
    if request.method != 'POST':
        return JsonResponse({'error': '不正なリクエストメソッド'}, status=405)
    
    # POSTリクエストからキーワードを取得
    try:
        data = json.loads(request.body)
        keyword = data.get('keyword', '')
    except json.JSONDecodeError:
        keyword = request.POST.get('keyword', '')
    
    if not keyword:
        return JsonResponse({'error': 'キーワードが指定されていません'}, status=400)
    
    # 非同期で全サイト検索を実行
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            results_dict = loop.run_until_complete(search_all_sites(keyword))
        finally:
            loop.close()
        
        # 結果をマージ
        merged_results = merge_search_results(results_dict)
        
        # 価格でソート
        sorted_results = sorted(merged_results, key=lambda x: x.get('price', 0))
        
        # 結果を返す
        return JsonResponse({
            'keyword': keyword,
            'count': len(sorted_results),
            'results': sorted_results,
        })
    except Exception as e:
        import traceback
        error_traceback = traceback.format_exc()
        print(f"Error in search_api: {str(e)}\n{error_traceback}")
        return JsonResponse({
            'error': f'検索時にエラーが発生しました: {str(e)}',
            'details': error_traceback if settings.DEBUG else ''
        }, status=500)

def search_results_html(request):
    """検索結果を部分HTMLとして返す（Ajax用）"""
    keyword = request.GET.get('keyword', '')
    if not keyword:
        return HttpResponse('キーワードが指定されていません')
    
    # 非同期で全サイト検索を実行
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        results_dict = loop.run_until_complete(search_all_sites(keyword))
    finally:
        loop.close()
    
    # 結果をマージ
    merged_results = merge_search_results(results_dict)
    
    # 価格でソート
    sorted_results = sorted(merged_results, key=lambda x: x.get('price', 0))
    
    # テンプレートでレンダリング
    html = render_to_string('myapp/partials/search_results.html', {
        'results': sorted_results,
        'keyword': keyword,
    })
    
    return HttpResponse(html)

def export_search_results(request):
    """検索結果をCSVとしてエクスポート"""
    keyword = request.GET.get('keyword', '')
    if not keyword:
        messages.error(request, 'キーワードが指定されていません')
        return redirect('camera_search')
    
    # 非同期で全サイト検索を実行
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        results_dict = loop.run_until_complete(search_all_sites(keyword))
    finally:
        loop.close()
    
    # 結果をマージ
    merged_results = merge_search_results(results_dict)
    
    # 価格でソート
    sorted_results = sorted(merged_results, key=lambda x: x.get('price', 0))
    
    # CSVとしてエクスポート
    csv_data = export_to_csv(sorted_results)
    
    response = HttpResponse(csv_data, content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="camera_search_{keyword}.csv"'
    
    return response
