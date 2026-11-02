import os
import sys
import django
from decimal import Decimal
from django.utils import timezone
from PIL import Image, ImageDraw, ImageFont

# Initialize Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'skillconnect.settings')
django.setup()

from django.core.files.base import ContentFile
import io

from accounts.models import User, Profile, StudentProfile, CustomerProfile, Category, Skill, Follow
from posts.models import Post, PostLike, Comment
from services.models import Service
from orders.models import Order, OrderStatusHistory
from chat.models import Conversation, Message
from reviews.models import Review
from notifications.models import Notification


def create_solid_image(text, bg_color=(79, 70, 229), size=(800, 600)):
    """Generates an aesthetic branded image using Pillow."""
    img = Image.new('RGB', size, color=bg_color)
    draw = ImageDraw.Draw(img)
    
    # Draw simple decorative grid or pattern
    for x in range(0, size[0], 40):
        draw.line([(x, 0), (x, size[1])], fill=(bg_color[0]+15, bg_color[1]+15, min(255, bg_color[2]+15)), width=1)
    for y in range(0, size[1], 40):
        draw.line([(0, y), (size[0], y)], fill=(bg_color[0]+15, bg_color[1]+15, min(255, bg_color[2]+15)), width=1)

    # Draw centered badge/box
    box_w, box_h = size[0] * 0.75, 120
    box_x0 = (size[0] - box_w) / 2
    box_y0 = (size[1] - box_h) / 2
    draw.rounded_rectangle([box_x0, box_y0, box_x0 + box_w, box_y0 + box_h], radius=16, fill=(255, 255, 255))

    # Add text label (default font)
    # Estimate center
    draw.text((box_x0 + 30, box_y0 + 45), text, fill=(15, 23, 42))

    buf = io.BytesIO()
    img.save(buf, format='JPEG', quality=90)
    return ContentFile(buf.getvalue())


