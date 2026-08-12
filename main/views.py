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

def dental_filling(request):
    # Mock data for Treatment Charges
    class MockPrice:
        def __init__(self, name, notes, price):
            self.name = name
            self.notes = notes
            self.price = price

    class MockTreatment:
        class Prices:
            @staticmethod
            def all():
                return [
                    MockPrice("Composite Filling (Small)", "One surface, tooth-colored restoration", "1,500"),
                    MockPrice("Composite Filling (Large)", "Multi-surface, complex tooth-colored restoration", "2,500"),
                    MockPrice("Glass Ionomer Filling", "Fluoride-releasing restoration", "1,200")
                ]
        prices = Prices()

    treatment = MockTreatment()

    # Mock data for Testimonials
    testimonials = [
        {
            'name': 'Anil Sharma',
            'treatment': 'Dental Filling',
            'text': 'I was worried my front tooth filling would look noticeable, but the tooth-colored restoration blends perfectly with my natural smile. Highly recommend CareFirst!'
        },
        {
            'name': 'Priya Gurung',
            'treatment': 'Dental Filling',
            'text': 'The procedure was completely painless. Dr. Subash explained everything clearly, and the result is fantastic.'
        }
    ]

    # Mock data for Related Services
    related_services = [
        {
            'name': 'General Dentistry',
            'desc': 'Comprehensive checkups and preventive care for a healthy smile.',
            'url': '/treatments/general-dentistry/',
            'image': 'scalling_hero.jpg'
        },
        {
            'name': 'Root Canal Treatment',
            'desc': 'Save your natural tooth with painless endodontic therapy.',
            'url': '/treatments/root-canal/',
            'image': 'rct_hero.avif'
        },
        {
            'name': 'Scaling & Polishing',
            'desc': 'Professional cleaning to remove plaque and brighten teeth.',
            'url': '/treatments/scaling/',
            'image': 'scaling_before.png'
        }
    ]

    context = {
        'treatment': treatment,
        'testimonials': testimonials,
        'related_services': related_services
    }
    return render(request, 'treatments/dental_filling.html', context)

def crowns_bridges(request):
    dynamic_prices = {
        'metal_crown': '3,000',
        'pfm_crown': '6,000',
        'zirconia_crown': '12,000',
        'emax_crown': '18,000'
    }
    context = {
        'dynamic_prices': dynamic_prices
    }
    return render(request, 'treatments/crowns_bridges.html', context)

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
