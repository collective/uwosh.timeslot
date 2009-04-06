
def sendSignupNotificationEmail(obj, event):
    if event.transition and event.transition.id == 'signup':
        person = obj
        timeSlot = person.aq_parent
        day = timeSlot.aq_parent
        signupSheet = day.aq_parent

        toEmail = person.getEmail()
        fromEmail = "%s <%s>" % (obj.email_from_name, obj.email_from_address)
        subject = signupSheet.Title() + ' - Registration Confirmation'
        message = 'Hi ' + person.Title() + ',\n\n'
        message += 'You have been signed up for: ' + timeSlot.getLabel()
        
        mailHost = obj.MailHost
        mailHost.secureSend(message, toEmail, fromEmail, subject)
                
