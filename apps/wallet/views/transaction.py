from datetime import datetime
from decimal import Decimal

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _


from apps.wallet.forms.wallet import AdminBankTransactionsForm, AdminTreasuryTransactionsForm, \
    AdminExpensesTransactionsForm
from apps.wallet.models.models import WalletMoney, SystemWallet, Wallet
from apps.wallet.models.transaction import BankTransactions, TreasuryTransactions, ExpensesTransactions
from apps.wallet.views.common_transaction import AdminMoneyTransaction, AdminCommonTreasuryTransactions

from core.views.core import AdminCommonMediaHeroFiles
from core.views.notifications import AdminCommonNotifications

from helper.commonHelper import BACKEND_TEMPLATES
from helper.decorators import authenticated_staf, staff_only

User = get_user_model()


@authenticated_staf
@staff_only
def AdminBankTransactionAdd(request, slug):
    print('AdminBankTransactionAdd', slug)
    system_wallet = SystemWallet.objects.get(secret='SystemWallet')
    wallet = Wallet.objects.get(slug=slug)
    current_user = User.objects.get(id=request.user.id)
    bank_form = AdminBankTransactionsForm(request.POST or None)

    if request.method == "POST":
        if bank_form:
            transaction_amount = request.POST.get('bank_amount')
            transaction_category = request.POST.get('transaction_category')
            transaction_mode = request.POST.get('transaction_mode')
            bank_note = request.POST.get('bank_note')
            ############## Bank Transaction  ##############
            account_check = AdminOperationTransactionAccountsCheck(request)
            if account_check == False:
                messages.error(request, _('Please Add Operation Account First To Make System Work Good'),
                               extra_tags='Wallet Transactions')
                return redirect(request.META['HTTP_REFERER'])
            wallet_check = SystemWallet.objects.get(secret='SystemWallet')
            if wallet_check.earning == 0 and transaction_category == 'Expense':
                messages.error(request, _('You can not expense money from system wallet'),
                               extra_tags='Wallet Transactions')
                return redirect(request.META['HTTP_REFERER'])
            if transaction_category == 'Expense' and Decimal(wallet_check.earning) < Decimal(
                    transaction_amount):
                messages.error(request, _('Your Expense Amount Greate Than Bank Amount'),
                               extra_tags='Wallet Transactions')
                return redirect(request.META['HTTP_REFERER'])

            if bank_form:
                print(2)
                try:
                    last_transaction = SystemWallet.objects.get(secret='SystemWallet')
                    if transaction_category == 'Income':
                        transaction_type = 'Withdraw'

                        bank_amount = Decimal(last_transaction.amount) + Decimal(transaction_amount)
                        bank_earning =  Decimal(last_transaction.earning) + Decimal(transaction_amount)
                        bank_receive =  Decimal(last_transaction.receive) + Decimal(transaction_amount)
                        bank_send = Decimal(last_transaction.send)
                        AdminCommonBankTransactionsIncome(request, wallet.slug, transaction_type, transaction_mode,
                                                          transaction_category, bank_amount, bank_earning, bank_receive, bank_send,
                                                          bank_note,transaction_amount)
                    elif transaction_category == 'Expense':
                        transaction_type = 'Deposit'
                        bank_amount = Decimal(last_transaction.earning) - Decimal(transaction_amount)
                        bank_earning = Decimal(last_transaction.earning) - Decimal(transaction_amount)
                        bank_send =  Decimal(last_transaction.send) + Decimal(transaction_amount)
                        bank_receive = Decimal(last_transaction.receive)

                        AdminCommonBankTransactionsExpense(request, wallet.slug, transaction_type, transaction_mode,
                                                          transaction_category, bank_amount, bank_earning, bank_receive, bank_send,
                                                          bank_note,transaction_amount)
                except Exception as e:
                    print('error from last transaction ', e)
                    last_transaction = 0
                    if transaction_category == 'Income':
                        transaction_type = 'Withdraw'
                        bank_amount =  Decimal(transaction_amount)
                        bank_earning =  Decimal(transaction_amount)
                        bank_receive = Decimal(transaction_amount)
                        bank_send = 0
                        AdminCommonBankTransactionsIncome(request, wallet.slug, transaction_type, transaction_mode,
                                                          transaction_category, bank_amount, bank_earning, bank_receive, bank_send,
                                                          bank_note,transaction_amount)
                    elif transaction_category == 'Expense':
                        transaction_type = 'Deposit'
                        bank_amount = Decimal(transaction_amount)
                        bank_earning = Decimal(transaction_amount)
                        bank_send = transaction_amount
                        bank_receive = 0

                        AdminCommonBankTransactionsExpense(request, wallet.slug, transaction_type, transaction_mode,
                                                          transaction_category, bank_amount, bank_earning, bank_receive, bank_send,
                                                          bank_note,transaction_amount)
                print('last_transaction', last_transaction)

                messages.success(request, _("Bank Transactions Add Successfully"), extra_tags='Wallet Transactions')

                return redirect(request.META['HTTP_REFERER'])

        else:
          

            messages.error(request, _("Bank Transactions Not Add , Please Try Again"), extra_tags='Wallet Transactions')
    else:

        bank_form = AdminBankTransactionsForm()

        context = {
            'bank_form': bank_form,
            'current_page': _('Bank Transactions'),
            'prev_Page': _('Wallet'),
            'prev_Page_link': redirect(request.META['HTTP_REFERER'])
        }

        return redirect(request.META['HTTP_REFERER'], context)

    context = {
        'bank_form': bank_form,
        'current_page': _('Bank Transactions'),
        'prev_Page': _('Wallet'),
        'prev_Page_link': redirect(request.META['HTTP_REFERER'])
    }

    return redirect(request.META['HTTP_REFERER'], context)


