from django.test import TestCase
from django.urls import reverse


class NavigationViewsTests(TestCase):
    def test_root_redirects_to_dashboard(self):
        response = self.client.get('/')

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], reverse('dashboard'))

    def test_dashboard_page_is_available_at_clinica_root(self):
        response = self.client.get(reverse('dashboard'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'clinica/index.html')
        self.assertContains(response, 'Panel operativo')

    def test_legacy_panel_url_redirects_to_clinica_root(self):
        response = self.client.get('/clinica/panel/')

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], reverse('dashboard'))
