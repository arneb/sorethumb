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

import os.path
from PIL import Image
import hashlib
import socket
try:
    from django.utils import six
except ImportError:
    import six
try:
    from urllib.request import Request, urlopen  # Python 3
except:
    from urllib2 import Request, urlopen  # Python 2

from sorethumb.filters import Filter

class ThumbError(Exception):
    pass


def _camel_to_lower(name):
    """ Converts CamelCase to lower_case_with_underscores """
    return ''.join([c if not c.isupper() else '_'+c.lower()
                    for c in name]).lstrip('_')

class ThumbnailBase(type):

    """ This is a metaclass which extracts a thumbnail declaration and saves
    it in to a global registry. Not to be used directly, see Thumbnail below.

    """

    thumb_processors = {}

    def __new__(cls, name, bases, attrs):

        parents = [b for b in bases if isinstance(b, ThumbnailBase)]
        if not parents:
            return type.__new__(cls, name, bases, attrs)

        if 'name' not in attrs:
            attrs['name'] = _camel_to_lower(name)

        def check_get(name):
            """ Retrieves a value from attrs or throws an error if it does
            not exist. """
            if name not in attrs:
                raise ValueError("'%s' is a required field for Thumbnails" % name)
            return attrs[name]

        thumb_name = check_get('name')
        thumb_version = str(attrs.get('version', '1'))

        # Find all the filters and store them in a list
        # Also store the extra fields in processor_data
        processor_data = {}
        for k, v in six.iteritems(attrs):
            if not k.startswith('__'):
                processor_data[k] = v

        settings = {}
        if 'Settings' in attrs:
            settings = dict([(k, v)
                             for k, v in six.iteritems(attrs['Settings'].__dict__)
                                if not k.startswith('_')])

        filters = attrs.get('filters', [])

        processor_data.update(name = thumb_name,
                              filters = filters)

        processor_class = type.__new__(cls, name, bases, attrs)

        thumb_obj = processor_class(thumb_name, thumb_version, processor_data)

        thumb_obj.settings = settings
        ThumbnailBase.thumb_processors[thumb_name] = thumb_obj

        return processor_class



