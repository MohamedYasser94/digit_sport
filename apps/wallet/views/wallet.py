from datetime import datetime, timedelta
from decimal import Decimal
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.db.models import Sum
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils import timezone
from django.utils.crypto import get_random_string
from django.utils.translation import gettext_lazy as _


from apps.wallet.forms.wallet import WalletLoginForm, WalletLockedUserForm, AdminBankTransactionsForm, \
    AdminTreasuryTransactionsForm
from apps.wallet.models.models import Wallet, WalletResetPassword, WalletLocked, SystemWallet
from apps.wallet.models.transaction import BankTransactions, TreasuryTransactions, ExpensesTransactions, \
    MoneyTransaction
from core.models.core import SystemSetting

from helper.commonHelper import BACKEND_TEMPLATES
from helper.decorators import staff_only, authenticated_staf

User = get_user_model()
UserModel = get_user_model()


@authenticated_staf
@staff_only
def UserWalletLocked(request):
   
    current_user = request.user
    user = User.objects.get(id=current_user.id)
    try:
        if check_wallet := WalletLocked.objects.get(user=request.user):
            if request.method == "POST":
                form = WalletLoginForm(request.POST or None)
                wallet_code = request.POST.get("wallet_code")
                password = request.POST.get("password")
                try:
                    wallet = WalletLocked.objects.get(wallet_code=wallet_code, password=password,
                                                      user=current_user.id)
                    wallet.status = 'Login'
                    wallet.save()

                    return redirect(reverse('wallet:AdminWalletUserView', args=[check_wallet.slug]))
                except Exception as e:
                    messages.error(request, _('The Wallet Code or Password Is Wrong'))
                    wallet_state = 'Password'
                    context = {'form': form, 'user': user, 'current_user': current_user, 'wallet_state': wallet_state}
                    return render(request, f'{BACKEND_TEMPLATES}/wallet/wallet_locked.html', context)

            else:
                wallet_state = 'Login'
                context = {'user': user, 'current_user': current_user, 'wallet_state': wallet_state}
            return render(request, f'{BACKEND_TEMPLATES}/wallet/wallet_locked.html', context)
    except Exception as e:
       
        wallet_state = 'Create Wallet'
        context = {
            'user': user,
            'current_user': current_user,
            'wallet_state': wallet_state,
            'current_page': _('Wallet Locked'),
        }
        return redirect(reverse('wallet:AdminCreateWallet', ), context)

    wallet_state = 'Login'
    context = {

        'user': user,
        'wallet_state': wallet_state,
        'current_page': _('Wallet Locked'),
    }
    return render(request, f'{BACKEND_TEMPLATES}/wallet/create_wallet.html', context)

def UserWalletLockedt(request):
    return render(request, 'good/wallet/wallet.html')

@authenticated_staf
@staff_only
def CreateWallet(request):
    current_user = request.user
    user = User.objects.get(id=current_user.id)
    form = WalletLockedUserForm()
    wallet_state = 'No Wallet'

    try:
       
        check_wallet = WalletLocked.objects.get(user=request.user)
        if check_wallet:
            wallet_state = 'You Have Wallet'

            context = {
                'user': user,
                'current_user': current_user,
                'wallet_state': wallet_state,
                'current_page': _('Wallet Locked'),
            }
            return render(request, f'{BACKEND_TEMPLATES}/wallet/wallet_suspend.html', context)

    except Exception as e:
       
        check_wallet = None
        form = WalletLockedUserForm()
        wallet_state = 'Creating Wallet'
        try:
            if check_wallet := WalletLocked.objects.get(
                    user=current_user,
                    status='Login',
            ):
                context = {
                    'user': user,
                    'current_user': current_user, }
                return redirect(reverse('wallet:AdminWalletUserView', args=[check_wallet.slug]), context)
        except Exception as e:
            messages.error(request, _(f'Something Wrong , Please Try Again ,{e}'), extra_tags='Wallet')
            if request.method == "POST":
                form = WalletLockedUserForm(request.POST or None, )
                if form.is_valid:
                    wallet_code = request.POST.get('wallet_code')
                    password = request.POST.get('password')
                    print('create wallet fun wallet_code -', wallet_code)
                    form = None
                    if not form:
                        locked_form = WalletLocked(user=user, user_nuc=user.nuc, wallet_code=wallet_code,
                                                   password=password, status='Login', )

                        locked_form.save()
                        wallet = Wallet()
                        wallet.wallet_locked = locked_form
                        wallet.user = locked_form.user
                        wallet.owner_model = ContentType.objects.get(model='User')
                        wallet.owner_id = locked_form.user.id
                        wallet.user_nuc = locked_form.user_nuc
                        wallet.status = True
                        wallet.save()
                        reset_code = get_random_string(length=32)
                        
                        wallet_reset = WalletResetPassword(wallet_locked=locked_form, user=user,
                                                           owner_model=ContentType.objects.get_for_model(User),
                                                           owner_id=user.id,
                                                           reset_code=reset_code, )
                        wallet_reset.save()
                        user = User.objects.get(id=user.id)
                        user.have_wallet = True
                        user.save()
                        return redirect(reverse('wallet:AdminWalletUserView', args=[locked_form.slug]))

                    # return HttpResponseRedirect(reverse_lazy('wallet:AdminWalletUserView', args=[locked_form.slug]))
                else:
                  

                    messages.error(request, _("Something Wrong , Please Try Again"), extra_tags='Wallet')
            else:
                form = WalletLockedUserForm()
                wallet_state = 'New Wallet'
                context = {
                    'user': user,
                    'form': form,
                    'wallet_state': wallet_state,
                    'current_page': _('Wallet Locked'),
                }
                return render(request, f'{BACKEND_TEMPLATES}/wallet/create_wallet.html', context)

    context = {
        'user': user,
        'form': form,
        'wallet_state': wallet_state,
    }
    return render(request, f'{BACKEND_TEMPLATES}/wallet/create_wallet.html', context)


