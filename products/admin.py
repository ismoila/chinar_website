from django.contrib import admin
import nested_admin
from .models import (
    # CartItem,
    CategoryModel,
    IdeaModel,
    IdeaPinModel,
    ProductColorImageModel,
    ProductColorModel,
    ProfileModel,
    ReplyModel,
    SizeModel,
    ColorModel,
    ProductModel,
    WishlistModel,
    ProductImage,
    # Project,
    # ProjectImages,
)

from django import forms
from django.forms.models import ModelChoiceIterator


class ColorImgSelect(forms.Select):
    """Rang tanlovi: har bir variant yoniga rang rasmi/kvadratini chiqaradi."""

    class Media:
        css = {'all': ('admin/color_select.css',)}
        js = ('admin/color_select.js',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        attrs = self.attrs or {}
        cls = (attrs.get('class', '') + ' color-img-select').strip()
        attrs['class'] = cls
        self.attrs = attrs
        self._color_cache = None

    def _colors(self):
        if self._color_cache is None:
            self._color_cache = {c.pk: c for c in ColorModel.objects.all()}
        return self._color_cache

    def create_option(self, name, value, label, selected, index, subindex=None, attrs=None):
        opt = super().create_option(name, value, label, selected, index, subindex=subindex, attrs=attrs)
        pk = getattr(value, 'value', value)
        if pk:
            c = self._colors().get(pk)
            if c is not None:
                opt['attrs']['data-img'] = c.image.url if c.image else ''
                opt['attrs']['data-code'] = c.code or ''
        return opt


class GroupedColorChoiceIterator(ModelChoiceIterator):
    """Colors tanlovini kategoriya (optgroup) bo'yicha guruhlaydi."""
    def __iter__(self):
        if self.field.empty_label is not None:
            yield ("", self.field.empty_label)
        for key, label in ColorModel.GROUP_CHOICES:
            qs = self.queryset.filter(group=key).order_by('name')
            if qs.exists():
                yield (label, [self.choice(c) for c in qs])


@admin.register(CategoryModel)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name']

@admin.register(SizeModel)
class SizeAdmin(admin.ModelAdmin):
    list_display = ['title']

@admin.register(ColorModel)
class ColorAdmin(admin.ModelAdmin):
    change_list_template = 'admin/products/colormodel/change_list.html'
    list_display = ['color_preview', 'name', 'code', 'group']
    list_display_links = ['name']
    list_filter = ['group']
    ordering = ['group', 'name']
    readonly_fields = ['color_preview_big']
    fields = ['name', 'code', 'group', 'color_preview_big', 'image']

    @admin.display(description="Rang")
    def color_preview(self, obj):
        from django.utils.html import format_html
        if obj.image:
            return format_html(
                '<img src="{}" style="width:34px;height:34px;border-radius:50%;'
                'object-fit:cover;border:1px solid #ccc;" />', obj.image.url)
        return format_html(
            '<span style="display:inline-block;width:34px;height:34px;'
            'border-radius:50%;background:{};border:1px solid #ccc;"></span>',
            obj.code or '#ffffff')

    @admin.display(description="Rang ko'rinishi")
    def color_preview_big(self, obj):
        from django.utils.html import format_html
        if obj.image:
            return format_html(
                '<img src="{}" style="width:90px;height:90px;border-radius:50%;'
                'object-fit:cover;border:1px solid #ccc;" />', obj.image.url)
        return format_html(
            '<span style="display:inline-block;width:90px;height:90px;'
            'border-radius:50%;background:{};border:1px solid #ccc;"></span>',
            obj.code or '#ffffff')

    def changelist_view(self, request, extra_context=None):
        groups = []
        for key, label in ColorModel.GROUP_CHOICES:
            items = list(ColorModel.objects.filter(group=key).order_by('name'))
            if items:
                groups.append({'label': label, 'colors': items})
        extra_context = {**(extra_context or {}), 'color_groups': groups}
        return super().changelist_view(request, extra_context=extra_context)

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 4
    fields = ['image', 'order']

class ProductImageInline(nested_admin.NestedTabularInline):
    model = ProductImage
    extra = 4
    fields = ['image', 'order']

class ProductColorImageInline(nested_admin.NestedTabularInline):
    model = ProductColorImageModel
    extra = 2

class ProductColorInline(nested_admin.NestedStackedInline):
    model = ProductColorModel
    extra = 1
    inlines = [ProductColorImageInline]

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'color':
            kwargs['widget'] = ColorImgSelect()
        field = super().formfield_for_foreignkey(db_field, request, **kwargs)
        if db_field.name == 'color':
            # Color tanlovi kategoriya bo'yicha guruhlanadi (To'qima / Arqon / Rattan / Mato)
            field.iterator = GroupedColorChoiceIterator
            # widget'dagi eski (guruhsiz) choices'ni yangilaymiz
            field.widget.choices = field.choices
            inner = getattr(field.widget, 'widget', None)
            if inner is not None:
                inner.choices = field.choices
        return field

@admin.register(ProductModel)
class ProductAdmin(nested_admin.NestedModelAdmin):
    inlines = [ProductImageInline, ProductColorInline]
    list_display = ['name', 'category', 'price', 'in_stock', 'tavsif_bormi', 'discount', 'discount_days', 'discount_end', 'is_discount_active']
    list_editable = ['in_stock', 'discount', 'discount_days']
    readonly_fields = ['discount_start', 'discount_end']
    # ── Kategoriya bo'yicha bo'lish ──
    list_filter = ['category', 'in_stock']      # o'ng panelda kategoriya va ombor filtri
    ordering = ['category__name', 'name']       # ro'yxat kategoriya bo'yicha guruhlanib turadi
    search_fields = ['name']                    # tepada qidiruv
    list_per_page = 40

    def tavsif_bormi(self, obj):
        """Ro'yxatda ko'rinadi — qaysi mahsulotga tavsif yozilmaganini bilish uchun"""
        return bool((obj.description or '').strip())
    tavsif_bormi.boolean = True
    tavsif_bormi.short_description = 'Tavsif'

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        field = super().formfield_for_manytomany(db_field, request, **kwargs)
        if db_field.name == 'colors':
            field.iterator = GroupedColorChoiceIterator
            field.widget.choices = field.choices
            inner = getattr(field.widget, 'widget', None)
            if inner is not None:
                inner.choices = field.choices
        return field

    def is_discount_active(self, obj):
        return obj.is_discount_active
    is_discount_active.boolean = True
    is_discount_active.short_description = 'Active?'

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields['price'].help_text = "Narxni USD (dollar)da kiriting — saytda avtomatik so'mga aylanadi"
        return form
@admin.register(WishlistModel)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ['user', 'product']
    

from .models import FurnitureSet, FurnitureSetProduct

class FurnitureSetProductInline(admin.TabularInline):
    model = FurnitureSetProduct
    extra = 3
    fields = ['product', 'order']

@admin.register(FurnitureSet)
class FurnitureSetAdmin(admin.ModelAdmin):
    inlines = [FurnitureSetProductInline]
    list_display = ['name', 'order', 'is_active']
    list_editable = ['order', 'is_active']
    
    
# class ProjectImagesInline(admin.TabularInline):
#     model = ProjectImages
#     extra = 4
#     fields = ['image', 'order']

# @admin.register(Project)
# class ProjectAdmin(admin.ModelAdmin):
#     inlines = [ProjectImagesInline]
#     list_display = ['name', 'category', 'year', 'order', 'is_active']
#     list_editable = ['order', 'is_active']

@admin.register(ProfileModel)
class ProfileAdmin(admin.ModelAdmin):
    list_display = [
        "phone",
        "first_name",
        "last_name",
        "email",
        "gender",
        "date_of_birth",
    ]
    def get_queryset(self, request):
        return super().get_queryset(request).exclude(user__is_superuser=True)
    
    
from .models import ReviewModel

@admin.register(ReviewModel)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['name', 'product', 'rating', 'created_at']
    list_filter = ['rating']
    
    
@admin.register(ReplyModel)
class ReplyAdmin(admin.ModelAdmin):
    list_display = ['name', 'review', 'created_at']
    search_fields = ['name']
    

# @admin.register(CartItem)
# class CartItemAdmin(admin.ModelAdmin):
#     list_display = ['user', 'product', 'quantity', 'created_at']


class IdeaPinInline(admin.TabularInline):
    model = IdeaPinModel
    extra = 1

@admin.register(IdeaModel)
class IdeaAdmin(admin.ModelAdmin):
    list_display = ['id', 'order']
    inlines = [IdeaPinInline]

from products.models import Order, OrderItem   # yoki pages.models — qayerda bo'lsa


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['product', 'quantity', 'price', 'size', 'color']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_id', 'user', 'first_name', 'total_price', 'status', 'payment_status', 'created_at']
    list_filter = ['status', 'payment_status', 'delivery_method', 'created_at']
    search_fields = ['order_id', 'first_name', 'last_name', 'phone']
    readonly_fields = ['order_id', 'created_at', 'updated_at']
    inlines = [OrderItemInline]

from products.models import PromoCode, PaymentTransaction

@admin.register(PromoCode)
class PromoCodeAdmin(admin.ModelAdmin):
    list_display = ['code', 'discount_percent', 'is_active', 'valid_until', 'max_uses', 'used_count']
    list_editable = ['is_active']
    search_fields = ['code']


@admin.register(PaymentTransaction)
class PaymentTransactionAdmin(admin.ModelAdmin):
    list_display = ['provider', 'trans_id', 'order', 'amount', 'state', 'created_at', 'perform_time']
    list_filter = ['provider', 'state']
    search_fields = ['trans_id', 'order__order_id']
    readonly_fields = ['provider', 'trans_id', 'order', 'amount', 'state',
                       'reason', 'created_at', 'perform_time', 'cancel_time']


# ═══ Mahsulot o'lcham-narxlari (admin'da mahsulot ichida tahrirlanadi) ═══
from products.models import ProductSizePrice

class ProductSizePriceInline(nested_admin.NestedTabularInline):
    model = ProductSizePrice
    extra = 1
    fields = ['title', 'price', 'order']

ProductAdmin.inlines = list(ProductAdmin.inlines) + [ProductSizePriceInline]


from .models import CallbackRequestModel


@admin.register(CallbackRequestModel)
class CallbackRequestAdmin(admin.ModelAdmin):
    list_display = ('phone', 'created_at', 'handled')
    list_editable = ('handled',)
    list_filter = ('handled',)
    search_fields = ('phone',)


from .models import ProjectModel, ProjectImageModel


class ProjectImageInline(admin.TabularInline):
    model = ProjectImageModel
    extra = 3
    fields = ('image', 'order')


@admin.register(ProjectModel)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'kind', 'location', 'year', 'is_active', 'order')
    list_editable = ('is_active', 'order')
    list_filter = ('kind', 'is_active')
    search_fields = ('title', 'location')
    filter_horizontal = ('products',)
    inlines = [ProjectImageInline]
