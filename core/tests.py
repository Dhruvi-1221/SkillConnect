from django.test import TestCase, Client
from django.urls import reverse
from decimal import Decimal
from accounts.models import User, StudentProfile, CustomerProfile, Category, Skill, Follow, Profile
from posts.models import Post, PostLike, Comment
from services.models import Service
from orders.models import Order, OrderStatusHistory
from chat.models import Conversation, Message
from reviews.models import Review
from notifications.models import Notification


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


class SkillConnectIntegrationTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.category = Category.objects.create(name='Graphic Design', slug='graphic-design')

        # Create verified student provider
        self.student = User.objects.create_user(
            username='riya_designer',
            email='riya@college.edu',
            password='password123',
            role='STUDENT',
            first_name='Riya',
            last_name='Shah'
        )
        self.student_profile = StudentProfile.objects.create(
            user=self.student,
            college_name='Nirma University',
            course='B.Des Graphic Design',
            year_of_study='3rd Year',
            verification_status='VERIFIED'
        )

        # Create customer buyer
        self.customer = User.objects.create_user(
            username='pooja_client',
            email='pooja@client.edu',
            password='password123',
            role='CUSTOMER',
            first_name='Pooja',
            last_name='Patel'
        )
        CustomerProfile.objects.create(user=self.customer)

        # Create administrator
        self.admin = User.objects.create_user(
            username='super_admin',
            email='admin@skillconnect.edu',
            password='password123',
            role='ADMIN',
            is_staff=True,
            is_superuser=True
        )

        # Create student service
        self.service = Service.objects.create(
            student=self.student,
            category=self.category,
            title='Campus Fest Poster Design',
            description='Creative digital poster and banner design in 48 hours.',
            price=Decimal('800.00'),
            delivery_time_days=2,
            is_active=True
        )

    def test_end_to_end_order_and_review_lifecycle(self):
        """
        Integration Test 1: Complete end-to-end commerce & milestone lifecycle.
        Customer books service -> Order created -> Student accepts ->
        Work progresses -> Delivery confirmed -> Review published -> Rating updated.
        """
        # Step 1: Customer books service
        self.client.login(username=self.customer.username, password='password123')
        book_res = self.client.post(
            reverse('book_service', args=[self.service.id]),
            {'requirements': 'Need a college tech fest banner and Instagram poster'}
        )
        self.assertEqual(book_res.status_code, 302)

        order = Order.objects.get(customer=self.customer, service=self.service)
        self.assertEqual(order.status, 'REQUESTED')
        self.assertEqual(order.price, Decimal('800.00'))

        # Verify audit history and notification to student
        self.assertTrue(OrderStatusHistory.objects.filter(order=order, status='REQUESTED').exists())
        self.assertTrue(Notification.objects.filter(recipient=self.student, notification_type='ORDER_REQUEST').exists())

        # Step 2: Student logs in and accepts order
        self.client.login(username=self.student.username, password='password123')
        accept_res = self.client.post(reverse('update_order_status', args=[order.id]), {'status': 'ACCEPTED'})
        self.assertEqual(accept_res.status_code, 302)
        order.refresh_from_db()
        self.assertEqual(order.status, 'ACCEPTED')

        # Step 3: Student advances to IN_PROGRESS
        self.client.post(reverse('update_order_status', args=[order.id]), {'status': 'IN_PROGRESS'})
        order.refresh_from_db()
        self.assertEqual(order.status, 'IN_PROGRESS')

        # Step 4: Student marks work READY (Ready for review)
        self.client.post(reverse('update_order_status', args=[order.id]), {'status': 'READY'})
        order.refresh_from_db()
        self.assertEqual(order.status, 'READY')

        # Step 5: Customer confirms delivery and marks COMPLETED
        self.client.login(username=self.customer.username, password='password123')
        complete_res = self.client.post(reverse('update_order_status', args=[order.id]), {'status': 'COMPLETED'})
        self.assertEqual(complete_res.status_code, 302)
        order.refresh_from_db()
        self.assertEqual(order.status, 'COMPLETED')

        # Step 6: Customer writes a 5-star review
        review_res = self.client.post(
            reverse('create_review', args=[order.id]),
            {'rating': 5, 'comment': 'Exceptional posters delivered ahead of time! Highly recommended.'}
        )
        self.assertEqual(review_res.status_code, 302)

        review = Review.objects.get(order=order)
        self.assertEqual(review.rating, 5)
        self.assertEqual(review.student, self.student)
        self.assertEqual(review.customer, self.customer)
        self.assertTrue(Notification.objects.filter(recipient=self.student, notification_type='REVIEW').exists())

        # Step 7: Prevent duplicate review for the same order
        dup_res = self.client.post(
            reverse('create_review', args=[order.id]),
            {'rating': 4, 'comment': 'Duplicate attempt'}
        )
        self.assertEqual(Review.objects.filter(order=order).count(), 1)

    def test_student_registration_and_admin_verification_workflow(self):
        """
        Integration Test 2: Student signup -> PENDING status -> Admin review ->
        VERIFIED approval -> Badge awarded -> Service creation.
        """
        # Step 1: New student registers
        reg_res = self.client.post(reverse('register'), {
            'role': 'STUDENT',
            'full_name': 'Kavya Designer',
            'username': 'kavya_design',
            'email': 'kavya@nirma.edu',
            'password': 'password123',
            'confirm_password': 'password123',
            'college_name': 'Nirma University',
            'course': 'B.Des',
            'year_of_study': '3rd Year'
        })
        self.assertEqual(reg_res.status_code, 302)

        kavya = User.objects.get(username='kavya_design')
        self.assertEqual(kavya.role, 'STUDENT')
        self.assertEqual(kavya.student_profile.verification_status, 'PENDING')
        self.assertFalse(kavya.student_profile.is_verified)

        # Step 2: Administrator inspects pending verifications
        self.client.login(username=self.admin.username, password='password123')
        verif_page = self.client.get(reverse('admin_verifications'))
        self.assertEqual(verif_page.status_code, 200)
        self.assertContains(verif_page, 'Kavya Designer')

        # Step 3: Admin approves the student
        approve_res = self.client.post(
            reverse('admin_process_verification', args=[kavya.student_profile.id]),
            {'action': 'APPROVE', 'notes': 'Verified college enrollment confirmed.'}
        )
        self.assertEqual(approve_res.status_code, 302)

        kavya.student_profile.refresh_from_db()
        self.assertEqual(kavya.student_profile.verification_status, 'VERIFIED')
        self.assertTrue(kavya.student_profile.is_verified)
        self.assertTrue(Notification.objects.filter(recipient=kavya, notification_type='VERIFICATION').exists())

        # Step 4: Approved student can create and publish services
        self.client.login(username='kavya_design', password='password123')
        srv_res = self.client.post(reverse('create_service'), {
            'title': 'UI/UX Mobile Wireframing',
            'category': self.category.id,
            'price': Decimal('1200.00'),
            'delivery_time_days': 3,
            'description': 'High-fidelity Figma wireframes for college tech projects.'
        })
        self.assertEqual(srv_res.status_code, 302)
        self.assertTrue(Service.objects.filter(student=kavya, title='UI/UX Mobile Wireframing').exists())

    def test_social_engagement_and_chat_integration(self):
        """
        Integration Test 3: Post creation -> AJAX Like -> Comment -> Follow ->
        1-on-1 Chat message exchange and live polling.
        """
        # Step 1: Student publishes a portfolio post
        post = Post.objects.create(
            student=self.student,
            category=self.category,
            caption='Brand identity designed for annual college cultural fest!'
        )

        # Step 2: Customer logs in and likes the post via AJAX
        self.client.login(username=self.customer.username, password='password123')
        like_res = self.client.post(reverse('like_toggle', args=[post.id]))
        self.assertEqual(like_res.status_code, 200)
        self.assertTrue(like_res.json()['liked'])
        self.assertEqual(like_res.json()['count'], 1)

        # Step 3: Customer comments on the post
        comment_res = self.client.post(
            reverse('add_comment', args=[post.id]),
            {'content': 'Incredible color palette and typography!'}
        )
        self.assertEqual(post.comments.count(), 1)

        # Step 4: Customer follows the student creator
        follow_res = self.client.post(reverse('ajax_follow_toggle', args=[self.student.username]))
        self.assertEqual(follow_res.status_code, 200)
        self.assertTrue(follow_res.json()['is_following'])
        self.assertTrue(Follow.objects.filter(follower=self.customer, following=self.student).exists())

        # Step 5: Direct chat exchange between Customer and Student
        conv, _ = Conversation.get_or_create_conversation(self.customer, self.student)
        
        # Customer sends message
        msg_send = self.client.post(
            reverse('send_message_ajax', args=[conv.id]),
            {'content': 'Hi Riya, are you available for a project this week?'}
        )
        self.assertEqual(msg_send.status_code, 200)

        # Student logs in, polls for new messages
        self.client.login(username=self.student.username, password='password123')
        poll_res = self.client.get(reverse('poll_messages_ajax', args=[conv.id]) + '?last_id=0')
        self.assertEqual(poll_res.status_code, 200)
        messages_received = poll_res.json()['messages']
        self.assertEqual(len(messages_received), 1)
        self.assertEqual(messages_received[0]['content'], 'Hi Riya, are you available for a project this week?')

        # Student replies
        reply_send = self.client.post(
            reverse('send_message_ajax', args=[conv.id]),
            {'content': 'Yes! Please book the service with your requirements.'}
        )
        self.assertEqual(reply_send.status_code, 200)
        self.assertEqual(conv.messages.count(), 2)

    def test_security_and_permission_boundaries_integration(self):
        """
        Integration Test 4: Security gates & unauthorized state transitions.
        Ensures strict boundary checks across different roles.
        """
        order = Order.objects.create(
            customer=self.customer,
            student=self.student,
            service=self.service,
            requirements='Security boundary verification order',
            price=self.service.price,
            status='REQUESTED'
        )

        # Rule 1: Customer CANNOT accept their own order (only student can)
        self.client.login(username=self.customer.username, password='password123')
        self.client.post(reverse('update_order_status', args=[order.id]), {'status': 'ACCEPTED'})
        order.refresh_from_db()
        self.assertEqual(order.status, 'REQUESTED')  # Status must remain unchanged!

        # Rule 2: Student CANNOT mark an in-progress order COMPLETED (only customer confirms completion)
        self.client.login(username=self.student.username, password='password123')
        order.status = 'IN_PROGRESS'
        order.save()
        self.client.post(reverse('update_order_status', args=[order.id]), {'status': 'COMPLETED'})
        order.refresh_from_db()
        self.assertEqual(order.status, 'IN_PROGRESS')  # Status must remain unchanged!

        # Rule 3: Third-party stranger CANNOT view someone else's order
        stranger = User.objects.create_user(username='random_stranger', password='password123', role='CUSTOMER')
        self.client.login(username='random_stranger', password='password123')
        stranger_res = self.client.get(reverse('order_detail', args=[order.id]))
        self.assertEqual(stranger_res.status_code, 403)  # Forbidden!

        # Rule 4: Customer CANNOT review an order before it is COMPLETED
        self.client.login(username=self.customer.username, password='password123')
        premature_rev = self.client.post(
            reverse('create_review', args=[order.id]),
            {'rating': 5, 'comment': 'Trying to review while IN_PROGRESS'}
        )
        self.assertFalse(Review.objects.filter(order=order).exists())
