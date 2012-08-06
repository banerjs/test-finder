from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

# Create your views here.

@login_required
def displayHome(request):
    customer = request.user.CustomerCore
    return render(request, 'customer/home.html', { 'customer':customer })

# @login_required                                               # Ensure logged in
# def displayDash(request):                                     # Display dash
#     customer = request.user.CustomerCore
#     return render(request, 'dashboard/customer.html',
#                   {'customer':customer})

@login_required
def changeAddress(request):
    # If there was no form
    ##### Load a form
    ##### Display the form
    
    # If the form is valid - Save the information in the model.
    ##### Redirect to login dashboard (display message with success)
    
    # Else
    ##### return the form with error messages
    return redirect('customer_dashboard')

@login_required
def changeInfo(request):
    """
    This view allows the customer to change profile information. Complementary
    to this view is the view that allows the customer to change his/her password
    """
    #If there was no form
    ##### Load the form
    ##### Display the form

    # If the form is valid - Save and update the information in the model
    ##### Redirect to  to the login dashboard and display a success message

    # Else
    ##### Return with error messages
    return redirect('customer_dashboard')

# Here is the view that changes the password. This should be tied into the auth system
# if possible

# Here are the views that deal with galleries and pictures.
