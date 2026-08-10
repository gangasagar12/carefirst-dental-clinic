from django.shortcuts import render

def index(request):
    return render(request, 'index.html')

def about(request):
    return render(request, 'pages/about.html')

def treatments(request):
    return render(request, 'pages/treatments.html')

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
