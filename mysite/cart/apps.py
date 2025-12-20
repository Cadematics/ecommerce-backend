from django.apps import AppConfig

class CartConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'mysite.cart'

    def ready(self):
        import cart.signals
