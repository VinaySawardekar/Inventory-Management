from email import encoders
import smtplib
from datetime import datetime
from email.message import EmailMessage
from .models import Invoices
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.mime.base import MIMEBase

def email_notify(subject,body,to):
    # msg = MIMEMultipart('alternative')
    msg=EmailMessage()
    msg.set_content(body)
    msg['subject']=subject
    msg['to']=to
    # msg.attach(body)
    # msg.attach(pdf)
    
    user = "nikhiltaneja223@gmail.com"
    msg['from']=user
    password = "wyjvnerqxlhvxxwt"
    
    server = smtplib.SMTP("smtp.gmail.com",587)
    server.starttls()
    server.login(user,password)
    server.send_message(msg)
    
    server.quit()

def generateinvoice(product_name, quantity,price, total_price, name, email, phone, staff):
    count = Invoices.objects.all().count()
    temp_id = Invoices.objects.values_list('temp_id_2', flat=True).all().order_by('-date')[:1]
    GSTIN_no = '18AABCU9603R1ZM'
    invoice_no = f'INV-{int(count)+1}'
    date = datetime.now().date()
    time = datetime.now().time().strftime('%H:%M:%S')
    new_line = '\n'
    body = f'{new_line} INVENTORY MANAGEMENT SYSTEM {new_line} Shivajinagar,Pune {new_line} {new_line} Customer:- {name} {new_line} {email}{new_line}{phone} {new_line} {new_line} GSTIN No. - {GSTIN_no} {new_line} Invoice No.- {invoice_no}{new_line}{new_line} Item \t\t\t Quantity \t\t Price {new_line} {product_name} \t\t\t {quantity} \t\t\t {price} {new_line} Gst \t\t\t\t\t\t\t 18%{new_line} Total \t\t\t\t\t\t\t {total_price}  {new_line} {new_line} Staff Name:-{staff} {new_line} Purchased On:- {date} - {time} {new_line}{new_line} Thanks. Welcome Again \U0001F601'
    invoice = Invoices(invoice_id = invoice_no, name=name, email=email, phone_no=phone, product=product_name, staff= staff, order_quantity=quantity, price=price, total_price=total_price, temp_id=temp_id, temp_id_2 = temp_id)
    invoice.save()
    return body, invoice_no, invoice.id

from io import BytesIO #A stream implementation using an in-memory bytes buffer
                       # It inherits BufferIOBase
 
from django.http import HttpResponse
from django.template.loader import get_template
 
#pisa is a html2pdf converter using the ReportLab Toolkit,
#the HTML5lib and pyPdf.
 
from xhtml2pdf import pisa  
#difine render_to_pdf() function
 
def render_to_pdf(template_src, context_dict={}):
     template = get_template(template_src)
     html  = template.render(context_dict)
     result = BytesIO()
 
     #This part will create the pdf.
     pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")), result)
     print(pdf)
     if not pdf.err:
        #  return pdf
         return HttpResponse(result.getvalue(), content_type='application/pdf')
     return None
 