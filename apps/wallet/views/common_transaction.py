from decimal import Decimal
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType

from apps.wallet.models.models import WalletMoney, SystemWallet
from apps.wallet.models.transaction import MoneyTransaction, OperationTransaction, OperationTransactionHistory, \
    BankTransactions, TreasuryTransactions, ExpensesTransactions, AppTransactions

User = get_user_model()


###################### Wallet Money ######################
def CommonWalletMoney(request, wallet, user, owner_model, owner_id,transaction_category, amount, earning,paid,due,receive,send):
    try:
        transaction_object = WalletMoney.objects.get(wallet=wallet.id,owner_model=ContentType.objects.get(model=owner_model),owner_id=owner_id)
        if transaction_category == 'Income':
            transaction_object.earning += Decimal(earning)
            transaction_object.amount += Decimal(amount)
            transaction_object.receive += Decimal(receive)
        elif transaction_category == 'Expense':
            transaction_object.paid += Decimal(paid)
            transaction_object.amount -= Decimal(amount)
            transaction_object.send += Decimal(send)
        elif transaction_category == 'Due':
            transaction_object.due += Decimal(due)
            transaction_object.amount += Decimal(amount)
        transaction_object.transaction_category = transaction_category
        transaction_object.save()
    except MoneyTransaction.DoesNotExist:
        transaction_object = MoneyTransaction.objects.create(wallet=wallet, owner_model=ContentType.objects.get(model=owner_model),
                                                             owner_id=owner_id,transaction_category=transaction_category, amount=amount,earning=earning,paid=paid,due=due,
                                                             receive=receive,send=send)

def CommonSystemWallet(request, secret, transaction_category, amount, earning,profit, paid, due,receive,send,bank,treasury,
                       custody,projects,projects_actual,projects_earning,projects_paid,projects_due,stores,actual,expenses,month,year):
    try:
        transaction_object = SystemWallet.objects.get(secret=secret,month=month,year=year)
        if transaction_category == 'Income':
            transaction_object.earning += Decimal(earning)
            transaction_object.amount += Decimal(amount)
            transaction_object.receive += Decimal(receive)
        elif transaction_category == 'Expense':
            transaction_object.paid += Decimal(paid)
            transaction_object.amount -= Decimal(amount)
            transaction_object.send += Decimal(send)
        elif transaction_category == 'Due':
            transaction_object.due += Decimal(due)
            transaction_object.amount += Decimal(amount)
        transaction_object.transaction_category = transaction_category
        transaction_object.save()
    except SystemWallet.DoesNotExist:
        transaction_object = SystemWallet.objects.create(secret=secret,transaction_category=transaction_category, amount=amount,earning=earning,profit=profit,paid=paid,due=due,
                                                         receive=receive,send=send,bank=bank,treasury=treasury,custody=custody,projects=projects,projects_actual=projects_actual,
                                                         projects_earning=projects_earning,projects_paid=projects_paid,projects_due=projects_due,stores=stores,actual=actual,expenses=expenses,month=month,year=year)


###################### Transaction Money ######################
def AdminMoneyTransaction(request, sender_model, sender_id, receiver_model, receiver_id, transaction_type, amount, month,
                      year):
    return MoneyTransaction.objects.create(
        sender_model=ContentType.objects.get(model=sender_model),
        sender_id=sender_id,
        receiver_model=ContentType.objects.get(model=receiver_model),
        receiver_id=receiver_id,
        transaction_type=transaction_type,
        amount=amount,
        month=month,
        year=year,
    )



def AdminCommonBankTransactions(request, sender_model, sender_id, receiver_model, receiver_id,owner_model,owner_id,
                                    auditor_model,auditor_id,transaction_type,transaction_mode, transaction_status,transaction_category,
                           amount,receive,send,note,month,year):
    transaction = BankTransactions.objects.create(sender_model=ContentType.objects.get(model=sender_model),sender_id=sender_id,
                                                      receiver_model=ContentType.objects.get(model=receiver_model),receiver_id=receiver_id,
                                                      owner_model=ContentType.objects.get(model=owner_model),owner_id=owner_id,
                                                      auditor_model=ContentType.objects.get(model=auditor_model),auditor_id=auditor_id,
                                                      transaction_type=transaction_type,transaction_mode=transaction_mode,transaction_status=transaction_status,
                                                      transaction_category=transaction_category,amount=amount,receive=receive,send=send,note=note,month=month,year=year)



def AdminCommonTreasuryTransactions(request, sender_model, sender_id, receiver_model, receiver_id,owner_model,owner_id,
                                    auditor_model,auditor_id,transaction_type,transaction_mode, transaction_status,transaction_category,
                           amount,receive,send,note,month,year):
    transaction = TreasuryTransactions.objects.create(sender_model=ContentType.objects.get(model=sender_model),sender_id=sender_id,
                                                      receiver_model=ContentType.objects.get(model=receiver_model),receiver_id=receiver_id,
                                                      owner_model=ContentType.objects.get(model=owner_model),owner_id=owner_id,
                                                      auditor_model=ContentType.objects.get(model=auditor_model),auditor_id=auditor_id,
                                                      transaction_type=transaction_type,transaction_mode=transaction_mode,transaction_status=transaction_status,
                                                      transaction_category=transaction_category,amount=amount,receive=receive,send=send,note=note,month=month,year=year)
    return transaction

