try:
    from zope.app.component.hooks import getSite
except ImportError:
    from zope.component.hooks import getSite
from Products.CMFCore.utils import getToolByName
from logging import getLogger

logger = getLogger('uwosh.timeslot')


def parseVocabulary(vocab):
    split = vocab.split(',')
    if len(split) == 0:
        return None

    results = []
    for item in split:
        value = item
        label = item
        if '<' in item and item.endswith('>'):
            itemsplit = item.split('<')
            if len(itemsplit) == 2:
                value = itemsplit[0]
                label = itemsplit[1].strip('>')
        results.append({'value': value, 'label': label})

    return results


def parseField(field):
    split = field.split('|')
    if len(split) < 2 or len(split) > 3:
        return None

    name = split[0]
    label = split[1]

    if len(split) == 2:
        vocabulary = None
    elif len(split) == 3:
        vocabulary = parseVocabulary(split[2])

    return {
        'name': name,
        'label': label,
        'vocabulary': vocabulary
    }


def getAllExtraFields(context=None):
    from uwosh.timeslot.config import DefaultExtraFields
    if context is None:
        context = getSite()
    pprops = getToolByName(context, 'portal_properties')
    site_props = pprops.site_properties

    extra_fields = site_props.getProperty('timeslot_extra_fields', None)
    if not extra_fields:
        extra_fields = DefaultExtraFields

    result = []
    for field in extra_fields:
        try:
            # don't let any parsing errors screw this up.
            result.append(parseField(field))
        except:
            # just log it.
            logger.info("Error parsing the extra field value %s" % field)

    return result
