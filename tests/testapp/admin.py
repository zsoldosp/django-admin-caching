from django.contrib import admin
from django.contrib.auth.models import Group


class MyGroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'capitalized_name')
    readonly_fields = ('pk', 'capitalized_name')
    fieldsets = (
        ('editable', ['name', ]),
        ('readonly', ['pk', 'capitalized_name']),
    )

    def capitalized_name(self, obj):
        return obj.name.capitalize()


admin.site.unregister(Group)
admin.site.register(Group, MyGroupAdmin)
