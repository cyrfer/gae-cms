"""
GAE-Python-CMS: Python-based CMS designed for Google AppEngine
Copyright (C) 2012  Imran Somji

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
from google.appengine.ext.webapp import template
from google.appengine.api import users

from framework.subsystems import permission

import settings

HOME_SECTION = 'home'

class Section(db.Model):
    path = db.StringProperty()
    parent_path = db.StringProperty()
    title = db.StringProperty()
    keywords = db.StringProperty()
    description = db.StringProperty()
    rank = db.IntegerProperty()
    is_private = db.BooleanProperty(default=False)
    
    path_parts = None
    handler = None
    
    def __str__(self):
        if not permission.view_section(self): raise Exception('AccessDenied', self.path)
        path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'theme/templates/Default.html')
        loginout_url = self.path if self.path != HOME_SECTION else '/'
        return template.render(path, {
            'user': users.get_current_user(),
            'is_admin': permission.is_admin(path),
            'logout_url': users.create_logout_url(loginout_url),
            'login_url': users.create_login_url(loginout_url),
            'self': self,
            'classes': 'section' + self.path.replace('/', '-').rstrip('-'),
            'body': self.module() if self.path_parts[1] else '<h2>Under Construction</h2>',
        })
        
    def module(self):
        package = "framework.modules." + self.path_parts[1]
        m = __import__(package, globals(), locals(), [self.path_parts[1]])
        klass = getattr(m, self.path_parts[1])
        return klass(self, self.handler, self.path_parts)

def section_key(path):
    return db.Key.from_path('Section', path)

def get_section(handler, path_parts):
    section = Section.gql("WHERE ANCESTOR IS :1 LIMIT 1", section_key(path_parts[0]))[0]
    section.handler = handler
    section.path_parts = path_parts
    return section

def create_section(path, parent_path, title):
    # TODO: check that path does not already exist
    section = Section(parent=section_key(path), path=path.lower(), parent_path=parent_path.lower(), title=title)
    section.put()
    return section

def update_section(old, path, parent_path, title):
    if old.path != path and path != HOME_SECTION:
        # TODO: check that new path does not already exist
        new = Section(parent=section_key(path), path=path.lower(), parent_path=parent_path.lower(), title=title)
        old.delete()
        new.put()
    else:
        # TODO: check that parent path exists
        old.parent_path = parent_path.lower()
        old.title = title
        old.put()