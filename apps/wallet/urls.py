from django.urls import path


from apps.wallet.views.transaction import AdminBankTransactionAdd, AdminCommonBankTransactionsExpenseApprove, \
    AdminTreasuryTransactionsAdd, AdminExpensesTransactionsList, AdminPercentageTransactionsList


from apps.wallet.views.wallet import UserWalletLocked, CreateWallet, AdminWalletUserView, UserWalletChangeInfo, \
    walletLogout, AdminWalletUserReset

app_name = 'wallet'

urlpatterns = [

    # ########## Wallet Admin #########

     path('wallet/lock/', UserWalletLocked, name='AdminUserWalletLocked'),
    path('wallet/add/', CreateWallet, name='AdminCreateWallet'),
    path('wallet/user/<slug:slug>', AdminWalletUserView, name='AdminWalletUserView'),
    path('wallet/change/<slug:slug>', UserWalletChangeInfo, name='AdminWalletChangeInfo'),
    path('wallet/logout/<slug:slug>', walletLogout, name='AdminWalletUserLogout'),
    path('wallet/rerset/', AdminWalletUserReset, name='AdminWalletUserReset'),

    # ########## Wallet Bank Transaction Admin #########
    path('wallet/bank/transaction/add/<slug:slug>', AdminBankTransactionAdd, name='AdminBankTransactionAdd'),
    path('wallet/treasury/transaction/aprove/', AdminCommonBankTransactionsExpenseApprove,
         name='AdminCommonBankTransactionsExpenseApprove'),

    path('wallet/treasury/transaction/add/<slug:slug>', AdminTreasuryTransactionsAdd,
         name='AdminTreasuryTransactionsAdd'),

    path('wallet/expenses/transaction/', AdminExpensesTransactionsList, name='AdminExpensesTransactionsList'),

    path('wallet/percentage/transaction/', AdminPercentageTransactionsList, name='AdminPercentageTransactionsList'),
    # path('wallet/expenses/transaction/add/', AdminExpensesTransactionsAdd, title='AdminExpensesTransactionsAdd'),
]
