import os
import shutil
from io import StringIO

import pytest

from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.core.management import call_command

from django_media_cleaner.code import get_used_media, get_file_fields, get_all_media, get_unused_media
from .models import Post, Product


@pytest.mark.django_db
def test_get_file_fields():
    assert set(get_file_fields()) == {
        Post._meta.get_field('photo'),
        Post._meta.get_field('attachment'),
        Product._meta.get_field('photo'),
    }


@pytest.mark.django_db
def test_get_used_media():
    Post.objects.create(photo='post/1.jpg', attachment='post/1.docx')
    Post.objects.create(photo='post/2.jpg')
    Post.objects.create(attachment='post/3.docx')
    Product.objects.create(photo='product/1.jpg')

    media = get_used_media()
    assert media == {
        os.path.join(settings.MEDIA_ROOT, 'post/1.jpg'),
        os.path.join(settings.MEDIA_ROOT, 'post/1.docx'),
        os.path.join(settings.MEDIA_ROOT, 'post/2.jpg'),
        os.path.join(settings.MEDIA_ROOT, 'post/3.docx'),
        os.path.join(settings.MEDIA_ROOT, 'product/1.jpg'),
    }


@pytest.mark.django_db
def test_get_all_media():
    if os.path.exists(settings.MEDIA_ROOT):
        shutil.rmtree(os.path.join(settings.MEDIA_ROOT))
    os.makedirs(os.path.join(settings.MEDIA_ROOT, 'product'))

    default_storage.save('product/1.jpg', ContentFile(b'111'))
    default_storage.save('product/2.jpg', ContentFile(b'222'))
    default_storage.save('product/3.jpg', ContentFile(b'333'))

    assert get_all_media() == {
        os.path.join(settings.MEDIA_ROOT, 'product/1.jpg'),
        os.path.join(settings.MEDIA_ROOT, 'product/2.jpg'),
        os.path.join(settings.MEDIA_ROOT, 'product/3.jpg'),
    }


@pytest.mark.django_db
def test_get_unused_media():
    if os.path.exists(settings.MEDIA_ROOT):
        shutil.rmtree(os.path.join(settings.MEDIA_ROOT))
    os.makedirs(settings.MEDIA_ROOT)

    default_storage.save('product/1.jpg', ContentFile(b'111'))
    default_storage.save('product/2.jpg', ContentFile(b'222'))
    default_storage.save('product/3.jpg', ContentFile(b'333'))
    default_storage.save('post/1.jpg', ContentFile(b'333'))
    default_storage.save('post/2.jpg', ContentFile(b'333'))

    assert get_unused_media() == {
        os.path.join(settings.MEDIA_ROOT, 'product/1.jpg'),
        os.path.join(settings.MEDIA_ROOT, 'product/2.jpg'),
        os.path.join(settings.MEDIA_ROOT, 'product/3.jpg'),
        os.path.join(settings.MEDIA_ROOT, 'post/1.jpg'),
        os.path.join(settings.MEDIA_ROOT, 'post/2.jpg'),
    }
    
    Product.objects.create(photo='product/1.jpg')
    Product.objects.create(photo='product/3.jpg')
    Post.objects.create(photo='post/2.jpg')

    assert get_unused_media() == {
        os.path.join(settings.MEDIA_ROOT, 'product/2.jpg'),
        os.path.join(settings.MEDIA_ROOT, 'post/1.jpg'),
    }


@pytest.mark.django_db
def test_find_unused_media_command():
    if os.path.exists(settings.MEDIA_ROOT):
        shutil.rmtree(os.path.join(settings.MEDIA_ROOT))
    os.makedirs(settings.MEDIA_ROOT)

    # 1. No media
    with StringIO() as out:
        call_command('find_unused_media', stdout=out)
        assert out.getvalue() == ''

    # 2. Search files
    default_storage.save('product/1.jpg', ContentFile(b'111'))
    default_storage.save('product/2.jpg', ContentFile(b'222'))
    default_storage.save('post/1.jpg', ContentFile(b'333'))

    Product.objects.create(photo='product/1.jpg')

    with StringIO() as out:
        call_command('find_unused_media', stdout=out)
        assert set(out.getvalue().splitlines()) == {
            os.path.join(settings.MEDIA_ROOT, 'product/2.jpg'),
            os.path.join(settings.MEDIA_ROOT, 'post/1.jpg'),
        }

    # 3. Search and remove
    with StringIO() as out:
        call_command('find_unused_media', stdout=out, delete=True)
        assert set(out.getvalue().splitlines()) == {
            os.path.join(settings.MEDIA_ROOT, 'product/2.jpg'),
            os.path.join(settings.MEDIA_ROOT, 'post/1.jpg'),
        }

    assert os.path.exists(os.path.join(settings.MEDIA_ROOT, 'product/1.jpg'))
    assert not os.path.exists(os.path.join(settings.MEDIA_ROOT, 'product/2.jpg'))
    assert not os.path.exists(os.path.join(settings.MEDIA_ROOT, 'post/1.jpg'))
