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

from django.template import Library
import importlib, traceback

from framework.subsystems import permission
import settings

register = Library()

@register.filter
def view_global(section, param_string):
    params = [x.strip() for x in param_string.split(',')]
    mod, view, location_id = params[0:3]
    params = params[3:] if len(params) > 3 else None
    try:
        m = importlib.import_module('framework.content.' + mod)
        contentmod = getattr(m, mod)(section, section.handler, section.path_parts)
        if permission.view_content(contentmod, section, view):
            view = getattr(m, 'view_' + view)
            return view(section, location_id, params)
        else:
            return '<div class="status error">You do not have permission to view this content</div>'
    except Exception as inst:
        error = str(inst) + ('<div class="traceback">' + traceback.format_exc().replace('\n', '<br><br>') + '</div>') if settings.DEBUG else ''
        return '<div class="status error">Error: View does not exist: ' + error + '</div>'