@authenticated_staf
@staff_only
def UserWalletChangeInfo(request, slug):
    current_user = request.user
    user = User.objects.get(id=current_user.id)
    form = WalletLockedUserForm()
    wallet_state = 'Change Info '
    if request.method == "POST":

        form = WalletLockedUserForm(request.POST or None, )
        if form.is_valid:

            wallet_code = request.POST.get('wallet_code')
            password = request.POST.get('password')
            form = None
            if not form:
                form = WalletLocked.objects.get(user=user, status='Login')
                form.wallet_code = wallet_code
                form.password = password
                form.user = user
                form.user_nuc = user.nuc
                form.first_login = False
                form.status = 'Logout'
                form.save()
                wallet_state = 'Login'
            context = {
                'user': user,
                'form': form,
                'wallet_state': wallet_state,
            }
            return render(request, f'{BACKEND_TEMPLATES}/wallet/wallet_locked.html', context)
        else:


            messages.error(request, "Error")
    else:
        form = WalletLockedUserForm()
        wallet_state = 'Error fro create'
        context = {
            'user': user,
            'form': form,
            'wallet_state': wallet_state,
        }
        return render(request, f'{BACKEND_TEMPLATES}/wallet/wallet_locked.html', context)

    context = {
        'user': user,
        'form': form,
        'wallet_state': wallet_state,
    }
    return render(request, f'{BACKEND_TEMPLATES}/wallet/wallet_locked.html', context)


@authenticated_staf
@staff_only
def wallet_create_successful(request):
    current_user = request.user
    user = User.objects.get(id=current_user.id)
    context = {

        'user': user,
        'current_user': current_user, }
    return render(request, f'{BACKEND_TEMPLATES}/wallet/wallet_locked.html', )