class Thumbnail(six.with_metaclass(ThumbnailBase, object)):
    """ This class is used to declare how images are turned in to thumbnails.
    It also exposes the basic API to retrieve processors from the global
    registry. Generally though, the 'sorethumb' django tag should be used.

    """

    def get_setting(self, name, default=None):
        if hasattr(self, 'settings'):
            return self.settings.get(name, default)
        return default

    def __init__(self, name, version, processor_data):
        self.name = name
        self.version = version
        self.processor_data = processor_data
        self.default_filters = self.get_setting('SORETHUMB_DEFAULT_FILTERS', [])
        self.filters = self.processor_data['filters']
        self.post_processors = self.processor_data.get('post_processors', [])
        self._dir_name = self._get_dir_name()

    @classmethod
    def get_processor(self, name):
        if name not in ThumbnailBase.thumb_processors:
            raise ThumbError("'%s' is not a registered thumb processor" % name)
        return ThumbnailBase.thumb_processors[name]

    @classmethod
    def render(self, processor_name, image_path):
        processor = self.get_processor(processor_name)
        return processor.process(image_path)


    def _get_dir_name(self):
        """ Gets a string that identifies the sequence of filters. """

        def get_filter_name(filter):
            if hasattr(filter, 'name'):
                return filter.name
            return filter.__class__.__name__

        filter_params = '.'.join([get_filter_name(filter) + ':' + repr(filter.get_params())
                                  for filter in (self.default_filters + self.filters)])
        filter_hash = hashlib.md5(filter_params.encode('utf-8')).hexdigest()[::2]
        name = "%s.%s.v%s" % (self.name, filter_hash, self.version)
        return name

    def get_missing_image(self):
        """Return a substitute image if the given image path does not exist
        or can not be read. May be overriden for different behaviour."""
        img = Image.new("RGB", (100, 100), (255, 0, 255))
        return img

    def process(self, image_path, format=None):
        """ Produces a thumbnail from a given path by running it through each
        registered filter in turn (if the thumbnail doesn't already exist).
        Returns the url path to the the thumbnail.

        """
        def url_join(u1, u2):
            return '/'.join((u1.rstrip('/'), u2.lstrip('/')))

        image_path = image_path or ''
        image_root = self.get_setting('SORETHUMB_IMAGE_ROOT') or ''
        input_name = image_path[len(image_root):].lstrip('/')

        if not input_name or not image_path:
            input_name = "__default"
            default_image = self.get_setting('SORETHUMB_DEFAULT_IMAGE')
            image_path = self.processor_data.get('default', default_image)
            if not image_path.startswith(image_root):
                image_path = os.path.join(image_root, image_path)

        if not image_path:
            raise ThumbError('No path to original, and SORETHUMB_DEFAULT_IMAGE is not set')

        path = self.get_setting('SORETHUMB_OUTPUT_PATH')
        if not path:
            raise ThumbError('SORETHUMB_OUTPUT_PATH is required')

        # Build a destination path from the filter name
        output_dir = os.path.join(path, self._dir_name)
        if format is None:
            format = self.processor_data.get('format', 'jpg')
        ext = '.thumb.' + format.lstrip('.')
        output_path = url_join(output_dir, input_name + ext)


        url_root = self.get_setting('SORETHUMB_URL_ROOT')
        url_path = os.path.join(url_root, url_join(self._dir_name, input_name + ext))

        # If it exists just return the path to the processed image
        if os.path.exists(output_path):
            return url_path

        # Make the destination folder, if it doesn't exist
        try:
            output_dir = os.path.dirname(output_path)
            os.makedirs(output_dir)
        except OSError:
            pass

        try:
            img = Image.open(image_path)
        except (OSError, IOError) as e:
            # If the image doesn't exist, replace it with a pink square
            # This should only occur when the media isn't up to date
            img = self.get_missing_image()
            output_path = url_join(output_dir, '__missing.png')
            url_path = os.path.join(url_root, url_join(self._dir_name, '__missing.png'))

        # Run the image through all registered filters
        for filter in (self.default_filters + self.filters):
            img = filter(img) or img

        # Write the processed image and return the path
        # extra_options ot handle animated gifs
        extra_options = {}
        #extra_options['save_all'] = True
        #extra_options['format'] = 'GIF'
        #output_path += ".gif"
        #extra_options['transparency'] = transparency
        try:
            img.save(output_path,
                     quality = self.processor_data.get('quality', 99),
                     **extra_options)
            # run post processor on generated file
            for processor in self.post_processors:
                processor(output_path)
        except (OSError, IOError) as e:
            # Ultra cautious approach to avoid a 500 error
            # If save fails it will be re-attempted next request
            pass

        return url_path



def _url_to_hash(url):
    ext = url.split('.')[-1]
    url_hash = hashlib.sha1(url).hexdigest()
    return url_hash + '.' + ext


class RemoteThumbnail(Thumbnail):
    """
    This subclass is able to fetch a remote image before producing
    the thumbnail.

    """
    def process(self, image_url, format=None):
        image_root = self.get_setting('SORETHUMB_IMAGE_ROOT') or ''
        remote_root = self.get_setting('SORETHUMB_REMOTE_ROOT')

        if remote_root is None:
            raise Exception("SORETHUMB_REMOTE_ROOT setting is needed to be able to fetch remote images")

        url_hash = _url_to_hash(image_url)
        image_path = os.path.join(image_root, remote_root, url_hash)

        output_dir = os.path.dirname(image_path)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        if not os.path.exists(image_path):
            socket_timeout = socket.getdefaulttimeout()
            socket.setdefaulttimeout(self.get_setting('SORETHUMB_REMOTE_TIMEOUT', 2.5))

            r = Request(image_url)
            r.add_header('User-Agent', self.get_setting('SORETHUMB_USER_AGENT', 'Mozilla/5.0 (Windows NT 5.1; rv:23.0) Gecko/20100101 Firefox/23.0'))
            r.add_header('Accept', self.get_setting('SORETHUMB_ACCEPT_HEADER', 'image/png,image/*;q=0.8,*/*;q=0.5'))
            r.add_header('Referer', self.get_setting('SORETHUMB_REFERER', 'http://www.google.com'))
            try:
                imagecontent = urlopen(r).read()
                open(image_path, "wb").write(imagecontent)
            except:
                image_path = None
            finally:
                socket.setdefaulttimeout(socket_timeout)

        return super(RemoteThumbnail, self).process(image_path, format)
