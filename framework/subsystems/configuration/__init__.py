"""
@org: GAE-CMS.COM
@description: Python-based CMS designed for Google App Engine
@(c): gae-cms.com 2012
@author: Imran Somji
@license: GNU GPL v2

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software Foundation,
Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
"""

from google.appengine.api import files
from google.appengine.ext.blobstore import BlobInfo

from framework.content import content_key
from framework.content.configuration import Configuration, CACHE_KEY

from framework.subsystems import cache

def get_configuration():
    try:
        item = cache.get(CACHE_KEY)
        if not item:
            item = Configuration.gql("").fetch()[0]
            cache.set(CACHE_KEY, item)
        return item
    except:
        item = Configuration(parent=content_key('Configuration', None, 'configuration'),
                             namespace = 'configuration',
                             SITE_HEADER = 'gae-cms',
                             SITE_SUB_HEADER = 'Python-based Content Management System for Google App Engine',
                             )
        item.put()
        cache.set(CACHE_KEY, item)
        return item

def get_robots_txt():
    item = get_configuration()
    return item.ROBOTS_TXT if item.ROBOTS_TXT else ''

def get_favicon_ico():
    item = get_configuration()
    if not item.FAVICON_ICO:
        data = file('framework/content/configuration/assets/images/favicon.ico', 'r').read()
        handle = files.blobstore.create(mime_type='image/x-icon', _blobinfo_uploaded_filename='favicon.ico')
        with files.open(handle, 'a') as f: f.write(data)
        files.finalize(handle)
        item.FAVICON_ICO = files.blobstore.get_blob_key(handle)
        item.update()
        cache.delete(CACHE_KEY)
    raise Exception('SendFileBlob', BlobInfo.get(item.FAVICON_ICO).open().read(), 'image/x-icon')

def default_theme():
    item = get_configuration()
    return item.DEFAULT_THEME

def theme_preview_enabled():
    item = get_configuration()
    return item.ENABLE_THEME_PREVIEW

def debug_mode():
    item = get_configuration()
    return item.DEBUG_MODE