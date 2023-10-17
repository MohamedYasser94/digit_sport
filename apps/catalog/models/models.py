
from django.contrib.auth import get_user_model
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.urls import reverse
from django.utils.crypto import get_random_string
from mptt.fields import TreeForeignKey
from mptt.models import MPTTModel
from slugify import slugify

from core.models.core import CommonMediaFiles
from helper.modelHelper import Active_Status, Public_Status, OutStock, VARIANTS, Publish_Status, Duration_Type, \
    Medicine_Unit, Medicine_Type
from helper.viewHelper import get_file_path

# Create your models here.


User = get_user_model()


class CatalogCategories(MPTTModel):
    parent = TreeForeignKey('self', blank=True, null=True, related_name='children', on_delete=models.CASCADE)
    title = models.CharField(max_length=20,validators=[UnicodeUsernameValidator])
    keyword = models.CharField(max_length=100, blank=True, null=True)
    image = models.ImageField(blank=True, null=True, upload_to=get_file_path)
    status = models.CharField(max_length=20, choices=Active_Status)
    code = models.CharField(max_length=50, null=True, blank=True)
    slug = models.SlugField(null=True, blank=True, max_length=128, unique=True)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    class Meta:
        # ordering = ('title',)
        verbose_name = 'category'
        # verbose_name_plural = 'categories'

    class MPTTMeta:
        order_insertion_by = ['title']

    class TranslatableMeta:
        fields = ['title', ]

    def get_absolute_url(self):
        return reverse("category_list")

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.code and not self.slug:
            self.code = f'CAT{get_random_string(5).upper()}'
            self.slug = slugify(self.title)
        super(CatalogCategories, self).save(*args, **kwargs)


class Manufacturer(models.Model):
    title = models.CharField(max_length=100,validators=[UnicodeUsernameValidator], unique=True)
    image = models.ImageField(upload_to=get_file_path, null=True,blank=True)
    code = models.CharField(max_length=50, null=True, blank=True)
    status = models.CharField(max_length=20, choices=Active_Status, default='Active')
    slug = models.SlugField(unique=True, null=True, blank=True, max_length=128)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.code and not self.slug:
            self.code = f'MAN{get_random_string(5).upper()}'
            self.slug = slugify(self.title)
        super(Manufacturer, self).save(*args, **kwargs)


