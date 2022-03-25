import smtplib
from datetime import datetime
from email.message import EmailMessage
from .models import Invoices

def email_notify(subject,body,to):
    msg=EmailMessage()
    msg.set_content(body)
    msg['subject']=subject
    msg['to']=to
    
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
    GSTIN_no = '18AABCU9603R1ZM'
    invoice_no = f'INV-{int(count)+1}'
    date = datetime.now().date()
    time = datetime.now().time().strftime('%H:%M:%S')
    new_line = '\n'
    body = f'{new_line} INVENTORY MANAGEMENT SYSTEM {new_line} Shivajinagar,Pune {new_line} {new_line} Customer:- {name} {new_line} {email}{new_line}{phone} {new_line} {new_line} GSTIN No. - {GSTIN_no} {new_line} Invoice No.- {invoice_no}{new_line}{new_line} Item \t\t\t Quantity \t\t Price {new_line} {product_name} \t\t\t {quantity} \t\t\t {price} {new_line} Gst \t\t\t\t\t\t\t 18%{new_line} Total \t\t\t\t\t\t\t {total_price}  {new_line} {new_line} Staff Name:-{staff} {new_line} Purchased On:- {date} - {time} {new_line}{new_line} Thanks. Welcome Again \U0001F601'
    invoice = Invoices(invoice_id = invoice_no, name=name, email=email, phone_no=phone, product=product_name, staff= staff, order_quantity=quantity, price=price, total_price=total_price)
    invoice.save()
    return body, invoice_no, invoice.id