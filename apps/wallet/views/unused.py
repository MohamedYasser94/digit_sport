from datetime import datetime
from decimal import Decimal

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.shortcuts import redirect
from django.utils.translation import gettext_lazy as _

from apps.medical.models.models import CarGarage
from apps.wallet.forms.wallet import AdminTreasuryTransactionsForm
from apps.wallet.models.models import SystemWallet, Wallet
from apps.wallet.models.transaction import TreasuryTransactions
from apps.wallet.views.transaction import AdminCommonTreasuryTransactionsIncome, AdminCommonTreasuryTransactionsExpense
from helper.decorators import authenticated_staf, staff_only

User = get_user_model()


@authenticated_staf
@staff_only
def AdminTreasuryTransactionsAdd(request, slug):
    print('AdminTreasuryTransactionsAdd', slug)
    system_wallet = SystemWallet.objects.get(secret='SystemWallet')
    wallet = Wallet.objects.get(slug=slug)
    current_user = User.objects.get(id=request.user.id)
    treasury_form = AdminTreasuryTransactionsForm(request.POST or None)
    if request.method == "POST":

        if treasury_form:
            treasury_amount = request.POST.get('treasury_amount')
            transaction_category = request.POST.get('transaction_category')
            transaction_mode = request.POST.get('transaction_mode')
            treasury_note = request.POST.get('treasury_note')
            ############## Bank Transaction  ##############
            month = datetime.now().month
            year = datetime.now().year
            garage = CarGarage.objects.get(id=1)
            last_bank = SystemWallet.objects.get(secret='SystemWallet')
            last_treasury = TreasuryTransactions.objects.filter(system_wallet=system_wallet).last()
            check_treasury = TreasuryTransactions.objects.all().count()
            if transaction_category == 'Income':
                if Decimal(last_bank.amount) < Decimal(treasury_amount) or Decimal(last_bank.amount) <= 0:
                    messages.error(request, _("A bank account does not cover your application , Please Try Again"),
                                   extra_tags='Wallet Transactions')
                    return redirect(request.META['HTTP_REFERER'])
                else:
                    if check_treasury > 0:
                        transaction_type = 'Withdraw'
                        treasury_receive = Decimal(last_treasury.receive) + Decimal(treasury_amount)
                        treasury_send = Decimal(last_treasury.send)
                        treasury_amount = Decimal(last_treasury.amount) + Decimal(treasury_amount)
                        bank_transaction_type = 'Deposit'
                        bank_transaction_category = 'Expense'
                        bank_send = Decimal(last_bank.send) + Decimal(treasury_amount)
                        bank_receive = Decimal(last_bank.receive)
                        bank_amount = Decimal(last_bank.amount) - Decimal(treasury_amount)
                        bank_earning = Decimal(last_bank.earning) - Decimal(treasury_amount)

                    else:
                        transaction_type = 'Withdraw'
                        treasury_receive = Decimal(treasury_amount)
                        treasury_send = Decimal(last_treasury.send)
                        treasury_amount = Decimal(treasury_amount)
                        bank_transaction_type = 'Deposit'
                        bank_transaction_category = 'Expense'
                        bank_send = Decimal(last_bank.send) + Decimal(treasury_amount)
                        bank_receive = Decimal(last_bank.receive)
                        bank_amount = Decimal(last_bank.amount) - Decimal(treasury_amount)
                        bank_earning = Decimal(last_bank.earning) - Decimal(treasury_amount)
                    transaction_amount = treasury_amount
                    AdminCommonTreasuryTransactionsIncome(request, transaction_amount, transaction_type,
                                                          transaction_mode, 'Partial',
                                                          transaction_category, treasury_amount, treasury_receive,
                                                          treasury_send, treasury_note,
                                                          wallet, bank_transaction_type, bank_transaction_category,
                                                          bank_amount, bank_earning, bank_receive,
                                                          bank_send, month, year)
                    messages.success(request, _("Treasury Transactions Successfully Added"),
                                     extra_tags='Wallet Transactions')
                    return redirect(request.META['HTTP_REFERER'])
            elif transaction_category == 'Expense':
                if Decimal(last_treasury.amount) <= 0:
                    messages.error(request, _("A Treasury account does not cover your application , Please Try Again"),
                                   extra_tags='Wallet Transactions')
                    return redirect(request.META['HTTP_REFERER'])
                else:
                    if check_treasury > 0 and Decimal(last_treasury.amount) >= Decimal(treasury_amount):
                        transaction_type = 'Deposit'
                        treasury_receive = Decimal(last_treasury.receive)
                        treasury_send = Decimal(last_treasury.send) + Decimal(treasury_amount)
                        treasury_amount = Decimal(last_treasury.amount) - Decimal(treasury_amount)
                        bank_transaction_type = 'Withdraw'
                        bank_transaction_category = 'Income'
                        bank_send = Decimal(last_bank.send)
                        bank_receive = Decimal(last_bank.receive) + Decimal(treasury_amount)
                        bank_amount = Decimal(last_bank.amount) + Decimal(treasury_amount)
                        bank_earning = Decimal(last_bank.earning) + Decimal(treasury_amount)
                    else:
                        messages.error(request,
                                       _("A Treasury account does not cover your application , Please Try Again"),
                                       extra_tags='Wallet Transactions')
                        return redirect(request.META['HTTP_REFERER'])
                    transaction_amount = treasury_amount
                    AdminCommonTreasuryTransactionsExpense(request, transaction_amount, transaction_type,
                                                           transaction_mode, 'Partial',
                                                           transaction_category, treasury_amount, treasury_receive,
                                                           treasury_send, treasury_note,
                                                           wallet, bank_transaction_type, bank_transaction_category,
                                                           bank_amount, bank_earning, bank_receive,
                                                           bank_send, month, year)
                    messages.success(request, _("Treasury Transactions Successfully Added"),
                                     extra_tags='Wallet Transactions')
                    return redirect(request.META['HTTP_REFERER'])

            else:

                messages.error(request, _("Treasury Transactions Not Add , Please Try Again"),
                               extra_tags='Wallet Transactions')
        else:

            treasury_form = AdminTreasuryTransactionsForm()

            context = {
                'treasury_form': treasury_form,
                'current_page': _('Treasury Transactions'),
                'prev_Page': _('Wallet'),
                'prev_Page_link': redirect(request.META['HTTP_REFERER'])
            }

            return redirect(request.META['HTTP_REFERER'], context)

        context = {
            'treasury_form': treasury_form,
            'current_page': _('Treasury Transactions'),
            'prev_Page': _('Wallet'),
            'prev_Page_link': redirect(request.META['HTTP_REFERER'])
        }

        return redirect(request.META['HTTP_REFERER'], context)