def AdminCommonBankTransactionsIncome(request, wallet_slug, transaction_type, transaction_mode,
                                                          transaction_category, bank_amount, bank_earning, bank_receive, bank_send,
                                                          bank_note,transaction_amount):
    system_wallet = SystemWallet.objects.get(secret='SystemWallet')
    wallet = Wallet.objects.get(slug=wallet_slug)
    current_user = User.objects.get(id=request.user.id)
    auditor = OperationTransactionAccounts.objects.all().last()

    bank_form = BankTransactions(system_wallet=system_wallet,
                                 sender_model=ContentType.objects.get(model='User'),
                                 sender_id=current_user.id,
                                 receiver_model=ContentType.objects.get(model='SystemWallet'),
                                 receiver_id=system_wallet.id,
                                 owner_model=ContentType.objects.get(model='Wallet'),
                                 owner_id=wallet.id,
                                 auditor_model=ContentType.objects.get(model='User'),
                                 auditor_id=auditor.auditor.id, transaction_type=transaction_type,
                                 transaction_mode=transaction_mode, transaction_status='Partial',
                                 transaction_category=transaction_category, amount=transaction_amount,
                                  receive=transaction_amount, send=0, note=bank_note, )

    bank_form.save()
    month = datetime.now().month
    year = datetime.now().year
    AdminMoneyTransaction(request, 'BankTransactions', bank_form.id, 'SystemWallet', system_wallet.id, transaction_type,
                      transaction_amount, month, year)
    AdminCommonSystemWalletTransactionsAdd(request, bank_earning, bank_amount, 0, 0, bank_receive, bank_send, bank_note, )
    AdminCommonPercentageTransactionsAdd(request, transaction_type, transaction_mode, 'Partial',
                                         transaction_category, bank_amount, 0,
                                         f'_(Percentage Transactions With Bank Transactions , By Note)  {bank_note} ',
                                         wallet, 'BankTransactions', bank_form.id, 'User', None,
                                         'Wallet', None,'User', auditor.auditor.id)

    AdminCommonActionNeedApproved(request, 'User', request.user.id, 'BankTransactions',
                                  bank_form.id, 'Partial')
    users = User.objects.filter(have_wallet=True)

    for user in users:
        wallet = Wallet.objects.get(user_nuc=user.nuc)
        AdminCommonNotifications(request, _(f'Money Transactions in Bank '), False, False, False,
                                 _(f'New {bank_amount} {transaction_category} Money Transactions in Bank '),
                                 'BankTransactions', bank_form.slug,
                                 _(f'New {transaction_category} Money Transactions in Bank With Amount {bank_amount}'),
                                 _(f'New {transaction_category} Money Transactions in Bank With Amount {bank_amount} By {current_user.get_full_name()} By Note {bank_note}'),
                                 bank_form.create_at, None, 'User', request.user.id,
                                 'User', user.id, 'Wallet', wallet.id,
                                 'User', auditor.auditor.id)


