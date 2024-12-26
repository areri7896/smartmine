from django.shortcuts import render

# Create your views here.

def index(request):
    return render(request, 'src/landing/index.html', {})

# def login(request):
#     return render(request, 'src/landing/login.html', {})

# def company(request):
#     return render(request, 'src/landing/company.html', {})

# def blog(request):
#     return render(request, 'src/landing/blog.html', {})