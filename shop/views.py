from django.shortcuts import render, redirect, get_object_or_404
from .models import Product
from django.contrib.auth.decorators import login_required
from django.db.models import Q

def home(request):
    products = Product.objects.all()
    return render(request, "home.html", {"products": products})

def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    return render(request, "product_detail.html", {"product": product})

@login_required
def add_product(request):
    if request.method == "POST":
        name = request.POST.get("name")
        category = request.POST.get("category")
        country = request.POST.get("country")
        description = request.POST.get("description")
        price = request.POST.get("price")
        stock = request.POST.get("stock", 0)
        is_active = 'is_active' in request.POST
        image = request.FILES.get("image")
        if not (name and description and price and image):
            return render(request, "add_product.html", {"error": "All fields are required!"})
        
        Product.objects.create(
            owner=request.user,
            name=name,
            category=category,
            country=country,
            description=description,
            price=price,
            stock=stock,
            is_active=is_active,
            image=image
        )
        return redirect("home")
    return render(request, "add_product.html")

@login_required
def edit_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if product.owner != request.user and not request.user.is_superuser:
        return render(request, "error.html", {"error": "Access denied!"})

    if request.method == "POST":
        product.name = request.POST.get("name")
        product.category = request.POST.get("category")
        product.country = request.POST.get("country")
        product.description = request.POST.get("description")
        product.price = request.POST.get("price")
        product.stock = request.POST.get("stock", 0)
        product.is_active = 'is_active' in request.POST
        if "image" in request.FILES:
            product.image = request.FILES["image"]
        product.save()
        return redirect("home")
    return render(request, "edit_product.html", {"product": product})

@login_required
def delete_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if product.owner != request.user and not request.user.is_superuser:
        return render(request, "error.html", {"error": "Access denied!"})
    if request.method == "POST":
        product.delete()
        return redirect("home")
    return render(request, "delete_product.html", {"product": product})

def search(request):
    query = request.GET.get('q', '')
    selected_categories = request.GET.getlist('category')
    country = request.GET.get('country', '')
    min_price = request.GET.get('min_price', '')
    max_price = request.GET.get('max_price', '')
    in_stock = request.GET.get('in_stock', '') 

    results = Product.objects.all()
    if query:
        results = results.filter(Q(name__icontains=query) | Q(description__icontains=query))
    if selected_categories:
        results = results.filter(category__in=selected_categories)
    if country:
        results = results.filter(country__icontains=country)
    if min_price:
        results = results.filter(price__gte=min_price)
    if max_price:
        results = results.filter(price__lte=max_price)
    if in_stock:
        results = results.filter(stock__gt=0)  

    categories = Product.objects.values_list('category', flat=True).distinct()

    return render(request, 'search.html', {
        'query': query,
        'selected_categories': selected_categories,
        'country': country,
        'min_price': min_price,
        'max_price': max_price,
        'results': results,
        'categories': categories,
    })