def AdminCommonBankTransactionsExpense(request, wallet_slug, transaction_type, transaction_mode,
                                                          transaction_category, bank_amount, bank_earning, bank_receive, bank_send,
                                                          bank_note,transaction_amount):
    system_wallet = SystemWallet.objects.get(secret='SystemWallet')
    wallet = Wallet.objects.get(slug=wallet_slug)
    current_user = User.objects.get(id=request.user.id)

    bank_form = BankTransactions(wallet=wallet, system_wallet=system_wallet,
                                 sender_model=ContentType.objects.get(model='User'),
                                 sender_id=current_user.id,
                                 receiver_model=ContentType.objects.get(model='SystemWallet'),
                                 receiver_id=system_wallet.id,
                                 owner_model=ContentType.objects.get(model='Wallet'),
                                 owner_id=wallet.id,
                                 auditor_model=ContentType.objects.get(model='User'),
                                 auditor_id=current_user.id, transaction_type=transaction_type,
                                 transaction_mode=transaction_mode, transaction_status='Pending',
                                 transaction_category=transaction_category, amount=transaction_amount,
                                  receive=0, send=transaction_amount, note=bank_note, )

    bank_form.save()

    AdminCommonActionNeedApproved(request, 'User', request.user.id, 'BankTransactions',
                                  bank_form.id, 'All')
    users = User.objects.filter(have_wallet=True)
    auditor = OperationTransactionAccounts.objects.all().last()
    for user in users:
        wallet = Wallet.objects.get(user_nuc=user.nuc)
        AdminCommonNotifications(request, _(f'Money  Transactions Request '), False, False, False,
                                 _(f'New {transaction_category} Money Transactions in Bank Request '),
                                 'BankTransactions', bank_form.slug,
                                 _(f'New {transaction_category} Money Transactions in Bank With Amount {bank_amount}'),
                                 _(f'New {transaction_category} Money Transactions in Bank With Amount {bank_amount} By {current_user.get_full_name()} By Note {bank_note}'
                                   f' And Need Approved By All Partners , Please Check It in Your Wallet To Approved It The Transaction Request Under Code {bank_form.code}'),
                                 bank_form.create_at, None, 'User', request.user.id,
                                 'User', user.id, 'Wallet', wallet.id,
                                 'User', auditor.auditor.id)


