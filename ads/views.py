from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator
from django.http import JsonResponse
from .models import Ad, Category, Tag, Comment, Favorite
from .forms import AdForm, CommentForm, SearchForm


def index(request):
    """Главная страница"""
    ads = Ad.objects.filter(is_active=True).select_related('author', 'category')
    sale_categories = Category.objects.filter(type='sale')
    buy_categories = Category.objects.filter(type='buy')

    # Поиск
    search_form = SearchForm(request.GET)
    query = request.GET.get('query', '')
    category_id = request.GET.get('category', '')
    min_price = request.GET.get('min_price', '')
    max_price = request.GET.get('max_price', '')
    city = request.GET.get('city', '')

    if query:
        ads = ads.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(city__icontains=query)
        )
    if category_id:
        ads = ads.filter(category_id=category_id)
    if min_price:
        ads = ads.filter(price__gte=min_price)
    if max_price:
        ads = ads.filter(price__lte=max_price)
    if city:
        ads = ads.filter(city__icontains=city)

    paginator = Paginator(ads, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'sale_categories': sale_categories,
        'buy_categories': buy_categories,
        'search_form': search_form,
        'query': query,
    }
    return render(request, 'ads/index.html', context)


def ad_detail(request, pk):
    """Детальная страница объявления"""
    ad = get_object_or_404(Ad, pk=pk, is_active=True)
    ad.increment_views()

    comments = ad.comments.select_related('author').all()
    comment_form = CommentForm()

    is_favorite = False
    if request.user.is_authenticated:
        is_favorite = Favorite.objects.filter(user=request.user, ad=ad).exists()

    if request.method == 'POST' and request.user.is_authenticated:
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.ad = ad
            comment.author = request.user
            comment.save()
            messages.success(request, 'Комментарий добавлен!')
            return redirect('ads:detail', pk=pk)

    context = {
        'ad': ad,
        'comments': comments,
        'comment_form': comment_form,
        'is_favorite': is_favorite,
    }
    return render(request, 'ads/detail.html', context)


def category_view(request, slug):
    """Объявления по категории"""
    category = get_object_or_404(Category, slug=slug)
    ads = Ad.objects.filter(
        category=category, is_active=True
    ).select_related('author')

    paginator = Paginator(ads, 12)
    page_obj = paginator.get_page(request.GET.get('page'))

    context = {
        'category': category,
        'page_obj': page_obj,
    }
    return render(request, 'ads/category.html', context)


@login_required
def ad_create(request):
    """Создание объявления"""
    if request.method == 'POST':
        form = AdForm(request.POST, request.FILES)
        if form.is_valid():
            ad = form.save(commit=False)
            ad.author = request.user
            ad.save()
            form.save_m2m()
            messages.success(request, 'Объявление успешно создано!')
            return redirect('ads:detail', pk=ad.pk)
    else:
        form = AdForm()

    return render(request, 'ads/ad_form.html', {
        'form': form,
        'title': 'Создать объявление'
    })


@login_required
def ad_edit(request, pk):
    """Редактирование объявления"""
    ad = get_object_or_404(Ad, pk=pk)

    if ad.author != request.user and not request.user.is_staff:
        messages.error(request, 'У вас нет прав для редактирования этого объявления')
        return redirect('ads:detail', pk=pk)

    if request.method == 'POST':
        form = AdForm(request.POST, request.FILES, instance=ad)
        if form.is_valid():
            form.save()
            messages.success(request, 'Объявление обновлено!')
            return redirect('ads:detail', pk=pk)
    else:
        form = AdForm(instance=ad)

    return render(request, 'ads/ad_form.html', {
        'form': form,
        'title': 'Редактировать объявление',
        'ad': ad
    })


@login_required
def ad_delete(request, pk):
    """Удаление объявления"""
    ad = get_object_or_404(Ad, pk=pk)

    if ad.author != request.user and not request.user.is_staff:
        messages.error(request, 'У вас нет прав для удаления этого объявления')
        return redirect('ads:detail', pk=pk)

    if request.method == 'POST':
        ad.is_active = False
        ad.save()
        messages.success(request, 'Объявление удалено!')
        return redirect('ads:index')

    return render(request, 'ads/ad_confirm_delete.html', {'ad': ad})


@login_required
def toggle_favorite(request, pk):
    """Добавить/убрать из избранного"""
    ad = get_object_or_404(Ad, pk=pk, is_active=True)
    favorite, created = Favorite.objects.get_or_create(user=request.user, ad=ad)

    if not created:
        favorite.delete()
        is_favorite = False
        msg = 'Удалено из избранного'
    else:
        is_favorite = True
        msg = 'Добавлено в избранное'

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'is_favorite': is_favorite, 'message': msg})

    messages.success(request, msg)
    return redirect('ads:detail', pk=pk)


@login_required
def favorites_list(request):
    """Список избранных объявлений"""
    favorites = Favorite.objects.filter(
        user=request.user
    ).select_related('ad', 'ad__author', 'ad__category')

    context = {'favorites': favorites}
    return render(request, 'ads/favorites.html', context)


@login_required
def my_ads(request):
    """Мои объявления"""
    ads = Ad.objects.filter(
        author=request.user
    ).order_by('-created_at')

    context = {'ads': ads}
    return render(request, 'ads/my_ads.html', context)


@login_required
def delete_comment(request, pk):
    """Удаление комментария"""
    comment = get_object_or_404(Comment, pk=pk)

    if comment.author != request.user and not request.user.is_staff:
        messages.error(request, 'Нет прав для удаления')
        return redirect('ads:detail', pk=comment.ad.pk)

    ad_pk = comment.ad.pk
    comment.delete()
    messages.success(request, 'Комментарий удалён')
    return redirect('ads:detail', pk=ad_pk)
