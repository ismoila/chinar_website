from modeltranslation.translator import register, TranslationOptions
from .models import CategoryModel, ProductModel, FurnitureSet

@register(CategoryModel)
class  CategoryrTranslationOptions(TranslationOptions):
    fields = ('name' ,)

@register(ProductModel)
class  ProductTranslationOptions(TranslationOptions):
    fields = ('name', 'description', 'material')
    
@register(FurnitureSet)
class  FurnitureSetTranslationOptions(TranslationOptions):
    fields = ('name' ,)


# ESLATMA: ReviewModel va ReplyModel endi tarjima qilinmaydi —
# sharhlar foydalanuvchi yozgan matn, u barcha tillarda bir xil ko'rinishi kerak.
# (Avval register qilingani uchun matnlar text_uz/text_en ustunlariga tushib,
#  boshqa tillarda bo'sh ko'rinardi.)

    

from .models import ProjectModel


@register(ProjectModel)
class ProjectTranslationOptions(TranslationOptions):
    fields = ('title', 'description', 'location')