def AdminCommonBankTransactionsExpenseApprove(request):
    print('bank_transaction', request.POST.get('transaction_slug'))

    bank_transaction = BankTransactions.objects.get(slug=request.POST.get('transaction_slug'))

    system_wallet = SystemWallet.objects.get(secret='SystemWallet')
    current_user = User.objects.get(id=request.user.id)
    request_sender = User.objects.get(id=bank_transaction.sender_id)
    garage = CarGarage.objects.get(id=1)
    request_sender_wallet = Wallet.objects.get(user_id=request_sender.id)
    current_user_wallet = Wallet.objects.get(user_id=current_user.id)
    if request.method == 'POST':
        approved_form = AdminWalletActionNeedApprovedForm()
        if approved_form:
            print('approved_form')
            transaction_slug = request.POST.get('transaction_slug')
            approved_status = request.POST.get('approved_status')
            print('approved_status', approved_status)
            common_actions = ActionNeedApproved.objects.get(sender_model=ContentType.objects.get(model='User'),
                                                            sender_id=request_sender.id,
                                                            receiver_model=ContentType.objects.get(model='User'),
                                                            receiver_id=current_user.id,
                                                            approved_model=ContentType.objects.get(
                                                                model='BankTransactions'),
                                                            approved_id=bank_transaction.id, )
            common_actions.approved_status = approved_status
            common_actions.save()
            get_approved_account = ActionNeedApproved.objects.filter(
                approved_model=ContentType.objects.get(model='BankTransactions'),
                approved_id=bank_transaction.id, ).count()

            check_approved = ActionNeedApproved.objects.filter(
                approved_model=ContentType.objects.get(model='BankTransactions'),
                approved_id=bank_transaction.id, approved_status='Approved').count()
            check_not_approved = ActionNeedApproved.objects.filter(
                approved_model=ContentType.objects.get(model='BankTransactions'),
                approved_id=bank_transaction.id, approved_status='Not Approved').count()
            check_partial_approved = ActionNeedApproved.objects.filter(
                approved_model=ContentType.objects.get(model='BankTransactions'),
                approved_id=bank_transaction.id, approved_status='Partial Approval').count()
            check_pending = ActionNeedApproved.objects.filter(
                approved_model=ContentType.objects.get(model='BankTransactions'),
                approved_id=bank_transaction.id, approved_status='Pending').count()
            print('get_approved_account', get_approved_account)
            print('check_approved', check_approved)
            print('check_not_approved', check_not_approved)
            print('check_partial_approved', check_partial_approved)
            print('check_pending', check_pending)
            if check_pending > 0:
                print('if check_pending')
                users = User.objects.filter(have_wallet=True)
                auditor = OperationTransactionAccounts.objects.all().last()
                for user in users:
                    wallet = Wallet.objects.get(user_nuc=user.nuc)
                    AdminCommonNotifications(request, _(f'A Partial Approve From Request  '), False, False, False,
                                             _(f'A Partial Approve For  Request With  {bank_transaction.amount} {bank_transaction.transaction_category} Money Transactions in Bank '),
                                             'BankTransactions', bank_transaction.slug,
                                             _(f'A Partial Approve For  Request With  {bank_transaction.amount} {bank_transaction.transaction_category} Money Transactions in Bank'),
                                             _(f'A Partial Approve For  Request With  {bank_transaction.amount} {bank_transaction.transaction_category} Money Transactions in Bank '
                                               f'By {current_user.get_full_name()} And Need Approved By All Partners , Please Check It in '
                                               f'Your Wallet  The Transaction Request Under Code {bank_transaction.code} , You Get notification When All Approved It'),
                                             bank_transaction.create_at, None, 'User', request.user.id,
                                             'User', user.id, 'Wallet', wallet.id,
                                             'User', auditor.auditor.id)
            elif check_approved == get_approved_account:
                if system_wallet.amount < bank_transaction.amount:
                    messages.error(request,
                                   _(f'You Cannot Approved This Transaction Because The System Wallet Earning Is Less Than The Transaction Amount'))
                    return redirect(request.META['HTTP_REFERER'])

                print('elif check_approved')
                month = datetime.now().month
                year = datetime.now().year
                AdminMoneyTransaction(request, 'BankTransactions', bank_transaction.id, 'SystemWallet', system_wallet.id,
                                  bank_transaction.transaction_type,
                                  bank_transaction.amount, month, year)
                if bank_transaction.transaction_category == 'Expense':
                    if system_wallet.amount < bank_transaction.amount:
                        bank_transaction.transaction_mode= 'Failed'
                        bank_transaction.save()
                        messages.error(request,
                                       _(f'You Cannot Approved This Transaction Because The System Wallet Earning Is Less Than The Transaction Amount'))
                        return redirect(request.META['HTTP_REFERER'])
                    else:
                        system_wallet.amount = Decimal(system_wallet.amount) - Decimal(bank_transaction.amount)
                        system_wallet.earning = Decimal(system_wallet.earning) -Decimal(bank_transaction.amount)
                        system_wallet.send = system_wallet.send + Decimal(bank_transaction.amount)
                        system_wallet.save()
                        bank_transaction.transaction_mode = 'Complete'
                        bank_transaction.save()

                AdminCommonPercentageTransactionsAdd(request, bank_transaction.transaction_type,
                                                     bank_transaction.transaction_mode, 'Complete',
                                                     bank_transaction.transaction_category, bank_transaction.receive,
                                                     bank_transaction.send,
                                                     f'_(Money Transactions With Bank Transactions , By Note)  {bank_transaction.note}',
                                                     current_user_wallet, 'BankTransactions', bank_transaction.id,
                                                     'User', None,
                                                     'Wallet', current_user_wallet.id,
                                                     'User', current_user.id)
                bank_transaction.transaction_status = 'Complete'
                bank_transaction.save()
                users = User.objects.filter(have_wallet=True)
                auditor = OperationTransactionAccounts.objects.all().last()
                for user in users:
                    wallet = Wallet.objects.get(user_nuc=user.nuc)
                    AdminCommonNotifications(request, _(f'Complete Money  Transactions Request '), False, False, False,
                                             _(f'Complete {bank_transaction.transaction_category} Money Transactions in Bank Request '),
                                             'BankTransactions', bank_transaction.slug,
                                             _(f'Complete {bank_transaction.transaction_category} Money Transactions in Bank With Amount {bank_transaction.amount}'),
                                             _(f'Complete {bank_transaction.transaction_category} Money Transactions in Bank With Amount {bank_transaction.amount} By {current_user.get_full_name()} By Note {bank_transaction.note}'
                                               f'  The Transaction Request Under Code {bank_transaction.code}'),
                                             bank_transaction.create_at, None, 'User', request.user.id,
                                             'User', user.id, 'Wallet', wallet.id,
                                             'User', auditor.auditor.id)
            elif check_not_approved > 0:
                print('elif check_not_approved')
                bank_transaction.transaction_status = 'Failed'
                bank_transaction.save()
                users = User.objects.filter(have_wallet=True)
                auditor = OperationTransactionAccounts.objects.all().last()
                for user in users:
                    wallet = Wallet.objects.get(user_nuc=user.nuc)
                    AdminCommonNotifications(request, _(f'Not Approved Money  Transactions Request '), False, False,
                                             False,
                                             _(f'Not Approved {bank_transaction.transaction_category} Money Transactions in Bank Request '),
                                             'BankTransactions', bank_transaction.slug,
                                             _(f'Not Approved {bank_transaction.transaction_category} Money Transactions in Bank With Amount {bank_transaction.amount}'),
                                             _(f'Not Approved {bank_transaction.transaction_category} Money Transactions in Bank With Amount {bank_transaction.amount} By {current_user.get_full_name()} By Note {bank_transaction.note}'
                                               f'  The Transaction Request Under Code {bank_transaction.code}'),
                                             bank_transaction.create_at, None, 'User', request.user.id,
                                             'User', user.id, 'Wallet', wallet.id,
                                             'User', auditor.auditor.id)
            elif check_partial_approved > 0:
                print('elif check_partial_approved')
                bank_transaction.transaction_status = 'Partial'
                bank_transaction.save()
                users = User.objects.filter(have_wallet=True)
                auditor = OperationTransactionAccounts.objects.all().last()
                for user in users:
                    wallet = Wallet.objects.get(user_nuc=user.nuc)
                    AdminCommonNotifications(request, _(f'Partial Approved Money  Transactions Request '), False, False,
                                             False,
                                             _(f'Partial Approved {bank_transaction.transaction_category} Money Transactions in Bank Request '),
                                             'BankTransactions', bank_transaction.slug,
                                             _(f'Partial Approved {bank_transaction.transaction_category} Money Transactions in Bank With Amount {bank_transaction.amount}'),
                                             _(f'Partial Approved {bank_transaction.transaction_category} Money Transactions in Bank With Amount {bank_transaction.amount} By {current_user.get_full_name()} By Note {bank_transaction.note}'
                                               f'  The Transaction Request Under Code {bank_transaction.code}'),
                                             bank_transaction.create_at, None, 'User', request.user.id,
                                             'User', user.id, 'Wallet', wallet.id,
                                             'User', auditor.auditor.id)
            print('Partial Approved')
            messages.success(request,
                             _(f'You Approved {bank_transaction.transaction_category} Money Transactions in Bank With Amount {bank_transaction.amount}'),
                             extra_tags='Wallet Transactions')
            return redirect(request.META['HTTP_REFERER'])
        else:
            print('Not Approved')
            messages.error(request, _(f'You Not Have Permission To Approve This Transaction'),
                           extra_tags='Wallet Transactions')
            return redirect(request.META['HTTP_REFERER'])


