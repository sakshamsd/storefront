from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
# request -> response
# request handler

def say_hello(request):
    x = 1
    y = 2
    return HttpResponse('Hello World')

def say_hello_template(request):
    return render(request, 'hello.html',{'name':'Saksham'})
