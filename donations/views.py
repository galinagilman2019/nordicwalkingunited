from django.shortcuts import render

def donate(request):
    return render(request, "donations/donate.html")
