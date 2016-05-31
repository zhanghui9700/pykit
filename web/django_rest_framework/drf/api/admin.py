from django.contrib import admin

# Register your models here.


from .models import Image, Network, Keypair, Instance


class ImageAdmin(admin.ModelAdmin):
    pass


class KeypairAdmin(admin.ModelAdmin):
    pass


class NetworkAdmin(admin.ModelAdmin):
    pass


class InstanceAdmin(admin.ModelAdmin):
    pass


admin.site.register(Image, ImageAdmin)
admin.site.register(Keypair, KeypairAdmin)
admin.site.register(Network, NetworkAdmin)
admin.site.register(Instance, InstanceAdmin)
