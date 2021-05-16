from django.shortcuts import render

# Create your views here.
def upload(request):
    print('success!')
    return render(request, "dataProcess/upload.html")