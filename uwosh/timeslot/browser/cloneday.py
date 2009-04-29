from zope import interface, schema
from zope.formlib import form
from Products.CMFCore import utils as cmfutils
from Products.Five.browser import pagetemplatefile
from Products.Five.formlib import formbase

from zExceptions import BadRequest

from DateTime import DateTime
from datetime import timedelta

# Begin ugly hack. It works around a ContentProviderLookupError: plone.htmlhead error caused by Zope 2 permissions.
#
# Source: http://athenageek.wordpress.com/2008/01/08/contentproviderlookuperror-plonehtmlhead/
# Bug report: https://bugs.launchpad.net/zope2/+bug/176566
#

from Products.Five.browser.pagetemplatefile import ZopeTwoPageTemplateFile

import math

def _getContext(self):
    self = self.aq_parent
    while getattr(self, '_is_wrapperish', None):
        self = self.aq_parent
    return self    
            
ZopeTwoPageTemplateFile._getContext = _getContext

# End ugly hack.

class ICloneDay(interface.Interface):
    numToCreate = schema.Int(title=u'Number to Create', description=u'The number of clones to create', required=True)
    includeWeekends = schema.Bool(title=u'Include Weekends', description=u'Do you want to include weekends?')
    
class CloneDayForm(formbase.PageForm):
    form_fields = form.FormFields(ICloneDay)
    result_template = pagetemplatefile.ZopeTwoPageTemplateFile('cloneday-results.pt')
    success = True
    errors = []

    @form.action('Clone')
    def action_clone(self, action, data):
        self.success = True
        self.errors = []
        
        numToCreate = data['numToCreate']
        numCreated = 0
        includeWeekends = data['includeWeekends']
        
        day = self.context
        signupSheet = day.aq_inner.aq_parent 
        origDate = day.getDate()
        
        dayContentsCopy = day.manage_copyObjects(day.objectIds())
        
        for i in range(1, numToCreate + (2 * int(math.ceil(numToCreate / 7)))):
            newDate = origDate + i
            
            if (includeWeekends) or (newDate.aDay() != 'Sat' and newDate.aDay() != 'Sun'):
                newTitle = newDate.strftime('%B %d, %Y')
                newId = newDate.strftime('%B-%d-%Y').lower()
                
                try:
                    signupSheet.invokeFactory(id=newId, type_name='Day', date=newDate)
                except BadRequest:
                    self.success = False
                    self.errors.append("Operation failed because there is already an object with id: %s" % newId)
                    break
                    
                newDay = signupSheet[newId]
                newDay.setTitle(newTitle)
                newDay.manage_pasteObjects(dayContentsCopy)
                
                if i == 1:
                    newDay.removeAllPeople()
                    dayContentsCopy = newDay.manage_copyObjects(newDay.objectIds())
                    
                newDay.reindexObject()     
                
                numCreated += 1
                if not numCreated < numToCreate:
                    break
            
        return self.result_template()
        
