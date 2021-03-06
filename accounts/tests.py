from cities_light.models import Country
from django.contrib.auth import get_user_model
from django.test import TestCase, Client, SimpleTestCase
from django.urls.base import reverse

from accounts.models import UserProfile


class RegistrationTestCase(TestCase, SimpleTestCase):
    def setUp(self):
        self.client = Client()
        self.user = get_user_model().objects.create_user(
            'username',
            'username@username.it',
            'u1u2u3u4'
        )
        self.tmp_user = get_user_model().objects.create_user(
            'temporary',
            'temporary@temporary.com',
            'temporary'
        )
        self.user_no_team = get_user_model().objects.create_user(
            'user_no_team',
            'user_no_team@user_no_team.com',
            'user_no_team'
        )
        self.country = Country.objects.create(name='Italy')
        UserProfile.objects.create(
            user=self.user_no_team,
            job='job',
            gender='M',
            country=self.country
        )

    #Test User Login
    def test_login(self):
        response = self.client.post(reverse('auth_login'), {
            'username': 'username',
            'password': 'u1u2u3u4',
        })
        self.assertEqual(response.status_code, 302)
        u = get_user_model().objects.get(username='username')
        self.assertEqual(int(self.client.session['_auth_user_id']), u.pk)

    # Test User Login Empty
    def test_login_empty(self):
        response = self.client.post(reverse('auth_login'), {
            'username': 'username',
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Your username and password didn\'t match.')

    # Test User Login Empty
    def test_login_wrong(self):
        response = self.client.post(reverse('auth_login'), {
            'username': 'username',
            'password': 'wrong',
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Your username and password didn\'t match.')


    # Test Reset Password
    def test_reset(self):
        response = self.client.post(reverse('auth_password_reset'), {
            'email': 'username@username.it',
        })
        self.assertEqual(response.status_code, 302)


    # Test Reset Password Empty
    def test_reset_empty(self):
        response = self.client.post(reverse('auth_password_reset'), {})
        self.assertEqual(response.status_code, 200)


    # Test User Registration
    def test_register(self):
        response = self.client.post(reverse('registration_register'), {
            'username': 'new_username',
            'email': 'newusername@newusername.it',
            'first_name': 'FirstName',
            'last_name': 'LastName',
            'password1': 'u1u2u3u4',
            'password2': 'u1u2u3u4',
            'job': 'job',
            'gender': 'M',
            'country': 1,
            'skills': 's1,s2'
        })
        # Created
        self.assertEqual(response.status_code, 302)

        u = get_user_model().objects.get(username='new_username')
        # Correct username
        self.assertEqual(u.username, 'new_username')
        # Correct email
        self.assertEqual(u.email, 'newusername@newusername.it')
        # Correct first_name
        self.assertEqual(u.first_name, 'FirstName')
        # Correct last_name
        self.assertEqual(u.last_name, 'LastName')
        # Correct Job
        self.assertEqual(u.profile.job, 'job')
        # Correct Gender
        self.assertEqual(u.profile.gender, 'M')
        # Correct country
        self.assertEqual(u.profile.country, self.country)
        # Correct skills
        self.assertEqual(u.profile.skills, 's1,s2')


    # Test User Registration Empty
    def test_register_empty(self):
        response = self.client.post(reverse('registration_register'), {})

        # Not created
        self.assertEqual(response.status_code, 200)

        # TODO: test this for all required fields
        self.assertContains(response, 'This field is required')

    # Test User Registration Security
    def test_register_noadmin(self):
        response = self.client.post(reverse('registration_register'), {
            'username': 'fake_admin',
            'email': 'fakeadmin@fakeadmin.it',
            'first_name': 'FirstName',
            'last_name': 'LastName',
            'password1': 'u1u2u3u4',
            'password2': 'u1u2u3u4',
            'job': 'job',
            'gender': 'M',
            'country': 1,
            'skills': 's1,s2',
            'is_superuser': 'True',
            'is_staff': 'True'
        })
        # Created
        self.assertEqual(response.status_code, 302)
        u = get_user_model().objects.get(username='fake_admin')

        # Not admin
        self.assertFalse(u.is_superuser)

        # Not staff
        self.assertFalse(u.is_staff)


    def test_login_without_profile(self):
        response = self.client.post(reverse('auth_login'), {
            'username': 'temporary',
            'password': 'temporary',
        })
        response = self.client.get('/')
        self.assertEqual(response.status_code, 500)


    def test_login_without_team(self):
        self.client.login(
            username='user_no_team',
            password='user_no_team'
        )
        response = self.client.get('/', follow=True)
        self.assertContains(response, 'You\'re not part of a team')