def AdminCommonExpensesTransactions(request, sender_model, sender_id, receiver_model, receiver_id,owner_model,owner_id,
                                    auditor_model,auditor_id,transaction_type,transaction_mode, transaction_status,transaction_category,
                           amount,receive,send,note,month,year):
    transaction = ExpensesTransactions.objects.create(sender_model=ContentType.objects.get(model=sender_model),sender_id=sender_id,
                                                      receiver_model=ContentType.objects.get(model=receiver_model),receiver_id=receiver_id,
                                                      owner_model=ContentType.objects.get(model=owner_model),owner_id=owner_id,
                                                      auditor_model=ContentType.objects.get(model=auditor_model),auditor_id=auditor_id,
                                                      transaction_type=transaction_type,transaction_mode=transaction_mode,transaction_status=transaction_status,
                                                      transaction_category=transaction_category,amount=amount,receive=receive,send=send,note=note,month=month,year=year)
    return transaction

def AdminCommonAppTransactions(request, sender_model, sender_id, receiver_model, receiver_id,owner_model,owner_id,
                                    auditor_model,auditor_id,transaction_type,transaction_mode, transaction_status,transaction_category,
                           amount,receive,send,note,month,year):
    transaction = AppTransactions.objects.create(sender_model=ContentType.objects.get(model=sender_model),sender_id=sender_id,
                                                      receiver_model=ContentType.objects.get(model=receiver_model),receiver_id=receiver_id,
                                                      owner_model=ContentType.objects.get(model=owner_model),owner_id=owner_id,
                                                      auditor_model=ContentType.objects.get(model=auditor_model),auditor_id=auditor_id,
                                                      transaction_type=transaction_type,transaction_mode=transaction_mode,transaction_status=transaction_status,
                                                      transaction_category=transaction_category,amount=amount,receive=receive,send=send,note=note,month=month,year=year)
    return transaction
def AdminCommonOperationTransaction(request, sender_model, sender_id, receiver_model, receiver_id,owner_model,owner_id,
                                    transaction_type,reason, amount,due,paid,paid_date,due_date,month,year):
    try:
        transaction_object = OperationTransaction.objects.get(sender_model=ContentType.objects.get(model=sender_model),sender_id=sender_id
                                                              ,owner_model=ContentType.objects.get(model=owner_model),owner_id=owner_id,
                                                              receiver_model=ContentType.objects.get(model=receiver_model),receiver_id=receiver_id,
                                                              month=month,year=year)
        if transaction_type == 'Cost':
            transaction_object.due += Decimal(due)
            transaction_object.amount -= Decimal(amount)
            transaction_object.due_date = due_date
        elif transaction_type == 'Truncate':
            transaction_object.due += Decimal(due)
            transaction_object.amount -= Decimal(amount)
            transaction_object.due_date = due_date
        elif transaction_type == 'Acquisition':
            transaction_object.paid += Decimal(paid)
            transaction_object.amount += Decimal(amount)
            transaction_object.paid_date = paid_date
        elif transaction_type == 'Leasing':
            transaction_object.due += Decimal(due)
            transaction_object.amount += Decimal(amount)
            transaction_object.cost += Decimal(due)
            transaction_object.due_date = due_date
        elif transaction_type == 'Leasing Cost' or transaction_type == 'Salary':
            transaction_object.paid += Decimal(paid)
            transaction_object.due -= Decimal(amount)
            transaction_object.paid_date = paid_date
        transaction_object.save()
    except OperationTransaction.DoesNotExist:
        transaction = OperationTransaction.objects.create(sender_model=ContentType.objects.get(model=sender_model),sender_id=sender_id,
                                                          receiver_model=ContentType.objects.get(model=receiver_model),receiver_id=receiver_id,
                                                          owner_model=ContentType.objects.get(model=owner_model),owner_id=owner_id,
                                                          transaction_type=transaction_type,reason=reason, amount=amount,cost=due,due=due,
                                                          paid=paid,paid_date=paid_date,due_date=due_date,month=month,year=year)



def AdminCommonOperationTransactionHistory(request, sender_model, sender_id, receiver_model, receiver_id,owner_model,owner_id,
                                    transaction_type,reason, amount,due,paid,paid_date,due_date,month,year):
    transaction = OperationTransactionHistory.objects.create(sender_model=ContentType.objects.get(model=sender_model),sender_id=sender_id,
                                                      receiver_model=ContentType.objects.get(model=receiver_model),receiver_id=receiver_id,
                                                      owner_model=ContentType.objects.get(model=owner_model),owner_id=owner_id,
                                                      transaction_type=transaction_type,reason=reason, amount=amount,cost=due,due=due,
                                                      paid=paid,paid_date=paid_date,due_date=due_date,month=month,year=year)