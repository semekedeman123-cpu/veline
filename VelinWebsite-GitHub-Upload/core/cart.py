from decimal import Decimal, ROUND_HALF_UP

from .models import Product


def price_to_string(value):
    return str(Decimal(value).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


def get_cart_session(request):
    return request.session.setdefault("cart", {})


def build_cart_summary(request):
    cart = request.session.get("cart", {})
    product_ids = []
    for key in cart.keys():
        try:
            product_ids.append(int(key))
        except (TypeError, ValueError):
            continue
    product_map = {
        product.id: product
        for product in Product.objects.filter(id__in=product_ids)
    }
    items = []
    subtotal = Decimal("0.00")
    for product_id, payload in cart.items():
        try:
            product = product_map[int(product_id)]
        except (KeyError, ValueError):
            continue
        quantity = min(int(payload.get("quantity", 1)), max(product.stock_quantity, 0))
        if quantity < 1:
            continue
        unit_price = Decimal(str(payload.get("unit_price", product.price_amount)))
        line_subtotal = (unit_price * quantity).quantize(Decimal("0.01"))
        subtotal += line_subtotal
        items.append(
            {
                "product": product,
                "quantity": quantity,
                "unit_price": unit_price,
                "subtotal": line_subtotal,
            }
        )
    shipping = Decimal("0.00")
    total = subtotal + shipping
    return {
        "items": items,
        "subtotal": subtotal,
        "shipping": shipping,
        "total": total,
        "count": sum(item["quantity"] for item in items),
    }


def add_to_cart(request, product, quantity=1):
    cart = get_cart_session(request)
    key = str(product.id)
    existing = cart.get(key, {})
    new_quantity = int(existing.get("quantity", 0)) + int(quantity)
    new_quantity = min(new_quantity, max(product.stock_quantity, 0))
    if new_quantity < 1:
        cart.pop(key, None)
    else:
        unit_price = Decimal(product.price_amount).quantize(Decimal("0.01"))
        cart[key] = {
            "quantity": new_quantity,
            "unit_price": price_to_string(unit_price),
            "subtotal": price_to_string(unit_price * new_quantity),
        }
    request.session.modified = True


def update_cart_item(request, product, quantity):
    cart = get_cart_session(request)
    key = str(product.id)
    quantity = max(0, min(int(quantity), max(product.stock_quantity, 0)))
    if quantity == 0:
        cart.pop(key, None)
    else:
        unit_price = Decimal(product.price_amount).quantize(Decimal("0.01"))
        cart[key] = {
            "quantity": quantity,
            "unit_price": price_to_string(unit_price),
            "subtotal": price_to_string(unit_price * quantity),
        }
    request.session.modified = True


def remove_cart_item(request, product_id):
    cart = get_cart_session(request)
    cart.pop(str(product_id), None)
    request.session.modified = True
