from . import views
from django.urls import path

urlpatterns = [
    path('ticket_create/', views.ticket_create, name='ticket_create'),
    path('ticket_list/', views.ticket_list, name='ticket_list'),
    path('ticket_list/<str:status>', views.ticket_list_status, name='ticket_list_status'),
    path('ticket_update/<int:id>', views.ticket_update, name='ticket_update'),
    path('ticket_delete/<int:id>', views.ticket_delete, name='ticket_delete'),
    path('ticket_detail/<int:id>', views.ticket_detail, name='ticket_detail'),

    path('ticket_approve/<int:id>', views.ticket_approve, name='ticket_approve'),
    path('ticket_scoping/<int:id>', views.ticket_scoping, name='ticket_scoping'),
    path('ticket_inprogress/<int:id>', views.ticket_inprogress, name='ticket_inprogress'),
    path('ticket_completed/<int:id>', views.ticket_completed, name='ticket_completed'),
    path('ticket_reject/<int:id>', views.ticket_reject, name='ticket_reject'),
    path('ticket_cancel/<int:id>', views.ticket_cancel, name='ticket_cancel'),
    path('email_template/',views.ticket_create, name='email_template'),
    path('status_change_email_template/',views.status_change_email_function, name='tatus_change_email_template'),
    # path('worknotes_create/<int:id>',views.worknotes_create, name='worknotes_create'),
    
    # CATEGORY URLS
    path('category_create/', views.category_create, name='category_create'),
    path('category_list/', views.category_list, name='category_list'),
    path('category_delete/<int:id>', views.category_delete, name='category_delete'),

    # SUBCATEGORY URLS
    path('subcategory_create/<int:id>', views.subcategory_create, name='subcategory_create'),
    path('subcategory_list/<int:id>', views.subcategory_list, name='subcategory_list'),
    path('subcategory_delete/<int:id>', views.subcategory_delete, name='subcategory_delete'),
    
    # API
    path('ajax/load-subcategories/', views.load_subcategories, name='ajax_load_subcategories'),
]