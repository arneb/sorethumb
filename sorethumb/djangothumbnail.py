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

from django.conf import settings
from sorethumb.thumbnail import Thumbnail, RemoteThumbnail, ThumbError

class DjangoSettingsMixIn(object):

    def get_setting(self, name, default=None):
        if hasattr(settings, name):
            return getattr(settings, name)
        return super(DjangoSettingsMixIn, self).get_setting(name, default)

class DjangoThumbnail(DjangoSettingsMixIn, Thumbnail):
    pass

class RemoteDjangoThumbnail(DjangoSettingsMixIn, RemoteThumbnail):
    pass