def AdminCommonTreasuryTransactions(request, transaction_type, transaction_mode, transaction_status,
                                    transaction_category, amount, earning, receive, send, note,
                                    wallet, sender_model, sender_id, receiver_model, receiver_id, owner_model, owner_id,
                                    auditor_model, auditor_id):
    try:
        last_transaction = TreasuryTransactions.objects.filter(wallet=wallet).last()
        if transaction_category == 'Income':
            transaction_type = 'Withdraw'
            receive = last_transaction.receive + Decimal(amount)
            earning = last_transaction.earning + Decimal(amount)
        elif transaction_category == 'Expense':
            transaction_type = 'Deposit'
            send = last_transaction.receive - Decimal(amount)
            earning = last_transaction.earning - Decimal(amount)
    except Exception as e:
        print('error from last transaction ', e)
        last_transaction = 0
        if transaction_category == 'Income':
            transaction_type = 'Withdraw'
            receive = amount
            earning = Decimal(amount)
        elif transaction_category == 'Expense':
            transaction_type = 'Deposit'
            send = amount
            earning = Decimal(amount)
    print('last_transaction', last_transaction)
    treasury_object = TreasuryTransactions.objects.create(wallet=wallet,
                                                          sender_model=ContentType.objects.get(model=sender_model),
                                                          sender_id=sender_id,
                                                          receiver_model=ContentType.objects.get(model=receiver_model),
                                                          receiver_id=receiver_id,
                                                          owner_model=ContentType.objects.get(model=owner_model),
                                                          owner_id=owner_id,
                                                          auditor_model=ContentType.objects.get(model=auditor_model),
                                                          auditor_id=auditor_id, transaction_type=transaction_type,
                                                          transaction_mode=transaction_mode,
                                                          transaction_status='Pending',
                                                          transaction_category=transaction_category, amount=amount,
                                                          earning=earning, receive=receive, send=send, note=note, )
    AdminMoneyTransaction(request, 'TreasuryTransactions', treasury_object.id, 'Wallet', wallet.id, transaction_type,
                      amount)
    return treasury_object