class Products(models.Model):
    sender_model = models.ForeignKey(ContentType,related_name='product_sender', on_delete=models.CASCADE, null=True, blank=True)
    sender_id = models.PositiveIntegerField(null=True, blank=True)
    sender = GenericForeignKey('sender_model', 'sender_id')
    receiver_model = models.ForeignKey(ContentType, related_name='product_receiver', on_delete=models.CASCADE,
                                       null=True,
                                       blank=True)
    receiver_id = models.PositiveIntegerField(null=True, blank=True)
    receiver = GenericForeignKey('receiver_model', 'receiver_id')

    owner_model = models.ForeignKey(ContentType,related_name='product_owner', on_delete=models.CASCADE, null=True, blank=True)
    owner_id = models.PositiveIntegerField(null=True, blank=True)
    owner = GenericForeignKey('owner_model', 'owner_id')
    category = models.ForeignKey(CatalogCategories, on_delete=models.CASCADE, null=True, blank=True)
    title = models.CharField(max_length=255,validators=[UnicodeUsernameValidator], null=False, blank=False)
    keyword = models.CharField(max_length=255,validators=[UnicodeUsernameValidator], null=True, blank=True)
    body = models.TextField(blank=True,null=True)
    model = models.CharField(max_length=50, validators=[UnicodeUsernameValidator], null=True, blank=True)
    brand = models.CharField(max_length=50, validators=[UnicodeUsernameValidator], null=True, blank=True)
    sku = models.CharField(max_length=50, validators=[UnicodeUsernameValidator], null=True, blank=True)
    purchase_price = models.DecimalField(max_digits=50, decimal_places=2, default=0, null=True, blank=True)   # 100.00
    sale_price = models.DecimalField(max_digits=50, decimal_places=2, default=0, null=True, blank=True)   # 100.00
    discount_price = models.DecimalField(max_digits=50, decimal_places=2, default=0, null=True, blank=True)   # 100.00
    discount_active = models.CharField(max_length=5, choices=Public_Status, default='No',null=True, blank=True)
    final_price = models.DecimalField(max_digits=50, decimal_places=2, default=0, null=True, blank=True)   # 100.00
    quantity = models.PositiveIntegerField(default=1,null=True, blank=True)
    stock = models.PositiveIntegerField(default=1,null=True, blank=True)
    minimum_quantity = models.PositiveIntegerField(default=1,null=True, blank=True)
    subtract_stock = models.CharField(max_length=5, choices=Public_Status, default='Yes',null=True, blank=True)
    out_of_stock_status = models.CharField(max_length=20, choices=OutStock, default='2',null=True, blank=True)
    requires_shipping = models.CharField(max_length=20, default='NO', choices=Active_Status, null=True, blank=True)
    weight = models.PositiveIntegerField(default=0, null=True, blank=True)
    width = models.PositiveIntegerField(default=0, null=True, blank=True)
    height = models.PositiveIntegerField(default=0, null=True, blank=True)
    length = models.PositiveIntegerField(default=0, null=True, blank=True)
    manufacturer = models.ForeignKey(Manufacturer, on_delete=models.CASCADE, null=True,blank=True)
    featured = models.CharField(max_length=20, choices=Public_Status, default='NO', null=True, blank=True)
    status = models.CharField(max_length=20, choices=Publish_Status, null=True, blank=True, default='Active')
    unit = models.CharField(max_length=20, choices=Medicine_Unit, null=True, blank=True, default='other')
    type = models.CharField(max_length=20, choices=Medicine_Type, null=True, blank=True, default='other')
    can_return = models.CharField(max_length=20, choices=Public_Status, default='NO', null=True, blank=True)
    for_sale = models.CharField(max_length=20, choices=Public_Status, default='NO', null=True, blank=True)
    clinic_show = models.CharField(max_length=20, choices=Public_Status, default='NO', null=True, blank=True)
    order_date = models.DateField(null=True, blank=True)
    expiration_date = models.DateField(null=True, blank=True)
    sort_order = models.SmallIntegerField(default=0,null=True, blank=True)
    code = models.CharField(max_length=50, null=True, blank=True)
    slug = models.SlugField(unique=True, null=True, blank=True, max_length=128)
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('ProductDetail', args=[str(self.id)])

    @property
    def get_price(self):
        if self.discount_price and self.discount_active:
            return self.discount_price
        elif self.sale_price:
            return self.sale_price
        return self.final_price
    def get_unit(self):
        return self.unit

    def get_image(self):
        return CommonMediaFiles.objects.filter(type='hero', owner_model=ContentType.objects.get(model='Products'), owner_id=self.id)

    def save(self, *args, **kwargs):
        if not self.code and not self.slug:
            code =f'PRODUCT-{get_random_string(5).upper()}'
            self.code = code
            self.slug = slugify(code)
        super(Products, self).save(*args, **kwargs)

