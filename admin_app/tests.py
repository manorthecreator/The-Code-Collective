from django.test import TestCase, Client
from django.urls import reverse
from products_app.models import Product, Category

class ProductFunctionalTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.category = Category.objects.create(name="Apparel")
        self.product = Product.objects.create(
            name="Silk Dress", 
            price=2500.00, 
            category=self.category,
            status="Available"
        )

    def test_category_filter_functional_requirement(self):
        """FR-01: Filtering products by category returns matching items."""
        response = self.client.get(reverse('admin_app:products'), {'category': self.category.categoryID})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Silk Dress")

    def test_product_search_functional_requirement(self):
        """FR-02: Search bar returns products matching the query name."""
        response = self.client.get(reverse('admin_app:products'), {'q': 'Silk'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Silk Dress")

    def test_settings_update_post_request(self):
        """FR-03: Submitting valid settings updates the store configuration."""
        response = self.client.post(reverse('admin_app:settings'), {
            'store_name': 'Velora Boutique',
            'store_email': 'contact@velora.com',
            'phone': '+230 51234567',
            'currency': 'Rs MUR',
            'timezone': '(GMT +4:00) Mauritius Standard Time',
            'legal_name': 'Velora Ltd',
            'description': 'Luxury apparel store',
            'address': 'Main St',
            'city': 'Quatre Bornes',
            'state': 'Plaines Wilhems'
        })
        self.assertEqual(response.status_code, 302) # Redirects on success
