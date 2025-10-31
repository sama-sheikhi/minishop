from django.shortcuts import render,redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from .models import Product
from django.shortcuts import get_object_or_404

def register(request):
    if request.method =="POST":
        username= request.POST.get("username")
        email= request.POST.get("email")
        password= request.POST.get("password")
        confirm_password= request.POST.get("confirm-password")
        check_pass = check_password(password)
        if User.objects.filter(username=username).exists():
            return render(request,"register.html",{"error":"username must be unique!"})
        elif len(check_pass) !=0:
            return render(request,"register.html",{"error": "\n".join(check_pass)})
        elif confirm_password != password:
            return render(request,"register.html",{"error":"passwords do not match!"})
        else:
            User.objects.create_user(username=username,email=email,password=password)
            return redirect('login')
    return render (request,'register.html')    


def check_password(password):
    errors = []
    up = False
    lo = False
    di = False
    for i in password:
        if i.isupper():
            up = True
        elif i.islower():
            lo = True
        elif i.isdigit():
            di = True
    if len(password) < 8:
        errors.append("Password Must Bigger Than 6.")
    if not up:
        errors.append("Password Must Have A - Z.")
    if not lo:
        errors.append("Password Must Have a - z.")
    if not di:
        errors.append("Password Must Have 0 - 9.")
    return errors


def login_view(request):
    if request.method =="POST":
        username= request.POST.get("username")
        password= request.POST.get("password")
        user=authenticate(request,username=username,password=password)
        if user is not None:
            login(request,user)
            return redirect("profile")
        else:
            return render(request,"login.html", {"error":"Wrong username or password!!!"})
        
    return render(request,'login.html')


def logout_view(request):
    logout(request)
    return redirect("login")


def home(request):
    products = Product.objects.all()
    return render(request, "home.html", {"products": products})


@login_required
def profile(request):
    user_products = Product.objects.filter(owner=request.user).order_by('-created_at')
    return render(request, 'profile.html', {'user_products': user_products})


@login_required
def add_product(request):
    if request.method == "POST":
        name = request.POST.get("name")
        description = request.POST.get("description")
        price = request.POST.get("price")
        image = request.FILES.get("image")
        if not (name and description and price and image):
            return render(request, "add_product.html", {"error": "All fields are required!"})
        
        Product.objects.create(
            owner=request.user,
            name=name,
            description=description,
            price=price,
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
        product.description = request.POST.get("description")
        product.price = request.POST.get("price")

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

def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    return render(request, "product_detail.html", {"product": product})
