# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo import SUPERUSER_ID
from odoo.exceptions import UserError


class pos_session(models.Model):
    _inherit = 'pos.session'

    @api.multi
    def get_pos_session(self, session_id):
        """ Display opened Session for logged user with Cash Register balance

        :param session_id: POS Open Session id .

        :return: Array of POS Session records.
        """
        if session_id:
            session = self.browse(int(session_id))
        if session:
            if session.user_id.has_group('point_of_sale.group_pos_manager'):
                admin = 1
            else:
                admin = 0
            pos_session = {"id": session.id,
                           "name": session.name,
                           "user_id": [session.user_id.id,
                                       session.user_id.name],
                           "cash_control": session.cash_control,
                           "state": session.state,
                           "stop_at": session.stop_at,
                           "config_id": [session.config_id.id,
                                         session.config_id.display_name],
                           "start_at": session.start_at,
                           "currency_id": [session.currency_id.id,
                                           session.currency_id.name],
                           "cash_register_balance_end_real": (
                                session.cash_register_balance_end_real),
                           "cash_register_total_entry_encoding": (
                                session.cash_register_total_entry_encoding),
                           "cash_register_difference": (
                                session.cash_register_difference),
                           "cash_register_balance_start": (
                                session.cash_register_balance_start),
                           "cash_register_balance_end": (
                                session.cash_register_balance_end),
                           "is_admin": (admin)
                           }
            return pos_session
        else:
            return

    @api.multi
    def get_cashbox(self, session_id, balance):
        """ Display Set Closing Balance Records for logged session

        :param session_id: POS Open Session id.

        :return: Array of cashbox line.
        """
        session = self.browse(int(session_id))
        session.ensure_one()
        context = dict(session._context)
        balance_type = balance or 'end'
        context['bank_statement_id'] = session.cash_register_id.id
        context['balance'] = balance_type
        context['default_pos_id'] = session.config_id.id
        cashbox_id = None
        if balance_type == 'start':
            cashbox_id = session.cash_register_id.cashbox_start_id.id
        else:
            cashbox_id = session.cash_register_id.cashbox_end_id.id
        cashbox_line = []
        total = 0
        if cashbox_id:
            account_cashbox_line = self.env['account.cashbox.line']
            cashbox = account_cashbox_line.search([
                         ('cashbox_id', '=', cashbox_id)
                      ])
            if cashbox:
                for line in cashbox:
                    subtotal = line.number * line.coin_value
                    total += subtotal
                    cashbox_line.append({"id": line.id,
                                         "number": line.number,
                                         "coin_value": line.coin_value,
                                         "subtotal": subtotal,
                                         "total": total
                                         })
            else:
                cashbox_line.append({"total": total})
        else:
            cashbox_line.append({"total": total})
        return cashbox_line


class AccountBankStmtCashWizard(models.Model):
    """
    Account Bank Statement popup that allows entering cash details.
    """
    _inherit = 'account.bank.statement.cashbox'
    _description = 'Account Bank Statement Cashbox Details'

    description = fields.Char("Description")

    @api.model
    def create(self, vals):
        line = super(AccountBankStmtCashWizard, self).create(vals)
        return line

    @api.multi
    def validate_from_ui(self, session_id, balance, values):
        """ Create , Edit , Delete of Closing Balance Grid

        :param session_id: POS Open Session id .
        :param values: Array records to save

        :return: Array of cashbox line.
        """
        session = self.env['pos.session'].browse(int(session_id))
        bnk_stmt = session.cash_register_id
        if (balance == 'start'):
            self = session.cash_register_id.cashbox_start_id
        else:
            self = session.cash_register_id.cashbox_end_id
        if not self:
            self = self.create({'description': "Created from POS"})
            if self and (balance == 'end'):
                account_bank_statement = session.cash_register_id
                account_bank_statement.write({'cashbox_end_id': self.id})
        for val in values:
            id = val['id']
            number = val['number']
            coin_value = val['coin_value']
            cashbox_line = self.env['account.cashbox.line']
            if id and number and coin_value:  # Add new Row
                cashbox_line = cashbox_line.browse(id)
                cashbox_line.write({'number': number,
                                    'coin_value': coin_value
                                    })
            elif not id and number and coin_value:   # Add new Row
                cashbox_line.create({'number': number,
                                     'coin_value': coin_value,
                                     'cashbox_id': self.id
                                     })
            elif id and not (number and coin_value):  # Delete Exist Row
                cashbox_line = cashbox_line.browse(id)
                cashbox_line.unlink()

        total = 0.0
        for lines in self.cashbox_lines_ids:
            total += lines.subtotal

        if (balance == 'start'):
            #starting balance
            bnk_stmt.write({'balance_start': total,
                            'cashbox_start_id': self.id})
        else:
            # closing balance
            bnk_stmt.write({'balance_end_real': total,
                            'cashbox_end_id': self.id})

            return

    @api.multi
    def validate(self):
        """Raise popup for set closing balance in session POS

        :rtype: dict

        """
        res = super(AccountBankStmtCashWizard, self).validate()
        bnk_stmt_id = (self.env.context.get('bank_statement_id', False) or
                       self.env.context.get('active_id', False))
        bnk_stmt = self.env['account.bank.statement'].browse(bnk_stmt_id)
        if bnk_stmt.pos_session_id.state == 'closing_control':

                return res
        else:
            return res
