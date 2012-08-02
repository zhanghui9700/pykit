from django.contrib import admin
from django.contrib.auth.models import User
'''
audit.admin.py
'''
class CoreDBTabularInline(admin.TabularInline):
    using = 'default'

    def queryset(self, request):
        return super(CoreDBTabularInline, self).queryset(request).using(self.using)

    def formfield_for_foreignkey(self,db_field, request=None, **kwargs):
        return super(CoreDBTabularInline,self).formfield_for_foreignkey(db_field, request=request, \
            using=self.using, **kwargs)

    def formfield_for_manytomany(self, db_field, request=None, **kwargs):
        return super(CoreDBTabularInline, self).formfield_for_manytomany(db_field, request=request,\
            using=self.using, **kwargs)

class UserInline(CoreDBTabularInline):
    model = User
   
class MisDBModelAdmin(admin.ModelAdmin):
    using = 'mis'

    def save_model(self, request, obj, form, change):
        obj.save(using = self.using)
    
    def delete_model(self, request, obj):
        obj.delete(using = self.using)

    def queryset(self,request):
        return super(MisDBModelAdmin, self).queryset(request).using(self.using)

    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        return super(MisDBModelAdmin,self).formfield_for_foreignkey(
            db_field, request=request, using = self.using, **kwargs)
    
    def formfield_for_manytomany(self, db_field, request=None, **kwargs):
        return super(MisDBModelAdmin, self).formfield_for_manytomany(
            db_field, request=request, using = self.using, **kwargs)

'''
mis.admin
'''
class CoreDBModelAdmin(admin.ModelAdmin):
    using = 'default'

    def save_model(self, request, obj, form, change):
        obj.save(using = self.using)

    def delete_model(self, request, obj):
        obj.delete(using = self.using)

    def queryset(self,request):
        return super(CoreDBModelAdmin, self).queryset(request).using(self.using)

    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        return super(CoreDBModelAdmin,self).formfield_for_foreignkey(
            db_field, request=request, using = self.using, **kwargs)

    def formfield_for_manytomany(self, db_field, request=None, **kwargs):
        return super(CoreDBModelAdmin, self).formfield_for_manytomany(
            db_field, request=request, using = self.using, **kwargs)

'''
risk.admin
'''

class MultiDBModelAdmin(admin.ModelAdmin):
    using = 'risk'

    def save_model(self, request, obj, form, change):
        obj.save(using = self.using)

    def delete_model(self, request, obj):
        obj.delete(using = self.using)

    def queryset(self,request):
        return super(MultiDBModelAdmin, self).queryset(request).using(self.using)

    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        return super(MultiDBModelAdmin,self).formfield_for_foreignkey(
            db_field, request=request, using = self.using, **kwargs)

    def formfield_for_manytomany(self, db_field, request=None, **kwargs):
        return super(MultiDBModelAdmin, self).formfield_for_manytomany(
            db_field, request=request, using = self.using, **kwargs)

'''
settle.admin
'''

class SettleDBModelAdmin(admin.ModelAdmin):
    using = 'settle'

    def save_model(self, request, obj, form, change):
        obj.save(using = self.using)

    def delete_model(self, request, obj):
        obj.delete(using = self.using)

    def queryset(self,request):
        return super(SettleDBModelAdmin, self).queryset(request).using(self.using)

    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        return super(SettleDBModelAdmin,self).formfield_for_foreignkey(
            db_field, request=request, using = self.using, **kwargs)

    def formfield_for_manytomany(self, db_field, request=None, **kwargs):
        return super(SettleDBModelAdmin, self).formfield_for_manytomany(
            db_field, request=request, using = self.using, **kwargs)

