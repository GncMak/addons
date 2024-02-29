# Copyright 2021 Sygel - Valentin Vinagre
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)
{
    "name": "Crm Salesperson Planner Task",
    "version": "11.0.1.0.0",
    "development_status": "Beta",
    "category": "Customer Relationship Management",
    "author": "Sygel Technology, Tecnativa, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/crm",
    "license": "AGPL-3",
    "depends": ["crm_salesperson_planner", "project"],
    "data": [
        "views/project_task_views.xml",
        "views/crm_salesperson_planner_visit_views.xml",
    ],
    "installable": True,
}
