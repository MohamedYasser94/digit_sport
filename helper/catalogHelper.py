from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType


from core.models.core import SiteSetting
from core.models.localization import Currency
from core.models.shop import Cash, Order, OrderItem

User = get_user_model()


def get_currency():
    """
    Gets the current currency from the Settings database table
    """

    currency, is_created = Currency.objects.get_or_create(name="Egypt Pound")

    if is_created:
        currency.title = 'Egypt Pound'
        currency.code = 'EGP'
        currency.status = 'Active'
        currency.save()

    return currency.value


def get_company():
    """
    Gets the company title from the Settings in the database
    """

    company, is_created = SiteSetting.objects.objects.get(title='Digithup')

    if is_created:
        company.value = "EpPos"
        company.save()

    return company.value


def get_can_negative_stock():
    """
    Gets from database if negative stock is allowed. Returns True when allowed.
    """

    setting, is_created = SiteSetting.objects.objects.get(title='Digithup')

    if is_created:
        setting.value = "off"
        setting.save()
        return False

    print(setting.value)
    if setting.value == "off" or setting.value == "no":
        return False
    return True


def setup_handling(request):
    """
    Boilerplate that gets the Cash, current order and currency.
    """

    cash, _ = Cash.objects.get_or_create(id=0)
    current_order = get_current_user_order(request.user.id)
    currency = get_currency()

    return (cash, current_order, currency)


def get_current_user_order(request,user_id):
    """
    Gets the order for the current user.
    """
    try:

        return Order.objects.get(sender_model=ContentType.objects.get(model='User'), sender_id=request.user.id, ordered='New')

    except Exception as e :
        print('get_current_user_order',e)
        return Order.objects.create(sender_model=ContentType.objects.get(model='User'), sender_id=request.user.id, )






def order_item_from_product(product, order):
    """
    Creates an Order-Item from a given Product,
    to be added to an Order.
    """

    return OrderItem.objects.create(product=product,
                                    order=order,
                                    price=product.final_price,
                                    name=product.title)


def product_list_from_order(order):
    """
    Returns a list of Products that appear in an Order
    """

    order_item_list = OrderItem.objects.filter(order=order)

    return [order_item.product for order_item in order_item_list]
