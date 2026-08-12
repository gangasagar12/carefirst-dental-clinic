from django.shortcuts import render

def index(request):
    return render(request, 'index.html')

def about(request):
    return render(request, 'pages/about.html')

def treatments(request):
    return render(request, 'pages/treatments.html')

def general_dentistry(request):
    context = {
        'treatment': {
            'prices': {
                'all': [
                    {'name': 'Dental Checkup', 'price': '1,500', 'notes': 'Comprehensive exam & consultation'},
                    {'name': 'Scaling & Polishing', 'price': '3,500', 'notes': 'Full mouth professional cleaning'},
                    {'name': 'Dental Filling', 'price': '2,500', 'notes': 'Tooth-colored composite restoration'},
                    {'name': 'Digital Dental X-Ray', 'price': '800', 'notes': 'Periapical high-res radiograph'},
                ]
            }
        },
        'testimonials': [
            {'name': 'Ananya S.', 'text': 'The most gentle dental checkup I have ever had. Highly recommend!', 'rating': '5.0', 'treatment': 'General Checkup'},
            {'name': 'Bikash M.', 'text': 'Very professional clinic. The scaling was completely painless.', 'rating': '4.9', 'treatment': 'Scaling & Polishing'},
            {'name': 'Priya K.', 'text': 'My cavity was fixed in 20 minutes without any discomfort. Thank you CareFirst!', 'rating': '5.0', 'treatment': 'Dental Filling'}
        ],
        'related_services': [
            {'name': 'Root Canal Treatment', 'desc': 'Save your natural tooth with painless endodontic care.', 'image': 'rct_feat_painfree.png', 'url': '#'},
            {'name': 'Teeth Whitening', 'desc': 'Brighten your smile safely and effectively.', 'image': 'scalling_hero.jpg', 'url': '#'},
            {'name': 'Scaling & Polishing', 'desc': 'Remove stubborn plaque and stains for healthy gums.', 'image': 'dental_x-ray.jpg', 'url': '#'}
        ]
    }
    return render(request, 'treatments/general_dentistry.html', context)

def doctors(request):
    return render(request, 'pages/doctors.html')

def gallery(request):
    return render(request, 'pages/gallery.html')

def reviews(request):
    return render(request, 'pages/reviews.html')

def blog(request):
    return render(request, 'pages/blog.html')

def contact(request):
    return render(request, 'pages/contact.html')

def appointment(request):
    return render(request, 'pages/appointment.html')

def media(request):
    return render(request, 'pages/media.html')

def pricing(request):
    return render(request, 'pages/pricing.html')