@authenticated_staf
@staff_only
def AdminWalletUserView(request, slug):  # sourcery skip: aug-assign, convert-to-enumerate
    system_wallet_check = SystemWallet.objects.get_or_create(secret='SystemWallet')

    
    approved_form =AdminWalletActionNeedApprovedForm()
    can_approved_user = request.user.id

    try:
        check_wallet = WalletLocked.objects.get(slug=slug)
    except Exception as e:
        wallet_state = 'No Wallet Found'
        context = {
            'wallet_state': wallet_state,
        }
        return render(request, f'{BACKEND_TEMPLATES}/wallet/wallet_locked.html', context)


    current_user = request.user
   
    user_type = User.objects.get(id=current_user.id)
    
    bank_form = AdminBankTransactionsForm()
    treasury_form = AdminTreasuryTransactionsForm()
    percentage_form = AdminPartnerPercentageForm()
    check_wallet = WalletLocked.objects.get(user=current_user, slug=slug)
    wallet = Wallet.objects.get(user=current_user, wallet_locked=check_wallet)
    current_app = SystemSetting.objects.get(title='Digithup')
    wallet.app = current_app.app
    wallet.mode = user_type.access_level
    wallet.save()
    wallet_app = wallet.app
    wallet_mode = wallet.mode
    system_wallet = SystemWallet.objects.get(secret='SystemWallet')
    system_wallet.profit = Decimal(system_wallet.amount) - Decimal(system_wallet.projects_due)
    system_wallet.save()
    bank_transactions = None
    project_transactions = None
    projects_amount = None
    today = datetime.now()
   
    try:
        percentage_amount = PercentageTransactions.objects.get(receiver_id=request.user.id)
        partner_percent = PartnerPercentage.objects.get(partner=request.user.id)
    except Exception as e:
        messages.error(request, _(f'"No Partner Percentage Found" {e}'), extra_tags='Wallet Transactions')
        percentage_amount = None
        partner_percent =None

    try:

        bank_amount = BankTransactions.objects.filter(system_wallet=system_wallet).last()

        total_bank_send = BankTransactions.objects.filter(system_wallet=system_wallet).aggregate(TOTAL=Sum('send'))['TOTAL']
        total_bank_receive = BankTransactions.objects.filter(system_wallet=system_wallet).aggregate(TOTAL=Sum('receive'))['TOTAL']

        bank_transactions = BankTransactions.objects.all().order_by('-id')

        treasury_amount = TreasuryTransactions.objects.filter(system_wallet=system_wallet).last()
        treasury_transactions = TreasuryTransactions.objects.all()
        projects_amount = \
            MoneyTransaction.objects.filter(sender_model=ContentType.objects.get(model='CarProject'),month=today.month,year=today.year).aggregate(
                TOTAL=Sum('amount'))['TOTAL']
        project_transactions = CarProject.objects.all().order_by('-id')
        expenses_amount = ExpensesTransactions.objects.last()

        expenses_transactions = ExpensesTransactions.objects.all().order_by('-id')
        money_transactions = MoneyTransaction.objects.filter(created_at__lte=datetime.now(tz=timezone.utc),
                                                             created_at__gt=datetime.now(
                                                                 tz=timezone.utc) - timedelta(
                                                                 days=30))


        context = {

            'approved_form':approved_form,
            'can_approved_user':can_approved_user,
            'current_user': current_user,

            'bank_form': bank_form,
            'treasury_form': treasury_form,
            'percentage_form': percentage_form,
            'check_wallet': check_wallet,
            'wallet': wallet,
            'wallet_app': wallet_app,
            'wallet_mode': wallet_mode,
            'system_wallet': system_wallet,
            'bank_amount': bank_amount,
            'percentage_amount': percentage_amount,
            'partner_percent': partner_percent,
            'total_bank_send': total_bank_send,
            'total_bank_receive': total_bank_receive,
            'bank_transactions': bank_transactions,
            'treasury_amount': treasury_amount,
            'treasury_transactions': treasury_transactions,
            'project_transactions': project_transactions,
            'projects_amount': projects_amount,
            'expenses_amount': expenses_amount,
            'expenses_transactions': expenses_transactions,
            'money_transactions': money_transactions,
            'current_page': _('Wallet'),
        }
    except Exception as e:
        messages.error(request, _(f'Something wrong ,{e}'), extra_tags='Wallet Transactions')
        context = {
            'current_user': current_user,
            'bank_form': bank_form,
            'treasury_form': treasury_form,
            'percentage_form': percentage_form,
            'check_wallet': check_wallet,
            'wallet': wallet,
            'wallet_app': wallet_app,
            'wallet_mode': wallet_mode,
            'current_page': _('Wallet'),
        }
    return render(request, f'{BACKEND_TEMPLATES}/wallet/wallet.html', context)

    # return render(request, f'{BACKEND_TEMPLATES}/wallet/wallet_locked.html', context)


@authenticated_staf
@staff_only
def walletLogout(request, slug):
    user = User.objects.get(id=request.user.id)

    wallet = WalletLocked.objects.get(user=user.id, slug=slug)
    wallet.status = 'Logout'
    wallet.save()

    context = {
        'user': user,
        'current_user': user, }
    return redirect(reverse('wallet:AdminUserWalletLocked'), context)


@authenticated_staf
@staff_only
def AdminWalletUserReset(request):  # sourcery skip: aug-assign, convert-to-enumerate
    system_wallet_check = SystemWallet.objects.get(secret='SystemWallet')
    if request.method == 'POST':
        approved_form = True
        if approved_form:
            system_wallet = SystemWallet.objects.get(secret='SystemWallet')
            system_wallet.amount = 0
            system_wallet.earning = 0
            system_wallet.profile = 0
            system_wallet.due = 0
            system_wallet.receive = 0
            system_wallet.send = 0
            system_wallet.bank = 0
            system_wallet.treasury = 0
            system_wallet.custody = 0
            system_wallet.projects = 0
            system_wallet.projects_actual = 0
            system_wallet.projects_earning = 0
            system_wallet.projects_paid = 0
            system_wallet.projects_due = 0
            system_wallet.stores = 0
            system_wallet.actual = 0
            system_wallet.expenses = 0
            system_wallet.save()
            bank_amount = BankTransactions.objects.filter(system_wallet=system_wallet)
            for bank in bank_amount:
                bank.delete()
            treasury_amount = TreasuryTransactions.objects.filter(system_wallet=system_wallet)
            for treasury in treasury_amount:
                treasury.delete()

            money_amount = MoneyTransaction.objects.all()
            for money in money_amount:
                money.delete()

            expenses_amount = ExpensesTransactions.objects.all()
            for expenses in expenses_amount:
                expenses.delete()
            percentage_amount = PercentageTransactions.objects.all()
            for percentage in percentage_amount:
                percentage.delete()


        else:
            messages.error(request, _('Wallet Reset Failed'), extra_tags='Wallet Transactions')
            return redirect(reverse('wallet:AdminUserWalletLocked'))

    return redirect(reverse('wallet:AdminUserWalletLocked'))

    # return render(request, f'{BACKEND_TEMPLATES}/wallet/wallet_locked.html', context)
