
from Products.validation import validation

def sendSignupNotificationEmail(obj, event):
    isEmail = validation.validatorFor('isEmail')
    
    if event.transition and event.transition.id == 'signup':
        person = obj
        timeSlot = person.aq_parent
        day = timeSlot.aq_parent
        signupSheet = day.aq_parent
        contactInfo = signupSheet.getContactInfo()

        toEmail = person.getEmail()
        if (isEmail(toEmail) == 1):        
            fromEmail = "%s <%s>" % (obj.email_from_name, obj.email_from_address)
            subject = signupSheet.Title() + ' - Registration Confirmation'

            message = 'Hi ' + person.Title() + ',\n\n'
            message += 'This message is to confirm that you have signed up for:\n'
            message += timeSlot.getLabel() + '\n\n'
            message += 'For the ' + signupSheet.Title() + ' Signup Sheet: ' + signupSheet.absolute_url() + '\n\n'
            message += 'If you have any questions please contact:\n'
            for line in contactInfo:
                message += line + '\n'
            message += '\n'
            
            mailHost = obj.MailHost
            mailHost.secureSend(message, toEmail, fromEmail, subject)
                
