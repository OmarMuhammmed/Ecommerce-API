from django.test import TestCase
from django.contrib.auth import get_user_model
from django_countries.fields import Country
from accounts.models import Profile, Address


class CustomUserModelTest(TestCase):
    def setUp(self):
        self.user_data = {
            'username': 'testuser',
            'email': 'testuser@example.com',
            'password': 'testpass123',
            'first_name': 'Test',
            'last_name': 'User'
        }
    
    def test_create_user(self):
        User = get_user_model()
        user = User.objects.create_user(**self.user_data)
        self.assertEqual(user.email, self.user_data['email'])
        self.assertEqual(user.username, self.user_data['username'])
        self.assertTrue(user.check_password(self.user_data['password']))
        self.assertFalse(user.is_staff)
        self.assertTrue(user.is_active)
    
    def test_create_superuser(self):
        User = get_user_model()
        superuser = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass123'
        )
        self.assertTrue(superuser.is_staff)
        self.assertTrue(superuser.is_superuser)
        self.assertTrue(superuser.is_active)
    
    def test_email_required(self):
        User = get_user_model()
        with self.assertRaises(ValueError):
            User.objects.create_user(username='nouser', email='')


class ProfileModelTest(TestCase):
    def test_profile_creation(self):
        User = get_user_model()
        user = User.objects.create_user(
            username='profileuser',
            email='profile@example.com',
            password='testpass123'
        )
        
        # Delete any existing profile that might have been created by signals
        Profile.objects.filter(user=user).delete()
        
        profile = Profile.objects.create(
            user=user,
            bio='This is a test bio'
        )
        
        self.assertEqual(profile.user, user)
        self.assertEqual(profile.bio, 'This is a test bio')
        self.assertTrue(profile.created_at)
        self.assertTrue(profile.updated_at)
    
    # Alternative approach using get_or_create if you prefer not to delete
    def test_profile_update(self):
        User = get_user_model()
        user = User.objects.create_user(
            username='profileuser2',
            email='profile2@example.com',
            password='testpass123'
        )
        
        profile, created = Profile.objects.get_or_create(
            user=user,
            defaults={'bio': 'This is a test bio'}
        )
        
        if not created:
            profile.bio = 'This is a test bio'
            profile.save()
        
        self.assertEqual(profile.user, user)
        self.assertEqual(profile.bio, 'This is a test bio')
        self.assertTrue(profile.created_at)
        self.assertTrue(profile.updated_at)


class AddressModelTest(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(
            username='addressuser',
            email='address@example.com',
            password='testpass123'
        )
    
    def test_address_creation(self):
        address = Address.objects.create(
            user=self.user,
            address_type=Address.BILLING,
            country=Country('EG'),
            city='Cairo',
            street_address='123 Test St',
            apartment_address='Apt 4',
            postal_code='12345'
        )
        
        self.assertEqual(address.user, self.user)
        self.assertEqual(address.address_type, Address.BILLING)
        self.assertEqual(address.country.code, 'EG')
        self.assertFalse(address.default)
    
    def test_address_type_choices(self):
        shipping_address = Address.objects.create(
            user=self.user,
            address_type=Address.SHIPPING,
            country=Country('US'),
            city='New York',
            street_address='456 Test Ave',
            apartment_address='Apt 5'
        )
        
        self.assertEqual(shipping_address.address_type, Address.SHIPPING)