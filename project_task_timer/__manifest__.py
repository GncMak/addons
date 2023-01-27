# -*- coding: utf-8 -*-
# Copyright 2020 Konien Ltd.Şti.
{
    'name': "Project Task Timer",
    'summary': """
        Project Task Timer""",
    'author': "Konien Yazılım ve Danışmanlık Ltd. Şti.",
    "website": "https://www.konien.com",
    'category': 'project',
    "version": "11.0.1",
    'depends': ['project'],
    'external_dependencies': {},
    'data': [
        'security/ir.model.access.csv',
        'wizard/project_task_timer_action_wizard_view.xml',
        'views/project_task.xml',
        'views/task_timer.xml',

    ],
    'demo': [],
    'qweb': [],
    'installable': True,
    'application': False,
    'auto_install': False,
}
