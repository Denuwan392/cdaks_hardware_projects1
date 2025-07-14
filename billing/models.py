from django.db import models

class Item(models.Model):
    name = models.CharField(max_length=100, unique=True)
    price_per_kg = models.FloatField()
    description = models.TextField(blank=True, null=True)
    # image = models.ImageField(upload_to='items/', blank=True, null=True)  # Optional: for display
    available = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Transaction(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='transactions')
    weight = models.FloatField()  # in grams
    total_price = models.FloatField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if self.item and self.weight:
            self.total_price = (self.weight / 1000) * self.item.price_per_kg
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.item.name} - Rs.{self.total_price:.2f}"
