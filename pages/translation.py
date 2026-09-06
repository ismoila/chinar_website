from modeltranslation.translator import register, TranslationOptions
from .models import BannerModel, ContactModel

@register(BannerModel)
class  BannerTranslationOptions(TranslationOptions):
    fields = ('title', 'header', 'description')


@register(ContactModel)
class  ContactTranslationOptions(TranslationOptions):
    fields = ('first_name', 'last_name', 'email')