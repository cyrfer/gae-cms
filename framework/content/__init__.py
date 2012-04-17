"""
GAE-Python-CMS: Python-based CMS designed for Google App Engine
Copyright (C) 2012
@author: Imran Somji

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

import os

from google.appengine.ext import db

from framework.subsystems import permission
from framework.subsystems import template
from framework.subsystems import cache

CACHE_KEY_PREPEND = 'CONTENT_'

SCOPE_GLOBAL = 'GLOBAL'
SCOPE_LOCAL = 'LOCAL'

class Content(db.Model):

    scope = db.StringProperty(choices=[SCOPE_GLOBAL, SCOPE_LOCAL])
    section_path = db.StringProperty(default=None)
    namespace = db.StringProperty()
    container_namespace = db.StringProperty(default=None)

    name = 'Base Content'
    author = 'Imran Somji'

    actions = [] # Format: [[action_id, action_string, display_in_outer], ...]
    views = [] # Format: [[view_id, view_string, display_in_outer], ...]

    def __unicode__(self):
        item = get(self.section.path, self.section.path_namespace)
        if not item: raise Exception('NotFound')
        return getattr(self, 'action_%s' % self.section.path_action)(item)

    def init(self, section):
        self.section = section
        return self

    def get_else_create(self, scope, section_path, content_type, namespace, container_namespace=None):
        item = get(section_path, namespace)
        if not item:
            self.__init__(parent=content_key(scope, section_path, content_type, namespace),
                          scope=scope,
                          section_path=section_path if scope != SCOPE_GLOBAL else None,
                          namespace=namespace,
                          container_namespace=container_namespace,
                          )
            self.put()
            item = self
        return item

    def get_manage_links(self, item):
        allowed = []
        for action in self.actions:
            if action[2] and permission.perform_action(item, self.section.path, action[0]):
                allowed.append(action)
        if permission.is_admin(self.section.path) and item.container_namespace:
            pass
        elif len(allowed) == 0:
            return ''
        params = {
                  'section': self.section,
                  'content_type': self.name,
                  'namespace': item.namespace,
                  'container_namespace': item.container_namespace,
                  'can_manage': permission.is_admin(self.section.path),
                  'allowed_actions': allowed,
                  }
        return template.snippet('content-permissions', params)

    def update(self):
        key = self.put()
        cache.delete(CACHE_KEY_PREPEND + self.namespace)
        return key

def get(section_path, namespace):
    item = cache.get(CACHE_KEY_PREPEND + namespace)
    if item: return item
    for content_type in get_all_content_types():
        m = __import__('framework.content.' + content_type, globals(), locals(), [content_type])
        concrete = getattr(m, content_type.title())
        for scope in SCOPE_GLOBAL, SCOPE_LOCAL:
            try:
                item = concrete.gql("WHERE ANCESTOR IS :1 LIMIT 1", content_key(scope, section_path, content_type, namespace))[0]
            except:
                pass
            else:
                cache.set(CACHE_KEY_PREPEND + section_path + '.' + namespace, item)
                return item
    return None

def get_all_content_types():
    content_types = []
    for name in os.listdir('framework/content'):
        if os.path.isdir('framework/content/' + name) and os.path.isfile('framework/content/' + name + '/__init__.py'):
            content_types.append(name)
    return content_types

def content_key(scope, section_path, content_type, namespace):
    if not namespace: raise Exception('namespace is required')
    path = scope.upper() + '.' + namespace
    if scope.upper() != SCOPE_GLOBAL:
        path = section_path + '.' + path
    return db.Key.from_path(content_type.title(), path)