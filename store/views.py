from django.shortcuts import render, redirect, get_object_or_404
from .models import Product, Order, Category # Category model ni add chesam
from .forms import EnhancedRegisterForm
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout 
from django.contrib.auth.decorators import login_required
from django.db import transaction

def home(request):
    cart = request.session.get('cart', {})
    if not cart:
        request.session['cart'] = {}
        cart = request.session['cart']

    # Add to cart logic
    if request.method == 'POST':
        product_id = request.POST.get('product')
        if product_id:
            quantity = cart.get(str(product_id), 0)
            cart[str(product_id)] = quantity + 1
            request.session['cart'] = cart
            request.session.modified = True 
            return redirect('home')

    query = request.GET.get('query')
    
    # Logic for Category Grouping
    grouped_products = []
    
    if query:
        # Search chesinappudu grouping avasaram ledu kabatti simple items list
        items = Product.objects.filter(name__icontains=query)
        # Search results ni kuda category wise group cheyali ante idi vaadaali
        categories = Category.objects.all()
        for cat in categories:
            cat_items = items.filter(category=cat)
            if cat_items:
                for item in cat_items:
                    item.in_cart_qty = cart.get(str(item.id), 0)
                grouped_products.append({'name': cat.name, 'products': cat_items})
    else:
        # Normal view lo Categories wise products ni group chestunnam
        categories = Category.objects.all()
        for cat in categories:
            cat_items = Product.objects.filter(category=cat)
            if cat_items:
                for item in cat_items:
                    item.in_cart_qty = cart.get(str(item.id), 0)
                grouped_products.append({'name': cat.name, 'products': cat_items})

    total_items = sum(cart.values())
    
    return render(request, 'home.html', {
        'grouped_products': grouped_products, # 'items' badulu 'grouped_products' pampistunnam
        'cart_count': total_items,
        'query': query 
    })

# --- Migatha views (Register, Login, Logout) lo emi maarpu ledu ---

def register_view(request):
    if request.method == 'POST':
        form = EnhancedRegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password']) 
            user.save()
            login(request, user)
            return redirect('home')
    else:
        form = EnhancedRegisterForm()
    return render(request, 'register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('home')

def view_cart(request):
    cart = request.session.get('cart', {})
    cart_items = []
    grand_total = 0
    
    for product_id, quantity in cart.items():
        try:
            product = Product.objects.get(id=product_id)
            total_price = product.price * quantity
            grand_total += total_price
            cart_items.append({
                'product': product,
                'quantity': quantity,
                'total_price': total_price
            })
        except Product.DoesNotExist:
            continue
        
    return render(request, 'cart.html', {
        'cart_items': cart_items, 
        'grand_total': grand_total
    })

def remove_from_cart(request, product_id):
    cart = request.session.get('cart', {})
    product_id_str = str(product_id)
    if product_id_str in cart:
        del cart[product_id_str]
        request.session['cart'] = cart
        request.session.modified = True
    return redirect('view_cart')

@login_required(login_url='/login/')
def order_list(request):
    orders = Order.objects.filter(user=request.user).order_by('-id')
    return render(request, 'order_list.html', {'orders': orders})

@login_required(login_url='/login/')
def payment_page(request):
    cart = request.session.get('cart', {})
    if not cart: return redirect('home')
    # Product lookup simplified
    grand_total = sum(Product.objects.get(id=pid).price * qty for pid, qty in cart.items())
    return render(request, 'payment.html', {'total': grand_total})

@login_required(login_url='/login/')
def place_order(request):
    if request.method == 'POST':
        cart = request.session.get('cart', {})
        if not cart: return redirect('home')
        try:
            with transaction.atomic():
                items_list = []
                grand_total = 0
                for pid, qty in cart.items():
                    product = Product.objects.get(id=pid)
                    items_list.append(f"{product.name} (x{qty})")
                    grand_total += product.price * qty
                new_order = Order.objects.create(user=request.user, product_names=", ".join(items_list), total_price=grand_total)
                request.session['cart'] = {}
                request.session.modified = True
                return render(request, 'order_success.html', {'order': new_order})
        except Exception: return redirect('home')
    return redirect('view_cart')

def add_quantity(request, product_id):
    cart = request.session.get('cart', {})
    pid = str(product_id)
    if pid in cart:
        cart[pid] += 1
        request.session['cart'] = cart
        request.session.modified = True
    return redirect('view_cart')

def reduce_quantity(request, product_id):
    cart = request.session.get('cart', {})
    pid = str(product_id)
    if pid in cart:
        if cart[pid] > 1:
            cart[pid] -= 1
        else:
            del cart[pid]
        request.session['cart'] = cart
        request.session.modified = True
    return redirect('view_cart')