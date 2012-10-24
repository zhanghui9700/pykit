from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'qfpay.views.home', name='home'),
    # url(r'^qfpay/', include('qfpay.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),


)

urlpatterns += patterns('',
    url(r'^validate-image$',"utils.validate_image.validate_image",name="new_validate_image"),
)
