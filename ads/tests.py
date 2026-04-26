from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from ads.models import Ad, Category, Tag, Comment, Favorite
from accounts.models import UserProfile
from decimal import Decimal


class CategoryModelTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(
            name='Электроника',
            slug='electronics',
            type='sale'
        )

    def test_category_str(self):
        self.assertEqual(str(self.category), 'Электроника (Продажа)')

    def test_category_type_choices(self):
        self.assertIn(self.category.type, ['sale', 'buy'])

    def test_category_get_absolute_url(self):
        url = self.category.get_absolute_url()
        self.assertIn('electronics', url)


class AdModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='aduser', password='pass123'
        )
        self.category = Category.objects.create(
            name='Тест', slug='test', type='sale'
        )
        self.ad = Ad.objects.create(
            title='Тестовое объявление',
            description='Описание тестового объявления',
            price=Decimal('1000.00'),
            author=self.user,
            category=self.category,
            city='Москва'
        )

    def test_ad_creation(self):
        self.assertEqual(self.ad.title, 'Тестовое объявление')
        self.assertEqual(self.ad.author, self.user)
        self.assertTrue(self.ad.is_active)

    def test_ad_str(self):
        expected = f'Тестовое объявление — {self.user.username}'
        self.assertEqual(str(self.ad), expected)

    def test_ad_default_status(self):
        self.assertEqual(self.ad.status, Ad.STATUS_ACTIVE)

    def test_ad_views_increment(self):
        initial_views = self.ad.views_count
        self.ad.increment_views()
        self.assertEqual(self.ad.views_count, initial_views + 1)

    def test_ad_price_negative_validation(self):
        from django.core.exceptions import ValidationError
        self.ad.price = Decimal('-100')
        with self.assertRaises(ValidationError):
            self.ad.full_clean()

    def test_ad_title_too_short(self):
        from django.core.exceptions import ValidationError
        self.ad.title = 'AB'
        with self.assertRaises(ValidationError):
            self.ad.full_clean()

    def test_ad_get_absolute_url(self):
        url = self.ad.get_absolute_url()
        self.assertIn(str(self.ad.pk), url)

    def test_ad_many_to_many_tags(self):
        tag = Tag.objects.create(name='б/у', slug='used')
        self.ad.tags.add(tag)
        self.assertIn(tag, self.ad.tags.all())


class CommentModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='commenter', password='pass123')
        self.author = User.objects.create_user(username='adauthor', password='pass123')
        self.category = Category.objects.create(name='Кат', slug='cat', type='sale')
        self.ad = Ad.objects.create(
            title='Объявление для теста',
            description='Описание',
            price=500,
            author=self.author,
            category=self.category
        )
        self.comment = Comment.objects.create(
            ad=self.ad,
            author=self.user,
            text='Тестовый комментарий'
        )

    def test_comment_str(self):
        self.assertIn(self.user.username, str(self.comment))
        self.assertIn(self.ad.title, str(self.comment))

    def test_comment_relation(self):
        self.assertEqual(self.comment.ad, self.ad)
        self.assertIn(self.comment, self.ad.comments.all())

    def test_comment_too_short(self):
        from django.core.exceptions import ValidationError
        self.comment.text = 'AB'
        with self.assertRaises(ValidationError):
            self.comment.full_clean()


class FavoriteModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='favuser', password='pass123')
        self.author = User.objects.create_user(username='adowner', password='pass123')
        self.ad = Ad.objects.create(
            title='Объявление',
            description='Описание',
            price=100,
            author=self.author
        )

    def test_favorite_creation(self):
        fav = Favorite.objects.create(user=self.user, ad=self.ad)
        self.assertEqual(fav.user, self.user)
        self.assertEqual(fav.ad, self.ad)

    def test_favorite_unique_together(self):
        from django.db import IntegrityError
        Favorite.objects.create(user=self.user, ad=self.ad)
        with self.assertRaises(Exception):
            Favorite.objects.create(user=self.user, ad=self.ad)

    def test_favorite_str(self):
        fav = Favorite.objects.create(user=self.user, ad=self.ad)
        self.assertIn(self.user.username, str(fav))


class AdViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='viewuser', password='pass123')
        UserProfile.objects.create(user=self.user)
        self.category = Category.objects.create(name='Кат', slug='cat-view', type='sale')
        self.ad = Ad.objects.create(
            title='Тестовое объявление',
            description='Описание для теста',
            price=999,
            author=self.user,
            category=self.category,
            is_active=True
        )

    def test_index_view_status(self):
        response = self.client.get(reverse('ads:index'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'ads/index.html')

    def test_index_shows_ads(self):
        response = self.client.get(reverse('ads:index'))
        self.assertContains(response, 'Тестовое объявление')

    def test_detail_view_status(self):
        response = self.client.get(reverse('ads:detail', kwargs={'pk': self.ad.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'ads/detail.html')

    def test_detail_view_404_for_inactive(self):
        self.ad.is_active = False
        self.ad.save()
        response = self.client.get(reverse('ads:detail', kwargs={'pk': self.ad.pk}))
        self.assertEqual(response.status_code, 404)

    def test_create_requires_login(self):
        response = self.client.get(reverse('ads:create'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response.url)

    def test_create_ad_authenticated(self):
        self.client.login(username='viewuser', password='pass123')
        response = self.client.get(reverse('ads:create'))
        self.assertEqual(response.status_code, 200)

    def test_create_ad_post(self):
        self.client.login(username='viewuser', password='pass123')
        data = {
            'title': 'Новое объявление тест',
            'description': 'Описание нового объявления',
            'price': '500.00',
            'city': 'Москва',
            'category': self.category.pk,
        }
        response = self.client.post(reverse('ads:create'), data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Ad.objects.filter(title='Новое объявление тест').exists())

    def test_edit_ad_not_owner(self):
        other_user = User.objects.create_user(username='other', password='pass123')
        self.client.login(username='other', password='pass123')
        response = self.client.get(reverse('ads:edit', kwargs={'pk': self.ad.pk}))
        self.assertEqual(response.status_code, 302)

    def test_delete_ad_owner(self):
        self.client.login(username='viewuser', password='pass123')
        response = self.client.post(reverse('ads:delete', kwargs={'pk': self.ad.pk}))
        self.assertEqual(response.status_code, 302)
        self.ad.refresh_from_db()
        self.assertFalse(self.ad.is_active)

    def test_search_by_query(self):
        response = self.client.get(reverse('ads:index'), {'query': 'Тестовое'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Тестовое объявление')

    def test_toggle_favorite_requires_login(self):
        response = self.client.post(reverse('ads:toggle_favorite', kwargs={'pk': self.ad.pk}))
        self.assertEqual(response.status_code, 302)

    def test_toggle_favorite_authenticated(self):
        self.client.login(username='viewuser', password='pass123')
        response = self.client.post(reverse('ads:toggle_favorite', kwargs={'pk': self.ad.pk}))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Favorite.objects.filter(user=self.user, ad=self.ad).exists())

    def test_favorites_view(self):
        self.client.login(username='viewuser', password='pass123')
        response = self.client.get(reverse('ads:favorites'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'ads/favorites.html')

    def test_my_ads_view(self):
        self.client.login(username='viewuser', password='pass123')
        response = self.client.get(reverse('ads:my_ads'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'ads/my_ads.html')


class AdFormTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name='Кат', slug='cat-form', type='sale')

    def test_valid_form(self):
        from ads.forms import AdForm
        data = {
            'title': 'Нормальный заголовок',
            'description': 'Нормальное описание',
            'price': '100.00',
            'city': 'Москва',
            'category': self.category.pk,
        }
        form = AdForm(data=data)
        self.assertTrue(form.is_valid())

    def test_invalid_form_empty_title(self):
        from ads.forms import AdForm
        data = {
            'title': '',
            'description': 'Описание',
            'price': '100.00',
        }
        form = AdForm(data=data)
        self.assertFalse(form.is_valid())

    def test_invalid_form_negative_price(self):
        from ads.forms import AdForm
        data = {
            'title': 'Заголовок',
            'description': 'Описание',
            'price': '-500',
        }
        form = AdForm(data=data)
        self.assertFalse(form.is_valid())