class ProductsStock(models.Model):
    sender_model = models.ForeignKey(ContentType,related_name='productStock_sender', on_delete=models.CASCADE, null=True, blank=True)
    sender_id = models.PositiveIntegerField(null=True, blank=True)
    sender = GenericForeignKey('sender_model', 'sender_id')
    receiver_model = models.ForeignKey(ContentType, related_name='productStock_receiver', on_delete=models.CASCADE,
                                       null=True,
                                       blank=True)
    receiver_id = models.PositiveIntegerField(null=True, blank=True)
    receiver = GenericForeignKey('receiver_model', 'receiver_id')
    owner_model = models.ForeignKey(ContentType,related_name='productStock_owner', on_delete=models.CASCADE, null=True, blank=True)
    owner_id = models.PositiveIntegerField(null=True, blank=True)
    owner = GenericForeignKey('owner_model', 'owner_id')
    title = models.CharField(max_length=255, validators=[UnicodeUsernameValidator], null=False, blank=False)
    keyword = models.CharField(max_length=255, validators=[UnicodeUsernameValidator], null=True, blank=True)
    sku = models.CharField(max_length=50, validators=[UnicodeUsernameValidator], null=True, blank=True)
    purchase_price = models.DecimalField(max_digits=50, decimal_places=2, default=0, null=True, blank=True)   # 100.00
    sale_price = models.DecimalField(max_digits=50, decimal_places=2, default=0, null=True, blank=True)   # 100.00
    discount_price = models.DecimalField(max_digits=50, decimal_places=2, default=0, null=True, blank=True)   # 100.00
    discount_active = models.CharField(max_length=5, choices=Public_Status, default='No',null=True, blank=True)
    final_price = models.DecimalField(max_digits=50, decimal_places=2, default=0, null=True, blank=True)   # 100.00
    quantity = models.PositiveIntegerField(default=1,null=True, blank=True)
    stock = models.PositiveIntegerField(default=1,null=True, blank=True)
    subtract_stock = models.CharField(max_length=5, choices=Public_Status, default='Yes',null=True, blank=True)
    out_of_stock_status = models.CharField(max_length=20, choices=OutStock, default='2',null=True, blank=True)
    manufacturer = models.ForeignKey(Manufacturer, on_delete=models.CASCADE, null=True,blank=True)
    status = models.CharField(max_length=20, choices=Publish_Status, null=True, blank=True, default='Active')
    unit = models.CharField(max_length=20, choices=Medicine_Unit, null=True, blank=True, default='other')
    type = models.CharField(max_length=20, choices=Medicine_Type, null=True, blank=True, default='other')
    can_return = models.CharField(max_length=20, choices=Public_Status, default='NO', null=True, blank=True)
    for_sale = models.CharField(max_length=20, choices=Public_Status, default='NO', null=True, blank=True)
    order_date = models.DateField(null=True, blank=True)
    expiration_date = models.DateField(null=True, blank=True)
    sort_order = models.SmallIntegerField(default=0,null=True, blank=True)

    code = models.CharField(max_length=50, null=True, blank=True)
    slug = models.SlugField(unique=True, null=True, blank=True, max_length=128)
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title



    @property
    def get_price(self):
        if self.discount_price and self.discount_active:
            return self.discount_price
        elif self.sale_price:
            return self.sale_price
        return self.final_price
    def get_unit(self):
        return self.unit



    def save(self, *args, **kwargs):
        if not self.code and not self.slug:
            code =f'ProductsStock-{get_random_string(5).upper()}'
            self.code = code
            self.slug = slugify(code)
        super(ProductsStock, self).save(*args, **kwargs)

class Variants(models.Model):

    title = models.CharField(max_length=20)
    option_type = models.CharField(max_length=20, choices=VARIANTS)
    code = models.CharField(max_length=10, blank=True, null=True)
    unit = models.ForeignKey('self', related_name='unit_variant', on_delete=models.CASCADE, blank=True, null=True, )
    unit_base = models.DecimalField(max_digits=50, decimal_places=2, default=0, null=True, blank=True)
    divided = models.CharField(max_length=5, choices=Public_Status, default='No')
    slug = models.SlugField(unique=True, null=True, blank=True, max_length=128)



    def __str__(self):
        return self.code
    def save(self, *args, **kwargs):
        if not self.slug:

            self.slug = slugify(f'VAR-{self.title}-{get_random_string(3)}')
        super(Variants, self).save(*args, **kwargs)


class UnitConversion(models.Model):
    title = models.CharField(max_length=20, null=True, blank=True)
    unit = models.CharField(max_length=20, choices=Medicine_Unit, null=True, blank=True, default='Active')
    unit_base = models.CharField(max_length=20, choices=Medicine_Unit, null=True, blank=True, default='Active')
    unit_base_value = models.DecimalField(max_digits=50, decimal_places=2, default=0, null=True, blank=True)   # 100.00
    unit_value = models.DecimalField(max_digits=50, decimal_places=2, default=0, null=True, blank=True)   # 100.00
    status = models.CharField(max_length=20, choices=Active_Status, null=True, blank=True, default='Active')
    code = models.CharField(max_length=50, null=True, blank=True)
    slug = models.SlugField(unique=True, null=True, blank=True, max_length=128)
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.code and not self.slug:
            code= f'UnitConversion-{get_random_string(5).upper()}'
            self.code = code
            self.slug = slugify(code)
        super(UnitConversion, self).save(*args, **kwargs)

