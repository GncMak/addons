###################################################################################
# 
#    Copyright (C) 2017 MuK IT GmbH
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###################################################################################

{
    "name": "MuK QMS Documents Human Resources",
    "summary": """Human Resources Extension""",
    "version": "11.0.1.0.3",
    "category": "Extra Tools",
    "license": "LGPL-3",
    "website": "http://www.mukit.at",
    "live_test_url": "https://demo.mukit.at/web/login",
    "author": "MuK IT",
    "contributors": [
        "Mathias Markl <mathias.markl@mukit.at>",
    ],
    "depends": [
        "hr",
        "muk_utils",
        "muk_hr_utils",
        "muk_quality_docs",
    ],
    "data": [
        "views/groups.xml",
    ],
    "qweb": [
        "static/src/xml/*.xml",
    ],
    "images": [
        'static/description/banner.png'
    ],
    "external_dependencies": {
        "python": [],
        "bin": [],
    },
    "auto_install": True,
    "application": False,
    "installable": True,
}