def run():
    print("Populating SkillConnect database with sample demo data...")

    # 1. Categories
    categories_data = [
        ('Photography', 'photography', 'Camera, portrait, event, and product photography', 'camera'),
        ('Graphic Design', 'graphic-design', 'Posters, logos, fest branding, and digital illustration', 'brush'),
        ('Web Development', 'web-development', 'Front-end, Django, prototypes, and bug fixes', 'code'),
        ('Mehndi & Henna', 'mehndi', 'Bridal, festive, Arabic, and creative henna art', 'sparkles'),
        ('Makeup & Styling', 'makeup', 'Event makeup, personal styling, and hair design', 'palette'),
        ('Tutoring & Academics', 'tutoring', 'Coding, mathematics, physics, and exam prep', 'book'),
        ('Video Editing', 'video-editing', 'Reels, YouTube editing, fest teasers, and montages', 'film'),
        ('Art & Painting', 'art', 'Canvas painting, sketches, digital art, and portraits', 'brush'),
        ('Baking & Cakes', 'baking', 'Custom campus cakes, cookies, and sweet treats', 'cake'),
        ('Music & Audio', 'music', 'Guitar, vocals, mixing, and audio production', 'music'),
        ('Dance & Choreography', 'dance', 'College fest choreography and group dances', 'music'),
        ('Handmade Products', 'handmade-products', 'Crochet, scented candles, campus merchandise', 'gift'),
    ]

    cats = {}
    for name, slug, desc, icon in categories_data:
        cat, _ = Category.objects.get_or_create(
            name=name,
            defaults={'slug': slug, 'description': desc, 'icon': icon, 'is_active': True}
        )
        cats[slug] = cat

    print("Categories initialized.")

    # 2. Skills
    skills_data = [
        ('photography', ['Portrait Photography', 'Event Photography', 'Lightroom Color Grading', 'Product Shoots']),
        ('graphic-design', ['Fest Poster Design', 'Logo & Branding', 'Social Media Graphics', 'UI/UX Mockups']),
        ('web-development', ['Django Web Apps', 'HTML/CSS/JS', 'Python Scripting', 'API Integration']),
        ('mehndi', ['Arabic Mehndi', 'Bridal Henna', 'Minimalist Mehndi', 'Festive Henna']),
        ('makeup', ['Party Makeup', 'Hairstyling', 'Natural Everyday Look', 'Photoshoot Makeup']),
        ('tutoring', ['Data Structures & Algorithms', 'Calculus & Linear Algebra', 'Python Programming', 'Physics']),
        ('video-editing', ['Instagram Reels', 'After Effects Motion Graphics', 'YouTube Video Editing']),
    ]

    skills_dict = {}
    for cat_slug, skill_names in skills_data:
        cat = cats.get(cat_slug)
        for sname in skill_names:
            sk, _ = Skill.objects.get_or_create(category=cat, name=sname)
            skills_dict[sname] = sk

    # 3. Admin Account
    admin_user, created = User.objects.get_or_create(
        username='admin',
        defaults={
            'email': 'admin@skillconnect.edu',
            'first_name': 'SkillConnect',
            'last_name': 'Administrator',
            'role': 'ADMIN',
            'is_staff': True,
            'is_superuser': True,
        }
    )
    if created:
        admin_user.set_password('admin123')
        admin_user.save()
        Profile.objects.create(user=admin_user, bio='SkillConnect Platform Lead Administrator')

    print("Admin user: admin / admin123 created.")

    # 4. Students
    students_info = [
        {
            'username': 'aarav_patel',
            'email': 'aarav.patel@pdpu.ac.in',
            'first_name': 'Aarav',
            'last_name': 'Patel',
            'college': 'Pandit Deendayal Energy University (PDEU)',
            'course': 'B.Tech Computer Science',
            'year': '3rd Year',
            'skills': ['Portrait Photography', 'Event Photography', 'Lightroom Color Grading'],
            'bio': 'Passionate photographer & CSE student capturing events, fest moments, and cinematic portraits.',
            'status': 'VERIFIED',
            'bg': (30, 64, 175)
        },
        {
            'username': 'riya_shah',
            'email': 'riya.shah@pdpu.ac.in',
            'first_name': 'Riya',
            'last_name': 'Shah',
            'college': 'Pandit Deendayal Energy University (PDEU)',
            'course': 'B.Des Industrial & Communication Design',
            'year': '2nd Year',
            'skills': ['Fest Poster Design', 'Logo & Branding', 'Social Media Graphics'],
            'bio': 'Graphic designer crafting modern event posters, club branding, and visual identity.',
            'status': 'VERIFIED',
            'bg': (124, 58, 237)
        },
        {
            'username': 'krisha_mehta',
            'email': 'krisha.mehta@pdpu.ac.in',
            'first_name': 'Krisha',
            'last_name': 'Mehta',
            'college': 'PDEU School of Liberal Studies',
            'course': 'B.A. Psychology',
            'year': 'Final Year',
            'skills': ['Arabic Mehndi', 'Bridal Henna', 'Festive Henna'],
            'bio': 'Self-taught henna artist specializing in intricate organic mehndi for campus events and weddings.',
            'status': 'VERIFIED',
            'bg': (180, 83, 9)
        },
        {
            'username': 'dev_shah',
            'email': 'dev.shah@pdpu.ac.in',
            'first_name': 'Dev',
            'last_name': 'Shah',
            'college': 'Pandit Deendayal Energy University (PDEU)',
            'course': 'B.Tech Information & Communication Tech',
            'year': '4th Year',
            'skills': ['Django Web Apps', 'Python Programming', 'HTML/CSS/JS'],
            'bio': 'Full-stack developer building practical web tools, student portals, and clean web applications.',
            'status': 'VERIFIED',
            'bg': (13, 148, 136)
        },
        {
            'username': 'anaya_patel',
            'email': 'anaya.patel@pdpu.ac.in',
            'first_name': 'Anaya',
            'last_name': 'Patel',
            'college': 'PDEU School of Management',
            'course': 'BBA General Management',
            'year': '2nd Year',
            'skills': ['Party Makeup', 'Hairstyling', 'Natural Everyday Look'],
            'bio': 'Certified student makeup enthusiast helping campus peers get ready for parties, fests, and graduations.',
            'status': 'VERIFIED',
            'bg': (219, 39, 119)
        },
        {
            'username': 'rohan_joshi',
            'email': 'rohan.joshi@pdpu.ac.in',
            'first_name': 'Rohan',
            'last_name': 'Joshi',
            'college': 'Pandit Deendayal Energy University (PDEU)',
            'course': 'B.Tech Mechanical Engineering',
            'year': '1st Year',
            'skills': ['Instagram Reels', 'YouTube Video Editing'],
            'bio': 'First year videographer building campus reels and music video montages.',
            'status': 'PENDING',  # Showcase pending state in Admin
            'bg': (71, 85, 105)
        }
    ]

    student_users = {}
    for s in students_info:
        user, ucreated = User.objects.get_or_create(
            username=s['username'],
            defaults={
                'email': s['email'],
                'first_name': s['first_name'],
                'last_name': s['last_name'],
                'role': 'STUDENT'
            }
        )
        if ucreated:
            user.set_password('student123')
            user.save()

        student_users[s['username']] = user

        # Profile
        prof, _ = Profile.objects.get_or_create(user=user)
        prof.bio = s['bio']
        prof.save()

        # Student Profile
        sprof, _ = StudentProfile.objects.get_or_create(
            user=user,
            defaults={
                'college_name': s['college'],
                'course': s['course'],
                'year_of_study': s['year'],
                'verification_status': s['status'],
                'is_available': True,
                'verification_notes': 'College identity card and enrollment confirmed.' if s['status'] == 'VERIFIED' else 'Awaiting review of submitted student credentials.'
            }
        )
        # Assign skills
        for sk_name in s['skills']:
            if sk_name in skills_dict:
                sprof.skills.add(skills_dict[sk_name])

    print("Student profiles initialized.")

    # 5. Customer Account
    cust_user, ccreated = User.objects.get_or_create(
        username='neha_customer',
        defaults={
            'email': 'neha.customer@example.com',
            'first_name': 'Neha',
            'last_name': 'Sharma',
            'role': 'CUSTOMER'
        }
    )
    if ccreated:
        cust_user.set_password('customer123')
        cust_user.save()
        cprof = Profile.objects.create(user=cust_user, bio='Event Coordinator for College Youth Club & cultural festivals.')
        CustomerProfile.objects.create(user=cust_user, organization_or_event='PDEU Cultural Committee')
        # Select sample interests
        cprof.interests.add(cats['photography'], cats['graphic-design'], cats['mehndi'])

    print("Customer user: neha_customer / customer123 created.")

    # 6. Sample Posts
    posts_data = [
        {
            'student': student_users['aarav_patel'],
            'category': cats['photography'],
            'caption': 'Captured creative golden hour portrait photography on campus quad. Lighting and shadows came out magical!',
            'tags': 'Photography, Portrait, GoldenHour, Campus',
            'text': 'Aarav Patel - Golden Hour Portrait'
        },
        {
            'student': student_users['riya_shah'],
            'category': cats['graphic-design'],
            'caption': 'Designed this minimal geometric event poster for the annual inter-college technical hackathon.',
            'tags': 'PosterDesign, GraphicDesign, Minimalist, Typography',
            'text': 'Riya Shah - Fest Poster Design'
        },
        {
            'student': student_users['krisha_mehta'],
            'category': cats['mehndi'],
            'caption': 'Intricate Arabic peacock henna pattern crafted for a cultural festival performance. Dried organic henna stain.',
            'tags': 'Mehndi, HennaArt, ArabicDesign, Traditional',
            'text': 'Krisha Mehta - Arabic Henna Art'
        },
        {
            'student': student_users['dev_shah'],
            'category': cats['web-development'],
            'caption': 'Built a responsive modern portal with clean typography and fast search. Clean code and responsive UI.',
            'tags': 'WebDevelopment, Django, Python, CleanCode',
            'text': 'Dev Shah - Web Application Prototype'
        },
        {
            'student': student_users['anaya_patel'],
            'category': cats['makeup'],
            'caption': 'Festive glam makeup look with soft tones and winged eyeliner. Prepared for college annual gala night.',
            'tags': 'Makeup, GlamLook, CampusStyle, Styling',
            'text': 'Anaya Patel - Festive Glam Styling'
        },
    ]

    created_posts = []
    for p in posts_data:
        existing = Post.objects.filter(student=p['student'], caption=p['caption']).first()
        if not existing:
            img_file = create_solid_image(p['text'], bg_color=(79, 70, 229))
            post = Post(
                student=p['student'],
                category=p['category'],
                caption=p['caption'],
                skill_tags=p['tags'],
                is_active=True
            )
            post.image.save(f"post_{p['student'].username}.jpg", img_file, save=True)
            created_posts.append(post)
        else:
            created_posts.append(existing)

    print("Sample posts created.")

    # Likes & Comments
    if created_posts:
        p0 = created_posts[0]
        PostLike.objects.get_or_create(post=p0, user=cust_user)
        Comment.objects.get_or_create(post=p0, user=cust_user, defaults={'content': 'Looks incredible Aarav! Bookmarking for our upcoming cultural fest photoshoot.'})
        Comment.objects.get_or_create(post=p0, user=student_users['riya_shah'], defaults={'content': 'The lighting and tones are stunning!'})

    # 7. Sample Services
    services_data = [
        {
            'student': student_users['aarav_patel'],
            'category': cats['photography'],
            'title': 'Birthday & Event Photography Session',
            'description': 'I provide 2-hour event coverage with DSLR camera, 25 high-resolution professionally edited digital photographs, and raw photos delivered via Google Drive within 2 days.',
            'price': Decimal('1500.00'),
            'days': 2,
            'text': 'Event Photography - ₹1500'
        },
        {
            'student': student_users['riya_shah'],
            'category': cats['graphic-design'],
            'title': 'College Fest & Social Media Poster Design',
            'description': 'Eye-catching posters for club events, fests, or business campaigns. High-resolution print-ready PDF and Instagram dimension graphics with 2 rounds of revisions.',
            'price': Decimal('400.00'),
            'days': 1,
            'text': 'Poster Design - ₹400'
        },
        {
            'student': student_users['krisha_mehta'],
            'category': cats['mehndi'],
            'title': 'Arabic & Bridal Henna Application',
            'description': 'Traditional or modern Arabic mehndi designs for both hands using 100% natural organic henna cones. Long-lasting dark stain guaranteed.',
            'price': Decimal('800.00'),
            'days': 1,
            'text': 'Organic Mehndi - ₹800'
        },
        {
            'student': student_users['dev_shah'],
            'category': cats['web-development'],
            'title': '1-on-1 Python & Web Development Mentoring',
            'description': 'One-hour practical live coding session covering Python basics, Django models, views, or debugging your college coursework projects.',
            'price': Decimal('500.00'),
            'days': 1,
            'text': 'Coding Mentoring - ₹500'
        },
        {
            'student': student_users['anaya_patel'],
            'category': cats['makeup'],
            'title': 'Party Makeup & Hair Styling',
            'description': 'Full face makeup for farewells, parties, and campus events. Includes skin prep, long-lasting base, eye look, and basic hair styling.',
            'price': Decimal('1200.00'),
            'days': 1,
            'text': 'Party Makeup - ₹1200'
        },
    ]

    created_services = []
    for s in services_data:
        srv = Service.objects.filter(student=s['student'], title=s['title']).first()
        if not srv:
            img_file = create_solid_image(s['text'], bg_color=(14, 165, 233))
            srv = Service(
                student=s['student'],
                category=s['category'],
                title=s['title'],
                description=s['description'],
                price=s['price'],
                delivery_time_days=s['days'],
                is_active=True
            )
            srv.image.save(f"srv_{s['student'].username}.jpg", img_file, save=True)
        created_services.append(srv)

    print("Sample services created.")

    # 8. Sample Orders & Reviews
    if created_services:
        s0 = created_services[0]  # Aarav's photography
        ord1, ocreated = Order.objects.get_or_create(
            order_number='ORD-1024',
            defaults={
                'customer': cust_user,
                'student': s0.student,
                'service': s0,
                'requirements': 'Need photography coverage for my friend birthday party on campus lawn from 5 PM to 7 PM.',
                'preferred_date': timezone.now().date(),
                'price': s0.price,
                'status': 'COMPLETED'
            }
        )
        if ocreated:
            OrderStatusHistory.objects.create(order=ord1, status='REQUESTED', note='Order requested', changed_by=cust_user)
            OrderStatusHistory.objects.create(order=ord1, status='ACCEPTED', note='Order accepted by Aarav', changed_by=s0.student)
            OrderStatusHistory.objects.create(order=ord1, status='IN_PROGRESS', note='Photoshoot conducted', changed_by=s0.student)
            OrderStatusHistory.objects.create(order=ord1, status='READY', note='Edited photos sent', changed_by=s0.student)
            OrderStatusHistory.objects.create(order=ord1, status='COMPLETED', note='Completed by customer', changed_by=cust_user)

            # Add Review
            Review.objects.create(
                order=ord1,
                customer=cust_user,
                student=s0.student,
                rating=5,
                comment='Very professional and delivered on time! Aarav captured beautiful candid memories of our birthday celebration. Highly recommended!'
            )

        # Order 2: In Progress
        s1 = created_services[1]  # Riya's poster design
        ord2, o2created = Order.objects.get_or_create(
            order_number='ORD-1025',
            defaults={
                'customer': cust_user,
                'student': s1.student,
                'service': s1,
                'requirements': 'Need an A3 poster design for our college coding club upcoming hackathon. Blue and purple palette preferred.',
                'preferred_date': timezone.now().date(),
                'price': s1.price,
                'status': 'IN_PROGRESS'
            }
        )
        if o2created:
            OrderStatusHistory.objects.create(order=ord2, status='REQUESTED', note='Order requested', changed_by=cust_user)
            OrderStatusHistory.objects.create(order=ord2, status='ACCEPTED', note='Accepted by Riya', changed_by=s1.student)
            OrderStatusHistory.objects.create(order=ord2, status='IN_PROGRESS', note='Drafting concepts', changed_by=s1.student)

    # 9. Follows
    Follow.objects.get_or_create(follower=cust_user, following=student_users['aarav_patel'])
    Follow.objects.get_or_create(follower=cust_user, following=student_users['riya_shah'])
    Follow.objects.get_or_create(follower=student_users['riya_shah'], following=student_users['aarav_patel'])

    # 10. Sample Chat Conversation
    conv, _ = Conversation.get_or_create_conversation(cust_user, student_users['aarav_patel'])
    if conv and conv.messages.count() == 0:
        Message.objects.create(
            conversation=conv,
            sender=cust_user,
            content="Hi Aarav! Loved your portrait posts. Are you free this Saturday for an event photoshoot?",
            is_read=True
        )
        Message.objects.create(
            conversation=conv,
            sender=student_users['aarav_patel'],
            content="Hello Neha! Yes, I am free after 4 PM on Saturday. Where is the location?",
            is_read=True
        )
        Message.objects.create(
            conversation=conv,
            sender=cust_user,
            content="It's near the PDEU amphitheater. I just booked your service package!",
            is_read=True
        )

    # 11. Sample Notifications
    Notification.send(
        recipient=student_users['aarav_patel'],
        sender=cust_user,
        notification_type='REVIEW',
        title='New 5-Star Review Received',
        message='Neha Sharma left a ★★★★★ review for Order #ORD-1024!',
        link='/profile/aarav_patel/'
    )
    Notification.send(
        recipient=cust_user,
        sender=student_users['riya_shah'],
        notification_type='ORDER_STATUS',
        title='Order #ORD-1025 Update',
        message='Riya Shah marked your poster design order as In Progress.',
        link='/orders/'
    )

    print("\n========================================================")
    print("SUCCESS: SkillConnect database successfully populated!")
    print("Demo Accounts:")
    print("  Administrator : username='admin',         password='admin123'")
    print("  Student 1     : username='aarav_patel',   password='student123' (Photography, Verified)")
    print("  Student 2     : username='riya_shah',     password='student123' (Graphic Design, Verified)")
    print("  Student 3     : username='krisha_mehta',  password='student123' (Mehndi, Verified)")
    print("  Student 4     : username='dev_shah',      password='student123' (Web Dev, Verified)")
    print("  Student 5     : username='anaya_patel',   password='student123' (Makeup, Verified)")
    print("  Student 6     : username='rohan_joshi',   password='student123' (Video, Pending)")
    print("  Customer      : username='neha_customer', password='customer123'")
    print("========================================================\n")

if __name__ == '__main__':
    run()