class ProductVariants(models.Model):
    title = models.CharField(max_length=100, validators=[UnicodeUsernameValidator], blank=True, null=True)
    product = models.ForeignKey(Products,related_name='product_variants',related_query_name='product_variants', on_delete=models.CASCADE, null=True, blank=True)
    color = models.ForeignKey(Variants,related_name='product_color', on_delete=models.CASCADE, null=True, blank=True)
    size = models.ForeignKey(Variants,related_name='product_size', on_delete=models.CASCADE, null=True, blank=True)
    purchase_Variant = models.DecimalField(max_digits=50, decimal_places=2, default=0, null=True, blank=True)   # 100.00
    sale_Variant = models.DecimalField(max_digits=50, decimal_places=2, default=0, null=True, blank=True)   # 100.00
    discount_Variant = models.DecimalField(max_digits=50, decimal_places=2, default=0, null=True, blank=True)   # 100.00
    discount_active = models.CharField(max_length=5, choices=Public_Status, default='No')
    final_Variant = models.DecimalField(max_digits=50, decimal_places=2, default=0, null=True, blank=True)   # 100.00
    quantity = models.PositiveIntegerField(default=1)
    image =models.ImageField(upload_to=get_file_path, null=True, blank=True)
    code = models.CharField(max_length=50, null=True, blank=True)
    slug = models.SlugField(unique=True, null=True, blank=True, max_length=128)
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)



    class Meta:
        verbose_name_plural = "Variant Detail"

    def save(self, *args, **kwargs):
        if not self.code and not self.slug:
            self.code = f'VAR-{get_random_string(5).upper()}'
            self.slug = slugify(self.title)
        super(ProductVariants, self).save(*args, **kwargs)


class ProductManufacturing(models.Model):
    product = models.ForeignKey(Products,related_name='manufacture_product',related_query_name='manufacture_product', on_delete=models.PROTECT, null=True, blank=True)
    ore = models.ForeignKey(Products, related_name='ore_product', related_query_name='ore_product',on_delete=models.PROTECT, null=True, blank=True)
    unit = models.ForeignKey(Variants,related_name='manufacture_unit', on_delete=models.PROTECT, null=True, blank=True)
    ore_price = models.DecimalField(max_digits=50, decimal_places=2, default=0, null=True, blank=True)   # 100.00
    quantity = models.PositiveIntegerField(default=1)
    code = models.CharField(max_length=50, null=True, blank=True)
    slug = models.SlugField(unique=True, null=True, blank=True, max_length=128)
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)



    class Meta:
        verbose_name_plural = "Variant Detail"

    def save(self, *args, **kwargs):
        if not self.code and not self.slug:
            self.code = f'Manufacturing-{get_random_string(5).upper()}'
            self.slug = slugify(self.code)
        super(ProductManufacturing, self).save(*args, **kwargs)


class Warranty(models.Model):

    title = models.CharField(max_length=20)
    body = models.TextField(blank=True, null=True)
    duration = models.PositiveIntegerField(default=0, null=True, blank=True)
    duration_type = models.CharField(max_length=20, choices=Duration_Type, default='Days')
    status = models.CharField(max_length=20, choices=Publish_Status, null=True, default='Inactive')
    code = models.CharField(max_length=10, blank=True, null=True)


    def __str__(self):
        return self.code
class ProductQuestions(models.Model):
    product = models.ForeignKey(Products, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    question = models.TextField()
    answer = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=Active_Status)


class ProductReviews(models.Model):
    product = models.ForeignKey(Products, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    review_image = models.FileField(upload_to=get_file_path, blank=True, null=True)
    rating = models.PositiveIntegerField(blank=True, null=True)
    review = models.TextField(default="")
    ip = models.CharField(max_length=20, blank=True)
    status = models.CharField(max_length=20, choices=Active_Status, default='Yes')
    created_at = models.DateTimeField(auto_now_add=True)


class ProductReviewVoting(models.Model):
    product_review = models.ForeignKey(ProductReviews, on_delete=models.CASCADE)
    user_voting = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=Active_Status)




    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('view_warehouse', args=[self.id])

    def save(self, *args, **kwargs):
        if not self.code and not self.slug:
            warehouse_code = 'WAH-' + get_random_string(5).upper()
            self.code = warehouse_code
            self.slug = slugify(warehouse_code)
        super(ProductReviewVoting, self).save(*args, **kwargs)