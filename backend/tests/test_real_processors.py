import io
import os
import zipfile
import pytest
from backend.app.processors import proc_image_metadata, proc_zip_list, proc_email_parse


def test_zip_list(tmp_path):
    zpath = tmp_path / 'a.zip'
    with zipfile.ZipFile(zpath, 'w') as z:
        z.writestr('file1.txt', 'hello')
        z.writestr('dir/file2.txt', 'world')
    res = proc_zip_list(str(zpath))
    assert 'files' in res
    assert 'file1.txt' in res['files']


def test_email_parse(tmp_path):
    eml = tmp_path / 'm.eml'
    eml.write_bytes(b"From: a@example.com\r\nTo: b@example.com\r\nSubject: hi\r\n\r\nHello world")
    res = proc_email_parse(str(eml))
    assert res.get('subject') == 'hi'
    assert 'Hello world' in (res.get('body') or '')


def test_image_metadata(tmp_path):
    pytest.importorskip('PIL')
    from PIL import Image
    p = tmp_path / 'img.png'
    img = Image.new('RGB', (100, 50), color='red')
    img.save(p)
    res = proc_image_metadata(str(p))
    assert res.get('format') in ('PNG', 'JPEG')
    assert res.get('size') == (100, 50)