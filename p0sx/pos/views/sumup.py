from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction as django_transaction, IntegrityError

from django_q.tasks import async_task

from ..models.stock import Order, PaymentState, OrderState
from ..models.sumup_cloud import SumupTransaction
from ..service.sumup import get_sumup_transaction

import json
import logging

logger = logging.getLogger(__name__)

@csrf_exempt
def sumup_ordercallback(request, order_id):
    callback = json.loads(request.body)
    transaction_id = callback['payload']['client_transaction_id']
    logger.debug(callback)

    try:
        order = Order.objects.get(pk=order_id, payment_reference=transaction_id)
        transaction = get_sumup_transaction(transaction_id)
        logger.debug(transaction)
        transaction_status = None if transaction is None else transaction['status']
        if transaction_status == 'SUCCESSFUL':
            order.payment_state = PaymentState.Paid
            if order.state == OrderState.Open:
                async_task("pos.services.print_pickup_receipts", order.id,
                           task_name='Pickup receipts for order {id}'.format(id=order.id))
            order.save()
        elif transaction_status == 'FAILED':
            order.payment_state = PaymentState.Failed
            order.save()
        elif transaction_status == 'CANCELLED':
            order.payment_state = PaymentState.Cancelled
            order.save()
        elif transaction_status == 'PENDING':
            logger.info(f"Payment for order {order_id} is still pending...")

        return HttpResponse('OK')
    except:
        logger.error(f"pk: {order_id} client_transaction_id: '{transaction_id}' failed to get order")
        return HttpResponse(status=500)

@csrf_exempt
def sumup_creditcallback(request, transaction_id):
    callback = json.loads(request.body)
    client_transaction_id = callback['payload']['client_transaction_id']
    logger.debug(callback)

    try:
        transaction = SumupTransaction.objects.get(pk=transaction_id, payment_reference=client_transaction_id)
        sumup_transaction = get_sumup_transaction(client_transaction_id)
        logger.debug(sumup_transaction)
        transaction_status = None if sumup_transaction is None else sumup_transaction['status']
        if transaction_status == 'SUCCESSFUL':
            try:
                with django_transaction.atomic():
                    transaction.payment_state = PaymentState.Paid
                    if not transaction.used:
                        transaction.used = True
                        transaction.user.credit += transaction.amount
                        transaction.user.save()
                    transaction.save()
            except IntegrityError:
                return HttpResponse(status=500)
        elif transaction_status == 'FAILED':
            transaction.payment_state = PaymentState.Failed
            transaction.save()
        elif transaction_status == 'CANCELLED':
            transaction.payment_state = PaymentState.Cancelled
            transaction.save()
        elif transaction_status == 'PENDING':
            logger.info(f"Payment for transaction {transaction_id} is still pending...")

        return HttpResponse('OK')
    except:
        logger.error(f"pk: {transaction_id} client_transaction_id: '{client_transaction_id}' failed to get transaction")
        return HttpResponse(status=500)
