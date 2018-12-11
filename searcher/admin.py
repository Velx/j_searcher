from django.contrib import admin

# Register your models here.
from searcher.models import TypeForList, TitleList, MangaTranslators, AnimeTranslators, CustomUser, TitleInProgress


class TypeAdmin(admin.ModelAdmin):
    pass


class TitleAdmin(admin.ModelAdmin):
    pass

class TitleInProgressInline(admin.TabularInline):
    model = TitleInProgress
    extra = 1 # how many rows to show

class CustomUserAdmin(admin.ModelAdmin):
    inlines = (TitleInProgressInline,)

admin.site.register(CustomUser, CustomUserAdmin)


admin.site.register(TypeForList, TypeAdmin)
admin.site.register(TitleList, TitleAdmin)