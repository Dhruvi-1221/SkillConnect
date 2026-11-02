from django.test import TestCase, Client
from django.urls import reverse
from decimal import Decimal
from accounts.models import User, StudentProfile, Category, Skill
from posts.models import Post, PostLike, Comment
from services.models import Service
from orders.models import Order
from chat.models import Conversation, Message
from reviews.models import Review


class SkillConnectCoreTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.category = Category.objects.create(name='Photography', slug='photography')
        
        # Create student user
        self.student = User.objects.create_user(
            username='test_student',
            email='student@college.edu',
            password='password123',
            role='STUDENT'
        )
        self.student_profile = StudentProfile.objects.create(
            user=self.student,
            college_name='PDEU',
            course='B.Tech CSE',
            year_of_study='3rd Year',
            verification_status='VERIFIED'
        )

        # Create customer user
        self.customer = User.objects.create_user(
            username='test_customer',
            email='customer@college.edu',
            password='password123',
            role='CUSTOMER'
        )

        # Create admin user
        self.admin = User.objects.create_user(
            username='test_admin',
            email='admin@skillconnect.edu',
            password='password123',
            role='ADMIN',
            is_staff=True,
            is_superuser=True
        )

        # Create service
        self.service = Service.objects.create(
            student=self.student,
            category=self.category,
            title='College Event Photography',
            description='Photoshoot test description',
            price=Decimal('1000.00'),
            delivery_time_days=2,
            is_active=True
        )

    def test_landing_page_loads(self):
        res = self.client.get(reverse('landing'))
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, "Discover Skills. Connect with Students. Get Things Done.")

    def test_user_authentication_flow(self):
        # Login customer
        login_success = self.client.login(username='test_customer', password='password123')
        self.assertTrue(login_success)
        res = self.client.get(reverse('home'))
        self.assertEqual(res.status_code, 200)
        self.client.logout()

    def test_order_creation_and_tracking(self):
        self.client.login(username='test_customer', password='password123')
        order = Order.objects.create(
            customer=self.customer,
            student=self.student,
            service=self.service,
            requirements='Need photos for club fest',
            price=self.service.price,
            status='REQUESTED'
        )
        self.assertEqual(order.status, 'REQUESTED')

        # Check order detail page
        res = self.client.get(reverse('order_detail', args=[order.id]))
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, "Order #")

        # Student accepts order
        self.client.login(username='test_student', password='password123')
        can_accept = order.can_transition_to('ACCEPTED', self.student)
        self.assertTrue(can_accept)

        order.status = 'ACCEPTED'
        order.save()
        self.assertEqual(order.status, 'ACCEPTED')

    def test_chat_creation_and_polling(self):
        self.client.login(username='test_customer', password='password123')
        conv, _ = Conversation.get_or_create_conversation(self.customer, self.student)
        self.assertIsNotNone(conv)

        # Send message
        res = self.client.post(reverse('send_message_ajax', args=[conv.id]), {'content': 'Hello from customer'})
        self.assertEqual(res.status_code, 200)
        self.assertEqual(conv.messages.count(), 1)

        # Poll message
        res_poll = self.client.get(reverse('poll_messages_ajax', args=[conv.id]) + '?last_id=0')
        self.assertEqual(res_poll.status_code, 200)
        self.assertEqual(len(res_poll.json()['messages']), 1)

    def test_admin_console_access(self):
        # Non-admin access denied
        self.client.login(username='test_customer', password='password123')
        res = self.client.get(reverse('admin_dashboard'))
        self.assertEqual(res.status_code, 302)  # Redirected away

        # Admin access allowed
        self.client.login(username='test_admin', password='password123')
        res = self.client.get(reverse('admin_dashboard'))
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, "Platform Dashboard")
