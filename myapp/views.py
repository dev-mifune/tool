from django.shortcuts import render

def item_list(request):
    # Your view logic here
    return render(request, 'myapp/item_list.html', {'items': []})