################TreasuryTransactions ####################



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
            transaction_amount = request.POST.get('treasury_amount')
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
                if Decimal(last_bank.amount) < Decimal(transaction_amount) or Decimal(last_bank.amount) <= 0:
                    messages.error(request, _("A bank account does not cover your application , Please Try Again"),
                                   extra_tags='Wallet Transactions')
                    return redirect(request.META['HTTP_REFERER'])
                else:
                    if check_treasury > 0:
                        transaction_type = 'Withdraw'
                        treasury_receive = Decimal(last_treasury.receive) + Decimal(transaction_amount)
                        treasury_send = Decimal(last_treasury.send)
                        treasury_amount = Decimal(last_treasury.amount) + Decimal(transaction_amount)
                        bank_transaction_type = 'Deposit'
                        bank_transaction_category = 'Expense'


                    else:
                        transaction_type = 'Withdraw'
                        treasury_receive = Decimal(transaction_amount)
                        treasury_send = 0
                        treasury_amount = Decimal(transaction_amount)
                        bank_transaction_type = 'Deposit'
                        bank_transaction_category = 'Expense'

                    AdminCommonTreasuryTransactionsIncome(request, transaction_amount, transaction_type,
                                                          transaction_mode, 'Partial',
                                                          transaction_category, treasury_amount,
                                                          treasury_note,
                                                          wallet, bank_transaction_type, bank_transaction_category,
                                                           month, year)
                    messages.success(request, _("Treasury Transactions Successfully Added"),
                                     extra_tags='Wallet Transactions')
                    return redirect(request.META['HTTP_REFERER'])
            elif transaction_category == 'Expense':
                if last_treasury == None:
                    print('last_treasury == None')
                    messages.error(request, _("A Treasury account does not cover your application , Please Try Again"),
                                   extra_tags='Wallet Transactions')
                    return redirect(request.META['HTTP_REFERER'])
                if Decimal(last_treasury.amount) <= 0 :
                    print('Decimal(last_treasury.amount) <= 0')
                    messages.error(request, _("A Treasury account does not cover your application , Please Try Again"),
                                   extra_tags='Wallet Transactions')
                    return redirect(request.META['HTTP_REFERER'])
                else:
                    if check_treasury > 0 and Decimal(last_treasury.amount) >= Decimal(transaction_amount):
                        print('check_treasury > 0 and Decimal(last_treasury.amount) >= Decimal(treasury_amount)')
                        transaction_type = 'Deposit'
                        treasury_receive = Decimal(last_treasury.receive)
                        treasury_send = Decimal(last_treasury.send) + Decimal(transaction_amount)
                        treasury_amount = Decimal(last_treasury.amount) - Decimal(transaction_amount)
                        bank_transaction_type = 'Withdraw'
                        bank_transaction_category = 'Income'


                        AdminCommonTreasuryTransactionsExpense(request, transaction_amount, transaction_type,
                                                               transaction_mode, 'Partial',
                                                               transaction_category, treasury_amount,
                                                               treasury_note,
                                                               wallet, bank_transaction_type, bank_transaction_category,
                                                                month, year)
                        messages.success(request, _("Treasury Transactions Successfully Added"),
                                         extra_tags='Wallet Transactions')
                        return redirect(request.META['HTTP_REFERER'])
                    else:
                        messages.error(request,
                                       _("A Treasury account does not cover your application , Please Try Again"),
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


@authenticated_staf
@staff_only
def AdminCommonTreasuryTransactionsIncome(request,transaction_amount, transaction_type, transaction_mode, transaction_status,
                                                          transaction_category, treasury_amount,  treasury_note,
                                                          wallet, bank_transaction_type,bank_transaction_category, month,year ):
    system_wallet = SystemWallet.objects.get(secret='SystemWallet')
    current_user = User.objects.get(id=request.user.id)
    auditor = OperationTransactionAccounts.objects.all().last()
    treasury_form = TreasuryTransactions( system_wallet=system_wallet,
                                         sender_model=ContentType.objects.get(model='User'),
                                         sender_id=current_user.id,
                                         receiver_model=ContentType.objects.get(model='SystemWallet'),
                                         receiver_id=system_wallet.id,
                                         owner_model=ContentType.objects.get(model='Wallet'),
                                         owner_id=wallet.id,
                                         auditor_model=ContentType.objects.get(model='User'),
                                         auditor_id=auditor.auditor.id, transaction_type=transaction_type,
                                         transaction_mode=transaction_mode, transaction_status=transaction_status,
                                         transaction_category=transaction_category, amount=treasury_amount,
                                         receive=transaction_amount, send=0, note=treasury_note, )
    treasury_form.save()
    AdminMoneyTransaction(request,'SystemWallet', system_wallet.id, 'BankTransactions', treasury_form.id,
                          transaction_type,
                          transaction_amount, month, year)
    system_wallet.amount -= Decimal(transaction_amount)
    system_wallet.earning -= Decimal(transaction_amount)
    system_wallet.send +=  Decimal(transaction_amount)
    system_wallet.treasury +=Decimal(transaction_amount)
    system_wallet.save()
    AdminCommonPercentageTransactionsAdd(request, bank_transaction_type, transaction_mode, transaction_status,
                                         bank_transaction_category, 0, transaction_amount,
                                         f'_(Percentage Transactions With Bank Transactions , By Note)  {treasury_note} ',
                                         wallet, 'TreasuryTransactions', treasury_form.id, 'User', None,
                                         'Wallet', None, 'User', auditor.auditor.id)

    AdminCommonActionNeedApproved(request, 'User', request.user.id, 'TreasuryTransactions',
                                  treasury_form.id, 'Partial')

    users = User.objects.filter(have_wallet=True)

    for user in users:
        wallet = Wallet.objects.get(user_nuc=user.nuc)
        AdminCommonNotifications(request, _(f'Money Transactions in Treasury '), False, False, False,
                                 _(f'New {treasury_amount} {transaction_category} Money Transactions in Treasury '),
                                 'TreasuryTransactions', treasury_form.slug,
                                 _(f'New {transaction_category} Money Transactions in Bank With Amount {treasury_amount}'),
                                 _(f'New {transaction_category} Money Transactions in Bank With Amount {treasury_amount} By {current_user.get_full_name()} By Note {treasury_note}'),
                                 treasury_form.create_at, None, 'User', request.user.id,
                                 'User', user.id, 'Wallet', wallet.id,
                                 'User', auditor.auditor.id)


@authenticated_staf
@staff_only
def AdminCommonTreasuryTransactionsExpense(request,transaction_amount, transaction_type, transaction_mode, transaction_status,
                                                          transaction_category, treasury_amount,   treasury_note,
                                                          wallet, bank_transaction_type,bank_transaction_category, month,year ):
    system_wallet = SystemWallet.objects.get(secret='SystemWallet')
    current_user = User.objects.get(id=request.user.id)
    auditor = OperationTransactionAccounts.objects.all().last()
    treasury_form = TreasuryTransactions( system_wallet=system_wallet,
                                         sender_model=ContentType.objects.get(model='User'),
                                         sender_id=current_user.id,
                                         receiver_model=ContentType.objects.get(model='SystemWallet'),
                                         receiver_id=system_wallet.id,
                                         owner_model=ContentType.objects.get(model='Wallet'),
                                         owner_id=wallet.id,
                                         auditor_model=ContentType.objects.get(model='User'),
                                         auditor_id=auditor.auditor.id, transaction_type=transaction_type,
                                         transaction_mode=transaction_mode, transaction_status=transaction_status,
                                         transaction_category=transaction_category, amount=treasury_amount,
                                         receive=0, send=transaction_amount, note=treasury_note, )
    treasury_form.save()
    AdminMoneyTransaction(request,'SystemWallet', system_wallet.id, 'BankTransactions', treasury_form.id,
                          transaction_type,
                          transaction_amount, month, year)
    system_wallet.amount += Decimal(transaction_amount)
    system_wallet.earning += Decimal(transaction_amount)
    system_wallet.receive += Decimal(transaction_amount)
    system_wallet.treasury -= Decimal(transaction_amount)
    system_wallet.save()
    AdminCommonPercentageTransactionsAdd(request, bank_transaction_type, transaction_mode, transaction_status,
                                         bank_transaction_category, transaction_amount, 0,
                                         f'_(Percentage Transactions With Bank Transactions , By Note)  {treasury_note} ',
                                         wallet, 'TreasuryTransactions', treasury_form.id, 'User', None,
                                         'Wallet', None, 'User', auditor.auditor.id)

    AdminCommonActionNeedApproved(request, 'User', request.user.id, 'TreasuryTransactions',
                                  treasury_form.id, 'Partial')

    users = User.objects.filter(have_wallet=True)

    for user in users:
        wallet = Wallet.objects.get(user_nuc=user.nuc)
        AdminCommonNotifications(request, _(f'Money Transactions in Treasury '), False, False, False,
                                 _(f'New {treasury_amount} {transaction_category} Money Transactions in Treasury '),
                                 'TreasuryTransactions', treasury_form.slug,
                                 _(f'New {transaction_category} Money Transactions in Bank With Amount {treasury_amount}'),
                                 _(f'New {transaction_category} Money Transactions in Bank With Amount {treasury_amount} By {current_user.get_full_name()} By Note {treasury_note}'),
                                 treasury_form.create_at, None, 'User', request.user.id,
                                 'User', user.id, 'Wallet', wallet.id,
                                 'User', auditor.auditor.id)



@authenticated_staf
@staff_only
def AdminPercentageTransactionsList(request):
    percentage_transactions = PercentageTransactions.objects.all()
    context = {
        'percentage_transactions': percentage_transactions,
        'current_page': _('Percentage Transactions'),

    }
    return render(request, f'{BACKEND_TEMPLATES}/utilities/expenses/admin.html', context)


def AdminCommonPercentageTransactionsAdd(request, transaction_type, transaction_mode, transaction_status,
                                         transaction_category, receive, send, note,
                                         wallet, sender_model, sender_id, receiver_model, receiver_id, owner_model,
                                         owner_id,
                                         auditor_model, auditor_id):
    try:
        partner_percent = PartnerPercentage.objects.all()
    except Exception as e:
        messages.error(request,
                       _(f"There are no Any Partner Percentage In DataBase ,Please Add Some Partner Percentage First  , {e}"),
                       extra_tags='Wallet Transactions')
    system_wallet = SystemWallet.objects.get(secret='SystemWallet')

    last_amount = system_wallet.amount

    i = 0
    for partner in partner_percent:
        current_percent = Decimal(int(last_amount) * (int(partner.percent) / 100))
        user_wallet = Wallet.objects.get(user_nuc=partner.partner.nuc)
        try:
            percent_object_check = PercentageTransactions.objects.get_or_create(percent_type=partner.id)
            percent_object = PercentageTransactions.objects.get(percent_type=partner.id)
            percent_object.amount = last_amount
            percent_object.percent = current_percent
            percent_object.save()
        except Exception as e:
            print('error from last transaction ', e)
            percentage_object = PercentageTransactions.objects.create(wallet=user_wallet,system_wallet=system_wallet,
                                                                      sender_model=ContentType.objects.get(
                                                                          model=sender_model),
                                                                      sender_id=sender_id,
                                                                      receiver_model=ContentType.objects.get(
                                                                          model=receiver_model),
                                                                      receiver_id=partner.partner.id,
                                                                      owner_model=ContentType.objects.get(
                                                                          model=owner_model),
                                                                      owner_id=user_wallet.id,
                                                                      auditor_model=ContentType.objects.get(
                                                                          model=auditor_model),
                                                                      auditor_id=auditor_id,
                                                                      transaction_type=transaction_type,
                                                                      transaction_mode=transaction_mode,
                                                                      transaction_status='Pending',
                                                                      transaction_category=transaction_category,
                                                                      amount=last_amount,
                                                                      percent=current_percent,
                                                                      percent_type=PartnerPercentage.objects.get(
                                                                          id=partner.id),
                                                                      receive=receive, send=send, note=note, )

        i += 1


def AdminCommonSystemWalletTransactionsAdd(request, earning, amount, paid, due, receive, send, note, ):
    try:
        system_wallet = SystemWallet.objects.get(secret='SystemWallet')
        system_wallet.earning = earning
        system_wallet.amount = amount
        system_wallet.paid = paid
        system_wallet.due = due
        system_wallet.receive += receive
        system_wallet.send += send
        system_wallet.note = note
        system_wallet.save()
    except Exception as e:
        messages.error(request,
                       _(f"There are no Any System Wallet In DataBase ,Please Add Some System Wallet First  , {e}"),
                       extra_tags='Wallet Transactions')


@authenticated_staf
@staff_only
def AdminExpensesTransactionsList(request):
    expenses_transactions = ExpensesTransactions.objects.all()
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
            last_treasury = None
            transaction_type = None
            receive = None
            send = None
            earning = None
            transaction_category = 'Expense'
           
            garage = CarGarage.objects.get(id=1)
            print(2)
            try:
                last_expenses = ExpensesTransactions.objects.filter(system_wallet=system_wallet).last()
            except Exception as e:
                print('error from last transaction ', e)
                last_expenses = 0
            print(3)
            try:
                print(4)
                last_treasury = TreasuryTransactions.objects.filter(system_wallet=system_wallet).last()
                print(5, last_treasury.earning)

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
                print(4)

                print('error from last transaction ', e)
                try:
                    transaction_type = 'Deposit'
                    send = expenses_amount
                    earning = expenses_amount
                except Exception as e:
                    messages.error(request, _(f"There are no funds in the company's Treasury account or , {e}"),
                                   extra_tags='Expenses Transactions')
                    return redirect(request.META['HTTP_REFERER'])
            print(5)

            if expenses_form.is_valid():
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
                                  expenses_amount,month=last_treasury.month, year=last_treasury.year)
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
            'expenses_transactions': expenses_transactions,
            'expenses_form': expenses_form,
            'current_page': _('Treasury Transactions'),
            'prev_Page': _('Treasury'),
            'prev_Page_link': reverse_lazy('core:AdminExpensesTransactionsList'),
        }

        return render(request, f'{BACKEND_TEMPLATES}/utilities/expenses/admin.html', context)

    context = {
        'expenses_transactions': expenses_transactions,
        'expenses_form': expenses_form,
        'current_page': _('Treasury Transactions'),
        'prev_Page': _('Treasury'),
        'prev_Page_link': reverse_lazy('core:AdminExpensesTransactionsList'),
    }

    return render(request, f'{BACKEND_TEMPLATES}/utilities/expenses/admin.html', context)




