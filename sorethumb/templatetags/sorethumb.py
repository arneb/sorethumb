# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2010, 2degrees Limited <willmcgugan+2d@gmail.com>.
# All Rights Reserved.
#
# This file is part of sorethumb,
# which is subject to the provisions of the BSD at
# <http://dev.2degreesnetwork.com/p/2degrees-license.html>. A copy of the
# license should accompany this distribution. THIS SOFTWARE IS PROVIDED "AS IS"
# AND ANY AND ALL EXPRESS OR IMPLIED WARRANTIES ARE DISCLAIMED, INCLUDING, BUT
# NOT LIMITED TO, THE IMPLIED WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST
# INFRINGEMENT, AND FITNESS FOR A PARTICULAR PURPOSE.
#
##############################################################################

try:
    from urlparse import urljoin
except ImportError:
    from urllib.parse import urljoin
import os.path
import logging

from django.conf import settings
from django.template import Library, TemplateSyntaxError

from ..thumbnail import ThumbError
from ..djangothumbnail import DjangoThumbnail


register = Library()
logger = logging.getLogger('django')


@register.filter
def sorethumb(file_field, processor_name):
    """ Returns the url path to a thumbnail for a given thumbnail processor. """

    try:
        processor = DjangoThumbnail.get_processor(processor_name)
    except ThumbError as e:
        raise TemplateSyntaxError(getattr(e, 'message', str(e)))

    # pass urls unchanged to Thumbnail processor
    if str(file_field).startswith('http://') or str(file_field).startswith('https://'):
        image_path = unicode(file_field)
    else:
        image_path = os.path.join(settings.MEDIA_ROOT, str(file_field))

    try:
        path = processor.process(image_path)
        return path
    except IOError:
        logger.exception('failed to process image file: %s' % image_path)
        return ""
