from .models import ParentInvoice
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import EmailMessage
from .invoice_template import invoice_constructor


@receiver(post_save, sender=ParentInvoice)
def send_invoice_email(sender, instance,**kwargs):
    if instance.status == 'Confirmed':
        invoice = invoice_constructor(instance,for_mail=True)
        email = EmailMessage(
            'New Invoice',
            f'Invoice {instance.invoice} has been created',
            'nodarisvanidze88@gmail.com',
            ['info@bsi.ge'],)
        email.attach('invoice.xlsx', invoice, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        email.send()
        