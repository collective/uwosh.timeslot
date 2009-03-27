## Script (Python) "notifyPerson"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=review_state
##title=
##
person = review_state.object
timeSlot = person.aq_parent
day = timeSlot.aq_parent
signupSheet = day.aq_parent

toEmail = person.getEmail()
fromEmail = "%s <%s>" % (context.email_from_name, context.email_from_address)
subject = signupSheet.Title() + ' - Registration Confirmation'
message = 'Hi ' + person.Title() + ',\n\n'
message += 'You have been signed up for: ' + timeSlot.getLabel()

mailHost = context.MailHost
mailHost.secureSend(message, toEmail, fromEmail, subject)
