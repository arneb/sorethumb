Sore Thumb settings
===================

There are a few settings that should be added to Django's settings.py file. Alternatively, they can be set in the thumbnail specification to override settings on a per-thumbnail spec basis.


SORETHUMB_OUTPUT_PATH
---------------------

The absolute system path where the generated thumbnails should be placed, e.g. "/srv/mysite.com/media/sorethumboutput/

SORETHUMB_URL_ROOT
------------------

The URL where the generated thumbnails will be served from, e.g. "/media/sorethumboutput"

SORETHUMB_IMAGE_ROOT
--------------------

The top-level path where the original images will stored, e.g. MEDIA_ROOT. The directory structure underneath this path will be replicated in the thumbnail directory for your thumbnail cass.

SORETHUMB_DEFAULT_IMAGE
-----------------------

A path to the default image, which will be used if the file field is None. The filters will still be applied to this image, and the result cached as usual.

SORETHUMB_REMOTE_ROOT
---------------------

A path relative to SORETHUMB_IMAGE_ROOT, where remote images are stored if the RemoteThumbnail processors are used. Should not start with a slash, e.g. "remote/"

SORETHUMB_REMOTE_TIMEOUT
------------------------

A timeout in seconds to wait for remote images to load. Default: 2.5 seconds.

SORETHUMB_DEFAULT_FILTERS
-------------------------

A list of filters which are prepended to every Thumbnail filters definition.
