from odoo import models, fields

class TodoTask(models.Model):
    _name = 'todo.task'
    _description = 'Todo task'

    name = fields.Char(string='Tên Task', required=True)
    description = fields.Text(string="Mô tả")
    due_date = fields.Date(string='Due Date')
    done = fields.Boolean(string='Đã Hoàn Thành', default=False)