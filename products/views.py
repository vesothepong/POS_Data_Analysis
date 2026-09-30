from django.contrib import messages
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from accounts.permissions import admin_required
from forecasting.services import product_series

from . import calc
from .forms import ProductForm, StockUpdateForm
from .models import Product
from .services import inventory_rows


# ------------------------------------------------------------------- products
@admin_required
def products(request):
    q = request.GET.get("q", "").strip()
    qs = Product.objects.all().order_by("name")
    if q:
        qs = qs.filter(Q(name__icontains=q) | Q(category__icontains=q))
    return render(request, "products/list.html", {"products": qs, "q": q})


@admin_required
def product_create(request):
    form = ProductForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        form.save()
        messages.success(request, "Product added successfully.")
        return redirect("products")
    return render(request, "products/form.html", {"form": form, "title": "Add Product"})


@admin_required
def product_edit(request, pk):
    obj = get_object_or_404(Product, pk=pk)
    form = ProductForm(request.POST or None, request.FILES or None, instance=obj)
    if form.is_valid():
        form.save()
        messages.success(request, "Product updated successfully.")
        return redirect("products")
    return render(request, "products/form.html", {"form": form, "title": "Update Product", "product": obj})


@admin_required
def product_delete(request, pk):
    obj = get_object_or_404(Product, pk=pk)
    if request.method == "POST":
        obj.delete()
        messages.success(request, "Product deleted.")
        return redirect("products")
    return render(request, "products/confirm_delete.html", {"object": obj, "type": "product"})


# ------------------------------------------------------------------ inventory
@admin_required
def inventory(request):
    status, q = request.GET.get("status", ""), request.GET.get("q", "").strip()
    rows = inventory_rows(status=status if status in calc.ALL_STATUSES else None, query=q)
    return render(request, "products/inventory_list.html", {"rows": rows, "statuses": calc.ALL_STATUSES, "status": status, "q": q})


@admin_required
def inventory_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    row = next(r for r in inventory_rows() if r["product"].id == product.id)
    s = product_series(product.id)
    history = [{"month": i.strftime("%Y-%m"), "actual": int(v)} for i, v in s.items()][-12:]
    return render(request, "products/inventory_detail.html", {"row": row, "history": history, "form": StockUpdateForm(initial={"stock_quantity": product.stock_quantity})})


@admin_required
def inventory_update(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method != "POST":
        return redirect("inventory")
    form = StockUpdateForm(request.POST)
    if form.is_valid():
        product.stock_quantity = form.cleaned_data["stock_quantity"]
        product.save(update_fields=["stock_quantity", "updated_at"])
        messages.success(request, f"Stock for {product.name} updated to {product.stock_quantity}.")
    else:
        messages.error(request, "Enter a whole number of 0 or more.")
    if request.POST.get("next") == "detail":
        return redirect("inventory_detail", pk=pk)
    return redirect("inventory")
