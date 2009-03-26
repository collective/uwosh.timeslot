## Script (Python) "notifyUser"
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
fromEmail = 'scorcm43@uwosh.edu'
subject = 'Waiting list sign up'

message = 'Hi ' + person.Title() + ',\nYou have been chosen from the waiting list and signed up for: '
message += signupSheet.Title() + '\n'
message += timeSlot.getLabel()
mailHost = context.MailHost
mailHost.secureSend(message, toEmail, fromEmail, subject)