@authenticated_staf
@staff_only
def AdminExpensesTransactionsAdd(request):
    system_wallet = SystemWallet.objects.get(secret='SystemWallet')
    wallet = Wallet.objects.get(user_id=request.user.id)
    current_user = User.objects.get(id=request.user.id)
    expenses_form = AdminExpensesTransactionsForm(request.POST or None)

    if request.method == "POST":

        if expenses_form:

            expenses_amount = request.POST.get('expenses_amount')
            transaction_mode = request.POST.get('transaction_mode')
            hero_image = request.FILES.get('hero_image')
            expenses_note = request.POST.get('expenses_note')
            ############## Bank Transaction  ##############
            transaction_type = None
            receive = None
            send = None
            earning = None
            transaction_category = 'Expense'

            garage = CarGarage.objects.get(id=1)
            try:
                last_treasury = TreasuryTransactions.objects.filter(system_wallet=system_wallet).last()
                last_expenses = ExpensesTransactions.objects.filter(system_wallet=system_wallet).last()
                if last_treasury.earning < Decimal(expenses_amount) or last_treasury.earning <= 0:
                    messages.error(request, _("A Treasury account does not cover your application , Please Try Again"),
                                   extra_tags='Expenses Transactions')
                    return redirect(request.META['HTTP_REFERER'])
                if transaction_category == 'Income':
                    transaction_type = 'Withdraw'
                    receive = expenses_amount
                    earning = last_expenses.earning + Decimal(expenses_amount)
                elif transaction_category == 'Expense':
                    transaction_type = 'Deposit'
                    send = expenses_amount
                    earning = last_expenses.earning - Decimal(expenses_amount)
            except Exception as e:
                print('error from last transaction ', e)
                messages.error(request, _(f"There are no funds in the company's Treasury account or , {e}"),
                               extra_tags='Expenses Transactions')
                return redirect(request.META['HTTP_REFERER'])

            if expenses_form:
                print(2)

                expenses_form = ExpensesTransactions(wallet=wallet, system_wallet=system_wallet,
                                                     sender_model=ContentType.objects.get(model='User'),
                                                     sender_id=current_user.id,
                                                     receiver_model=ContentType.objects.get(
                                                         model='TreasuryTransactions'),
                                                     receiver_id=last_treasury.id,
                                                     owner_model=ContentType.objects.get(model='Wallet'),
                                                     owner_id=wallet.id,
                                                     auditor_model=ContentType.objects.get(model='User'),
                                                     auditor_id=current_user.id, transaction_type=transaction_type,
                                                     transaction_mode=transaction_mode, transaction_status='Pending',
                                                     transaction_category=transaction_category, amount=expenses_amount,
                                                     earning=earning, receive=receive, send=send, note=expenses_note, )

                expenses_form.save()
                AdminCommonMediaHeroFiles(request, hero_image, 'ExpensesTransactions', expenses_form.id)
                AdminMoneyTransaction(request, 'ExpensesTransactions', expenses_form.id, 'TreasuryTransactions',
                                  last_treasury.id, transaction_type,
                                  expenses_amount)
                AdminCommonTreasuryTransactions(request, transaction_type, transaction_mode, 'Pending',
                                                'Expense', expenses_amount, earning, receive, send, expenses_note,
                                                wallet, 'User', current_user.id, 'ExpensesTransactions',
                                                expenses_form.id, 'Wallet',
                                                wallet.id, 'User', current_user.id)

                messages.success(request, _("Expenses Transactions Add Successfully"),
                                 extra_tags='Expenses Transactions')

                return redirect(request.META['HTTP_REFERER'])

        else:
          

            messages.error(request, _("Expenses Transactions Not Add , Please Try Again"),
                           extra_tags='Expenses Transactions')
    else:

        expenses_form = AdminExpensesTransactionsForm()

        context = {
            'expenses_form': expenses_form,
            'current_page': _('Treasury Transactions'),
            'prev_Page': _('Treasury'),
            'prev_Page_link': reverse_lazy('core:AdminExpensesTransactionsList'),
        }

        return render(request, f'{BACKEND_TEMPLATES}/utilities/expenses/add.html', context)

    context = {
        'expenses_form': expenses_form,
        'current_page': _('Treasury Transactions'),
        'prev_Page': _('Treasury'),
        'prev_Page_link': reverse_lazy('core:AdminExpensesTransactionsList'),
    }

    return render(request, f'{BACKEND_TEMPLATES}/utilities/expenses/add.html', context)


def AdminCommonWalletMoneyTransactionsAdd(request, bank, percentage, stores, send, receive, earnings, actual, expenses,
                                          wallet, userowner_model, owner_id):
    try:
        system_wallet = SystemWallet.objects.get(secret='SystemWallet')
        wallet_money_object = WalletMoney.objects.get(wallet=wallet, )
        wallet_money_object.bank = bank
        wallet_money_object.percentage = percentage
        wallet_money_object.stores = stores
        wallet_money_object.send = send
        wallet_money_object.receive = receive
        wallet_money_object.earnings = earnings
        wallet_money_object.actual = actual
        wallet_money_object.expenses = expenses
        wallet_money_object.save()
    except Exception as e:
        month = datetime.now().month
        year = datetime.now().year

        wallet_money_object = WalletMoney.objects.create(wallet=wallet,
                                                         bank=bank,
                                                         percentage=percentage,
                                                         stores=stores,
                                                         send=send,
                                                         receive=receive,
                                                         earnings=earnings,
                                                         actual=actual,
                                                         expenses=expenses,
                                                         owner_model=ContentType.objects.get(
                                                             model=userowner_model),
                                                         owner_id=owner_id,
                                                         )
        AdminMoneyTransaction(request, 'WalletMoney', wallet_money_object.id, 'Wallet', wallet.id,
                          'WalletMoney',
                          actual, month, year)

