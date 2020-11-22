import logging
from itertools import chain

import requests
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.db.models import Sum, Q, F, Func, FloatField, ExpressionWrapper, CharField, Value
from django.views import generic
from django.db.models.functions import ExtractMonth, ExtractYear, Concat, ExtractDay
from myapp import stock_api
from myapp.models import Stock, UserProfile, Transaction
from myapp.forms import UserProfileForm, UserForm
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import logout, login, authenticate
from django.contrib import messages
from django.contrib.auth import logout
from . import stock_api, models
from datetime import datetime
from myapp.logic import trade_logic, register_logic
from django.views.decorators.csrf import csrf_exempt
from myapp.exceptions import custom_exception, trade_excpetions


# View for the home page - a list of 20 of the most active stocks
def index(request):
    # Query the stock table, filter for top ranked stocks and order by their rank.
    data = Stock.objects.filter(top_rank__isnull=False).order_by('top_rank')
    return render(request, 'index.html', {'page_title': 'Main', 'data': data})


# View for the single stock page
# symbol is the requested stock's symbol ('AAPL' for Apple)
def single_stock(request, symbol):
    data = stock_api.get_stock_info(symbol)
    return render(request, 'single_stock.html', {'page_title': 'Stock Page - %s' % symbol, 'data': data})


def register(request):
    # If post -> register the user and redirect to main page
    if request.method == 'POST':
        firstname = request.POST.get('firstname')
        lastname = request.POST.get('lastname')
        email = request.POST.get('email')
        password = request.POST.get('password')

        newuser = User.objects.create_user(username=email, email=email, password=password)
        newuser.first_name = firstname
        newuser.last_name = lastname
        newuser.save()

        register_logic.create_profile(newuser)

        logger = logging.getLogger('custom_log')
        logger.debug(f'{newuser.first_name}  {newuser.last_name} rigestered .')
        # to let the user login after registeration
        user = authenticate(username=email, password=password)
        if user is not None:
            login(request, user)

        return redirect('index')
    else:
        # If not post (regular request) -> render register page
        return render(request, 'register.html', {'page_title': 'Register'})


def logout_view(request):
    logout(request)
    return redirect('index')


def my_account(request):
    user = User.objects.get(pk=request.user.id)
    user_profile = UserProfile.objects.get(user__pk=request.user.id)
    stock_transactions = Transaction.objects.filter(user=request.user)
    frm_user_profile = UserProfileForm(instance=user_profile)
    frm_user = UserForm(instance=user)
    context = {'frm_user': frm_user, 'frm_user_profile': frm_user_profile, 'stock_transactions': stock_transactions}
    return render(request, 'my_account.html', context=context)


def update_my_account(request):
    # user_profile = UserProfile.objects.get(user__pk=request.user.id)
    # frm_user_profile = UserProfileForm(request.POST, instance=user_profile)
    if request.method == 'POST':
        frm_user = UserForm(request.POST, instance=request.user)
        if frm_user.is_valid():
            frm_user.save()
            messages.success(request, 'Profile details updated successfully.')
        else:
            messages.error(request, f'error: {frm_user.errors.as_data()}')
    return redirect('/accounts/myaccount')


# API for a stock's price over time
# symbol is the requested stock's symbol ('AAPL' for Apple)
# The response is JSON data of an array composed of "snapshot" objects (date + stock info + ...), usually one per day
def single_stock_historic(request, symbol):
    data = stock_api.get_stock_historic_prices(symbol, time_range='1m')
    return JsonResponse({'data': data})


def compare(request):
    stock_list = stock_api.get_all_stocks()
    data = {'stock_list': stock_list,
            }
    return render(request, 'compare_two_stocks.html', data)


@login_required
@csrf_exempt
def trade(request):
    stock_list = stock_api.get_all_stocks()
    context = {'stock_list': stock_list}
    try:
        if request.method == 'POST':
            params = request.POST
            stock_symbol = params["stock_selector"]
            number_of_stocks = int(params["number_of_stocks"])
            if number_of_stocks <= 0:
                raise trade_excpetions.InvalidNumberOfStocksExceptions("Invalid number")

            stock_price = trade_logic.get_stock_price(stock_symbol)

            user_profile = models.UserProfile.objects.get(user=request.user)
            total_price = stock_price * number_of_stocks

            if 'sell' in params:
                available_stocks = trade_logic.get_number_of_stocks(request.user, stock_symbol)
                if available_stocks < number_of_stocks:
                    raise trade_excpetions.NotEnoughStocksException("Not enough stocks to sell")

                number_of_stocks *= -1
                trade_logic.create_transaction(request.user, stock_symbol, number_of_stocks, stock_price)

                user_profile.balance += total_price
                user_profile.save()

            elif 'buy' in params:
                if total_price > user_profile.balance:
                    raise trade_excpetions.NotEnoughMoneyException("Not enough money")

                trade_logic.create_transaction(request.user, stock_symbol, number_of_stocks, stock_price)

                user_profile.balance -= total_price
                user_profile.save()

            return render(request, 'trade.html', context)

    except custom_exception.CustomException as e:
        context.update({'error': str(e)})

    return render(request, 'trade.html', context)


class TopBuySellListView(generic.ListView):
    model = Transaction
    context_object_name = 'top_buy_sell_list'  # your own name for the list as a template variable

    template_name = 'index.html'

    def get_queryset(self, **kwargs):
        params = self.request.GET

        ts_filtered = Transaction.objects.filter(trans_date_time__lte=params['to_date'],
                                                 trans_date_time__gte=params['from_date'])

        if self.request.user.is_authenticated and params.get('current_user_only', '0') == '1':
            ts_filtered = ts_filtered.filter(user=self.request.user)

        if params.get('CB_Stock', '0') == '1':
            stock_symbol = 'stock_symbol'
        else:
            stock_symbol = "user"

        if params['RBPeriod'] == 'Annually':
            ts_values = ts_filtered.values(stock_symbol, year=ExtractYear('trans_date_time'))
            ts_annonate = ts_values.annotate(f_date=F('year'))


        elif params['RBPeriod'] == 'Monthly':
            ts_values = ts_filtered.values(stock_symbol, month=ExtractMonth('trans_date_time'),
                                           year=ExtractYear('trans_date_time'), )
            ts_annonate = ts_values.annotate(f_date=ExpressionWrapper(
                Concat(F('month'), Value(' / '), F('year')), output_field=CharField()))

        elif params['RBPeriod'] == 'Daily':
            ts_values = ts_filtered.values(stock_symbol, day=ExtractDay('trans_date_time'),
                                           month=ExtractMonth('trans_date_time'),
                                           year=ExtractYear('trans_date_time'))
            ts_annonate = ts_values.annotate(f_date=ExpressionWrapper(
                Concat(F('day'), Value(' / '), F('month'), Value(' / '), F('year')), output_field=CharField()))

        return ts_annonate.annotate(
            full_name=Concat(F('user__first_name'), Value(' '), F('user__last_name')),

            sell=Sum(F('quantity') * F('price'), filter=Q(quantity__gt=0),
                     output_field=FloatField()),
            buy=Sum(F('quantity') * F('price'), filter=Q(quantity__lt=0),
                    output_field=FloatField())

        ).order_by('f_date')
