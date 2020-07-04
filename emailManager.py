import os
import smtplib
from email.message import EmailMessage
# from sendEmail import template_reader


class GMailClient:
    def __init__(self):
        pass

    def sendEmail(self, receiver_name, receiver_email):
        EMAIL_ADDRESS = os.environ.get('EMAIL_ID')
        EMAIL_PASSWORD = os.environ.get('EMAIL_PASSWORD')
        # EMAIL_ADDRESS = 'street.hawk492@gmail.com'
        # EMAIL_PASSWORD = 'kr$vivek9097'

        msg = EmailMessage()
        msg['Subject'] = 'Detailed Covid-19 Report!'
        msg['From'] = EMAIL_ADDRESS
        msg['To'] = receiver_email

        # value = contacts[3]
        # values = value.get("cases")
        msg.set_content("Hello Mr. {} Here is your Covid 19 Report PFA".format(receiver_name))
        # template = template_reader.TemplateReader()
        # email_message = template.read_course_template("simple")
        # #print(email_message)
        # country_name1 = "India"
        # total1 = str(values.get("total"))
        # new1 = str(values.get("new"))
        # active1 = str(values.get("active"))
        # critical1 = str(values.get("critical"))
        # recovered1 = str(values.get("recovered"))
        # print(new1 + total1)
        #.format(code1=code1, code2=code2, code3=code3, code4=code4, code5=code5

        '''msg.add_alternative(email_message.format(country_name=country_name1, total=total1, new=new1, active=active1, critical=critical1,
                                       recovered=recovered1,subtype='html'))'''



        # msg.add_alternative(email_message.format(country_name=country_name1, total=total1, new=new1, active=active1, critical=critical1,
        #                             recovered=recovered1), subtype='html')

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            smtp.send_message(msg)

        return True
