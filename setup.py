from distutils.core import setup

from sorethumb import __version__ as VERSION

classifiers = ["Framework :: Django",
               "Intended Audience :: Developers",
               "License :: OSI Approved :: BSD License",
               "Programming Language :: Python",
               "Topic :: Software Development :: Libraries :: Python Modules",
               ]

setup(
      name = 'sorethumb',
      packages = ['sorethumb',
                  'sorethumb.templatetags',
                  'sorethumb.filters'],
      version = VERSION,
      description = 'Thumbnail image processing, with Django integration',
      author = 'Will McGugan',
      author_email = "will@willmcgugan.com",
      url = 'https://bitbucket.org/_arne/sorethumb/',
      download_url = 'https://bitbucket.org/_arne/sorethumb/downloads',
      classifiers = classifiers,
      maintainer = "Arne Brodowski",
      maintainer_email = "arne@rcs4u.de"
)
