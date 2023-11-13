# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import re

from odoo import api, fields, models, tools
from odoo.exceptions import UserError
from odoo.osv.expression import AND, expression


class RapportConge(models.Model):
    _name = "opsol_zeendoc_core.rapport_conge_graph"
    _description = "Rapport conge Graph"
    _auto = False
    _order = 'code desc'

    id = fields.Integer(string='Id')
    number_of_days = fields.Integer(string='Nombre de jours')
    number_of_allocation = fields.Integer(string='Nombre de jours alloués')
    reste_jour = fields.Integer(string='Nombre de jours restants')
    date_from = fields.Date(string="Date debut")
    date_to = fields.Date(string="Date fin")
    leave_id = fields.Many2one(
        comodel_name='hr.leave',
        string='time off',
    )
    holiday_status_id = fields.Many2one(
        comodel_name='hr.leave.type',
        string='time off',
    )
    employee_id = fields.Many2one(
        comodel_name='hr.employee',
        string='Employee',
    )
    holiday_allocation_id = fields.Many2one(
        comodel_name='hr.leave.allocation',
        string='Allocation',
    )

    @property
    def _table_query(self):
        ''' . '''
        return '%s %s %s' % (self._select(), self._from(), self._group_by())

    def _select(self):
        select_str = """
            SELECT
                rcl.id,
                rcl.date_from,
                rcl.date_to,
                rcl.holiday_id as leave_id,
                l.holiday_status_id,
                l.employee_id,
                l.holiday_allocation_id,
                sum(l.number_of_days) as number_of_days,
                COALESCE(sum(lal.number_of_days), 0) as number_of_allocation,
                COALESCE(sum(lal.number_of_days), 0) - sum(l.number_of_days) as reste_jour
        """
        return select_str

    def _from(self):
        from_str = """
            FROM resource_calendar_leaves rcl
                left join hr_leave l on (rcl.holiday_id=l.id)
                left join hr_employee emp on (l.employee_id=emp.id)
                left join hr_leave_type ltyp on (l.holiday_status_id=ltyp.id)
                left join hr_leave_allocation lal on (l.holiday_allocation_id=lal.id)

            WHERE rcl.resource_id IS not NULL AND rcl.holiday_id IS NOT NULL
        """
        return from_str

    def _group_by(self):
        group_by_str = """
            GROUP BY
               l.holiday_status_id, l.employee_id, rcl.holiday_id, l.holiday_allocation_id, rcl.id, rcl.date_from, rcl.date_to
        """
        return group_by_str
