from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from accounts.models import UserProfile


class UserProfileModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpass123'
        )
        self.profile = UserProfile.objects.create(
            user=self.user,
            phone='+71234567890',
            city='Москва',
            bio='Тестовый пользователь'
        )

    def test_profile_creation(self):
        """Тест создания профиля"""
        self.assertEqual(self.profile.user, self.user)
        self.assertEqual(self.profile.city, 'Москва')

    def test_profile_str(self):
        """Тест __str__ профиля"""
        self.assertEqual(str(self.profile), f'Профиль {self.user.username}')

    def test_profile_phone_valid(self):
        """Тест валидного номера телефона"""
        from django.core.exceptions import ValidationError
        self.profile.phone = '+71234567890'
        self.profile.full_clean()  # не должно выбрасывать ошибку

    def test_profile_phone_invalid(self):
        """Тест невалидного номера телефона"""
        from django.core.exceptions import ValidationError
        self.profile.phone = '89991234567'
        with self.assertRaises(ValidationError):
            self.profile.full_clean()

    def test_get_ads_count(self):
        """Тест подсчёта объявлений"""
        self.assertEqual(self.profile.get_ads_count(), 0)

    def test_one_to_one_relation(self):
        """Тест связи 1:1 с User"""
        self.assertEqual(self.user.profile, self.profile)


class RegisterViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse('accounts:register')

    def test_register_page_get(self):
        """Тест GET-запроса страницы регистрации"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/register.html')

    def test_register_valid_data(self):
        """Тест регистрации с валидными данными"""
        data = {
            'username': 'newuser',
            'email': 'new@test.com',
            'password1': 'StrongPass123!',
            'password2': 'StrongPass123!',
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username='newuser').exists())
        self.assertTrue(UserProfile.objects.filter(user__username='newuser').exists())

    def test_register_invalid_data(self):
        """Тест регистрации с невалидными данными"""
        data = {
            'username': '',
            'email': 'bad-email',
            'password1': '123',
            'password2': '456',
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(email='bad-email').exists())

    def test_register_duplicate_email(self):
        """Тест регистрации с уже существующим email"""
        User.objects.create_user(username='existing', email='dup@test.com', password='pass123')
        data = {
            'username': 'newuser2',
            'email': 'dup@test.com',
            'password1': 'StrongPass123!',
            'password2': 'StrongPass123!',
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 200)


class LoginViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse('accounts:login')
        self.user = User.objects.create_user(
            username='loginuser', password='testpass123'
        )

    def test_login_page_get(self):
        """Тест GET страницы входа"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/login.html')

    def test_login_valid_credentials(self):
        """Тест входа с правильными данными"""
        response = self.client.post(self.url, {
            'username': 'loginuser',
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, 302)

    def test_login_invalid_credentials(self):
        """Тест входа с неверными данными"""
        response = self.client.post(self.url, {
            'username': 'loginuser',
            'password': 'wrongpassword'
        })
        self.assertEqual(response.status_code, 200)

    def test_profile_requires_auth(self):
        """Тест что профиль требует авторизации"""
        response = self.client.get(reverse('accounts:profile'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response.url)

    def test_profile_accessible_when_logged_in(self):
        """Тест что профиль доступен авторизованному"""
        self.client.login(username='loginuser', password='testpass123')
        UserProfile.objects.create(user=self.user)
        response = self.client.get(reverse('accounts:profile'))
        self.assertEqual(response.status_code, 200)
