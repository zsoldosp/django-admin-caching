==========================
django-admin-caching
==========================

.. image:: https://travis-ci.org/PaesslerAG/django-admin-caching.svg?branch=master
        :target: https://travis-ci.org/PaesslerAG/django-admin-caching

.. contents:: Django Admin Caching made easy

The Django admin changelist rows are not contained within a block that could be
extended through standard template caching with tags. Also, the generation of the
cache key for more complex objects might be too complicated to do in the templates.
Plus there might be out-of-process changes (e.g.: one of manual data fixes) that
don't change the cache key, but should invalidate the cached row.

Hence the existence of this application - declaratively cache your admin rows!

Setup
=====

* install it via ``pip install django-admin-caching``
* add it to your settings and it auto-registers itself
  ::

      settings.INSTALLED_APPS = [
         ...
         'django_admin_caching',
         ...
      ]
* configure the admins you want cached (see below for detail)

Configuring the admin
=====================

* to enable cahcing, the ``admin_caching_enabled`` attribute of the model's
  admin class must be set to  ``True``. Note this means you might need to
  ``unregister`` the default admin and register your custom one for third 
  party models (e.g.: ``django.contrib.auth.models.Group``)
* the cache key by default is ``<admin class module name>.<admin class name>-
  <model class app label>.<model class name>-<model object pk>``. This could
  be customized by adding a custom key method to the admin class that returns
  the string key for the model object part of the key -
  ``def admin_caching_key(self, obj)``

  * if ``settings.USE_I18N`` (and ``settings.USE_L10N``) are enabled, for each
    enabled setting, a prefix will be added to the above, e.g.:
    ``<language name>.<locale name>.<the key from above>``

* on the admin level, the cache's name can be specified through the
  ``admin_caching_cache_name`` attribute. If omitted, it defaults to ``default``
* on the admin level, the cache's timeout  can be specified through the
  ``admin_caching_timeout_seconds`` attribute. If omitted, it defaults to the
  cache's ``default_tiemout``

Release Notes
=============

* 0.1.2

  * if i18n/l10n is enabled, account for it in the cache prefix

* 0.1.1

  * allow specifying the cache timeout on the admin class

* 0.1.0 - initial release

  * supports Django 1.8, 1.9, 1.10 on python 2.7, 3.3, 3.4, and 3.5
  * supports the following configuration attributes on the admin class

    * ``admin_caching_enabled``
    * ``admin_caching_cache_name``
    * ``admin_caching_key`` for custom object cache key

.. contributing start

Contributing
============

As an open source project, we welcome contributions.

The code lives on `github <https://github.com/PaesslerAG/django-admin-caching>`_.

Reporting issues/improvements
-----------------------------

Please open an `issue on github <https://github.com/PaesslerAG/django-admin-caching/issues/>`_
or provide a `pull request <https://github.com/PaesslerAG/django-admin-caching/pulls/>`_
whether for code or for the documentation.

For non-trivial changes, we kindly ask you to open an issue, as it might be rejected.
However, if the diff of a pull request better illustrates the point, feel free to make
it a pull request anyway.

Pull Requests
-------------

* for code changes

  * it must have tests covering the change. You might be asked to cover missing scenarios
  * the latest ``flake8`` will be run and shouldn't produce any warning
  * if the change is significant enough, documentation has to be provided

Setting up all Python versions
------------------------------

::

    sudo apt-get -y install software-properties-common
    sudo add-apt-repository ppa:fkrull/deadsnakes
    sudo apt-get update
    for version in 3.3 3.5; do
      py=python$version
      sudo apt-get -y install ${py} ${py}-dev
    done

Code of Conduct
---------------

As it is a Django extension, it follows
`Django's own Code of Conduct <https://www.djangoproject.com/conduct/>`_.
As there is no mailing list yet, please just email one of the main authors
(see ``setup.py`` file or `github contributors`_)


.. contributing end


.. _github contributors: https://github.com/PaesslerAG/django-admin-caching/graphs/contributors
