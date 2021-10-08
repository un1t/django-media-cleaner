Django Media Cleaner
********************

Searches and removes unused media files.


Installation
------------

1.  Install

.. code-block::

    pip install django-media-cleaner


2.  Add to ``settings.py``

.. code-block:: python

    INSTALLED_APPS = (
        ...
        'django_media_cleaner',
        ...
    )


Usage
-----

To find all unused media files, run command:

.. code-block::

    ./manage.py find_unused_media

To remove them:

.. code-block::

    ./manage.py find_unused_media --delete


How to run tests
----------------

.. code-block::

    python -m venv venv
    source venv/bin/activate
    pip install -r tests/requirements.txt
    pip install -e .
    py.test
