from django.db import models


class User(models.Model):
    """
    Represents a user linked to a BigCommerce store.
    """
    bc_id = models.IntegerField(unique=True, null=False)
    email = models.EmailField(max_length=120, null=False)
    
    def __str__(self):
        return f'User(id={self.id}, bc_id={self.bc_id}, email={self.email})'


class Store(models.Model):
    """
    Represents a BigCommerce store.
    """
    store_hash = models.CharField(max_length=16, unique=True, null=False)
    access_token = models.CharField(max_length=128, null=False)
    scope = models.TextField(null=False)
    
    def __str__(self):
        return f'Store(id={self.id}, store_hash={self.store_hash}, access_token={self.access_token}, scope={self.scope})'


class StoreUser(models.Model):
    """
    Represents the relationship between a user and a store.
    """
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='storeusers')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='storeusers')
    admin = models.BooleanField(default=False)
    
    def __str__(self):
        return (f'StoreUser(id={self.id}, user_email={self.user.email}, '
                f'user_id={self.user.id}, store_id={self.store.id}, admin={self.admin})')