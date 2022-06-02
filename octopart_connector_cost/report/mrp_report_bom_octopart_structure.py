# -*- coding: utf-8 -*-

import json

from odoo import api, fields,models, _
from odoo.tools import float_round
from datetime import date, datetime, time

class ReportBomStructureOctopart(models.AbstractModel):
    _name = 'rep_bom_oct_str'
    _description = 'BOM Structure Report octopart'
    seller_category_ids = fields.Many2many('octopart.parts.vendors.category', string="Category")

    @api.model
    def _get_report_values(self, docids, data=None):
        print("************_get_report_values*****************")
        docs = []
        for bom_id in docids:
            bom = self.env['mrp.bom'].browse(bom_id)
            variant = data.get('variant')
            candidates = variant and self.env['product.product'].browse(variant) or bom.product_id or bom.product_tmpl_id.product_variant_ids
            quantity = float(data.get('quantity', bom.product_qty))
            for product_variant_id in candidates.ids:
                if data and data.get('childs'):
                    doc = self._get_pdf_line(bom_id, product_id=product_variant_id, qty=quantity, child_bom_ids=json.loads(data.get('childs')))
                else:
                    doc = self._get_pdf_line(bom_id, product_id=product_variant_id, qty=quantity, unfolded=True)
                doc['report_type'] = 'pdf'
                doc['report_structure'] = data and data.get('report_type') or 'all'
                docs.append(doc)
            if not candidates:
                if data and data.get('childs'):
                    doc = self._get_pdf_line(bom_id, qty=quantity, child_bom_ids=json.loads(data.get('childs')))
                else:
                    doc = self._get_pdf_line(bom_id, qty=quantity, unfolded=True)
                doc['report_type'] = 'pdf'
                doc['report_structure'] = data and data.get('report_type') or 'all'
                docs.append(doc)
                print({
                    'doc_ids': docids,
                    'doc_model': 'mrp.bom',
                    'docs': docs,
                })
        return {
            'doc_ids': docids,
            'doc_model': 'mrp.bom',
            'docs': docs,
        }

    @api.model
    def get_html(self, bom_id=False,
                       searchQty=1,
                       start_date=date.today(),
                       end_date=date.today(),
                       searchVariant=False,
                       checkAvail=False,
                       auth_supplier = False,
                       cat_supplier = False,
                       manufacturer = False,
                       auth_broker = False,
                       unauth_broker = False):
        print("*******************"),
        print(auth_supplier,cat_supplier,manufacturer,auth_broker,unauth_broker)
        print("**********")
        cat_ids = []
        if (self.env['octopart.parts.vendors.category'].search([('desc','=', auth_supplier)]).id):
            cat_ids.append(self.env['octopart.parts.vendors.category'].search([('desc','=', auth_supplier)]).id)
        if(self.env['octopart.parts.vendors.category'].search([('desc','=', cat_supplier)]).id):
            cat_ids.append(self.env['octopart.parts.vendors.category'].search([('desc','=', cat_supplier)]).id)
        if(self.env['octopart.parts.vendors.category'].search([('desc','=', manufacturer)]).id):
            cat_ids.append(self.env['octopart.parts.vendors.category'].search([('desc','=', manufacturer)]).id)
        if(self.env['octopart.parts.vendors.category'].search([('desc','=', auth_broker)]).id):
            cat_ids.append(self.env['octopart.parts.vendors.category'].search([('desc','=', auth_broker)]).id)
        if(self.env['octopart.parts.vendors.category'].search([('desc','=', unauth_broker)]).id):
            cat_ids.append(self.env['octopart.parts.vendors.category'].search([('desc','=', unauth_broker)]).id)

        print(self.env['octopart.parts.vendors.category'].browse(cat_ids))
        seller_cat_ids =  self.env['octopart.parts.vendors.category'].browse(cat_ids)

        print(seller_cat_ids)
        res = self._get_report_data(bom_id=bom_id, searchQty=searchQty, start_date=start_date, end_date=end_date,
                                    searchVariant=searchVariant, checkAvail=checkAvail, seller_cat_ids=seller_cat_ids)
        res['lines']['report_type'] = 'html'
        res['lines']['report_structure'] = 'all'
        res['lines']['has_attachments'] = res['lines']['attachments'] or any(component['attachments'] for component in res['lines']['components'])
        res['lines'] = self.env.ref('octopart_connector_cost.report_mrp_bom')._render({'data': res['lines']})
        return res

    @api.model
    def get_bom(self, bom_id=False, product_id=False, line_qty=False, line_id=False, level=False):
        lines = self._get_bom(bom_id=bom_id, product_id=product_id, line_qty=line_qty, line_id=line_id, level=level)
        return self.env.ref('octopart_connector_cost.report_mrp_bom_line')._render({'data': lines})

    @api.model
    def get_operations(self, bom_id=False, qty=0, level=0):
        bom = self.env['mrp.bom'].browse(bom_id)
        lines = self._get_operation_line(bom, float_round(qty / bom.product_qty, precision_rounding=1, rounding_method='UP'), level)
        values = {
            'bom_id': bom_id,
            'currency': self.env.company.currency_id,
            'operations': lines,
        }
        return self.env.ref('octopart_connector_cost.report_mrp_operation_line')._render({'data': values})

    @api.model
    def _get_report_data(self, bom_id, searchQty=0, start_date=None, end_date=None, searchVariant=False, checkAvail=False, seller_cat_ids=False):
        lines = {}
        bom = self.env['mrp.bom'].browse(bom_id)
        bom_quantity = searchQty or bom.product_qty or 1
        bom_product_variants = {}
        bom_uom_name = ''

        if bom:
            bom_uom_name = bom.product_uom_id.name

            # Get variants used for search
            if not bom.product_id:
                for variant in bom.product_tmpl_id.product_variant_ids:
                    bom_product_variants[variant.id] = variant.display_name

        lines = self._get_bom(bom_id, product_id=searchVariant, line_qty=bom_quantity, level=1,
                              start_date=start_date, end_date=end_date, searchQty=searchQty, checkAvail=checkAvail,
                              seller_cat_ids=seller_cat_ids)
        return {
            'lines': lines,
            'variants': bom_product_variants,
            'bom_uom_name': bom_uom_name,
            'bom_qty': bom_quantity,
            'is_variant_applied': self.env.user.user_has_groups('product.group_product_variant') and len(bom_product_variants) > 1,
            'is_uom_applied': self.env.user.user_has_groups('uom.group_uom')
        }

    def _get_bom(self, bom_id=False, product_id=False, line_qty=False, line_id=False, level=False, start_date=None, end_date=None,
                    searchQty=0, checkAvail=False, seller_cat_ids=False):
        print("***** _get_bom ****")
        print(seller_cat_ids)
        bom = self.env['mrp.bom'].browse(bom_id)
        company = bom.company_id or self.env.company
        bom_quantity = line_qty
        if line_id:
            current_line = self.env['mrp.bom.line'].browse(int(line_id))
            bom_quantity = current_line.product_uom_id._compute_quantity(line_qty, bom.product_uom_id) or 0
        # Display bom components for current selected product variant
        if product_id:
            product = self.env['product.product'].browse(int(product_id))
        else:
            product = bom.product_id or bom.product_tmpl_id.product_variant_id
        if product:
            print("********if product**")
            print(seller_cat_ids)
            price = product.uom_id._compute_price(product.with_company(company).standard_price, bom.product_uom_id) * bom_quantity
            min_price = product.uom_id._compute_price(product.with_company(company)._compute_min_price_bom(moq_qty=bom_quantity, start_date=start_date, end_date=end_date, seller_category = seller_cat_ids), bom.product_uom_id) * bom_quantity
            #if part is not linked to octopart or Retrieved price is 0, then use odoo system historical price
            #min_price = product.uom_id._compute_price(product.with_company(company).min_price, bom.product_uom_id) * bom_quantity
            #max_price = product.uom_id._compute_price(product.with_company(company).max_price, bom.product_uom_id) * bom_quantity

            max_price = product.uom_id._compute_price(product.with_company(company)._compute_max_price_bom(moq_qty=bom_quantity, start_date=start_date, end_date=end_date, seller_category = seller_cat_ids), bom.product_uom_id) * bom_quantity

            avg_price = product.uom_id._compute_price(product.with_company(company).avg_price, bom.product_uom_id) * bom_quantity

            if max_price is None:
                max_price = price

            if min_price is None:
                min_price = price

            if avg_price is None:
                avg_price = price
            attachments = self.env['mrp.document'].search(['|', '&', ('res_model', '=', 'product.product'),
            ('res_id', '=', product.id), '&', ('res_model', '=', 'product.template'), ('res_id', '=', product.product_tmpl_id.id)])
        else:
            # Use the product template instead of the variant
            price = bom.product_tmpl_id.uom_id._compute_price(bom.product_tmpl_id.with_company(company).standard_price, bom.product_uom_id) * bom_quantity
            print("****compute min priceFROM @@@ BOM Product template****")
            min_price = bom.product_tmpl_id.uom_id._compute_price(bom.product_tmpl_id.with_company(company)._compute_min_price_bom(moq_qty=bom_quantity, start_date=start_date, end_date=end_date, seller_category = seller_cat_ids), bom.product_uom_id) * bom_quantity

            max_price = bom.product_tmpl_id.uom_id._compute_price(bom.product_tmpl_id.with_company(company)._compute_max_price_bom(moq_qty=bom_quantity, start_date=start_date, end_date=end_date, seller_category = seller_cat_ids), bom.product_uom_id) * bom_quantity

            avg_price = bom.product_tmpl_id.uom_id._compute_price(bom.product_tmpl_id.with_company(company).avg_price, bom.product_uom_id) * bom_quantity

            if min_price is None:
                min_price = price
            if max_price is None:
                max_price = price
            if avg_price is None:
                avg_price = price
            attachments = self.env['mrp.document'].search([('res_model', '=', 'product.template'), ('res_id', '=', bom.product_tmpl_id.id)])
        operations = self._get_operation_line(bom, float_round(bom_quantity, precision_rounding=1, rounding_method='UP'), 0)
        lines = {
            'bom': bom,
            'bom_qty': bom_quantity,
            'bom_prod_name': product.display_name,
            'currency': company.currency_id,
            'product': product,
            'code': bom and bom.display_name or '',
            'price': price,
            'min_price': min_price,
            'max_price': max_price,
            'avg_price': avg_price,
            'total': sum([op['total'] for op in operations]),
            'total_min': 0,
            'total_max': 0,
            'total_avg': 0,
            'level': level or 0,
            'operations': operations,
            'operations_cost': sum([op['total'] for op in operations]),
            'attachments': attachments,
            'operations_time': sum([op['duration_expected'] for op in operations])
        }
        components, total, total_min, total_max , total_avg= self._get_bom_lines(bom, bom_quantity, product, line_id, level, start_date=start_date,
                                                                    end_date=end_date, searchQty=searchQty, checkAvail=checkAvail, seller_cat_ids=seller_cat_ids)
        lines['components'] = components
        lines['total'] += total
        lines['total_min'] += total_min
        lines['total_max'] += total_max
        lines['total_avg'] += total_avg
        return lines

    def _get_bom_lines(self, bom, bom_quantity, product, line_id, level, start_date = None, end_date=None,searchQty=0, checkAvail=False, seller_cat_ids=False):
        components = []
        total = 0
        total_min = 0
        total_max = 0
        total_avg = 0
        for line in bom.bom_line_ids:
            #if check availability button has clicked, then, check availablity on octopart, before calculating prices:
            if(checkAvail and line.product_id.octopart_linked):
                line.product_id.check_availability()

            line_quantity = (bom_quantity / (bom.product_qty or 1.0)) * line.product_qty
            if line._skip_bom_line(product):
                continue
            company = bom.company_id or self.env.company
            linked = line.product_id.with_company(company).octopart_linked
            price = line.product_id.uom_id._compute_price(line.product_id.with_company(company).standard_price, line.product_uom_id) * line_quantity
            if(linked):
                min_price = line.product_id.uom_id._compute_price(line.product_id.with_company(company)._compute_min_price_bom(moq_qty=line_quantity, start_date=start_date, end_date=end_date, seller_category = seller_cat_ids), line.product_uom_id) * line_quantity
                max_price = line.product_id.uom_id._compute_price(line.product_id.with_company(company)._compute_max_price_bom(moq_qty=line_quantity, start_date=start_date, end_date=end_date, seller_category = seller_cat_ids), line.product_uom_id) * line_quantity
                avg_price = line.product_id.uom_id._compute_price(line.product_id.with_company(company).avg_price, line.product_uom_id) * line_quantity
            else:
                min_price = price
                max_price = price
                avg_price = price

            #max_price = line.product_id.uom_id._compute_price(line.product_id.with_company(company).max_price, line.product_uom_id) * line_quantity

            # if min_price is None:
            #     min_price = price
            #
            # if max_price is None:
            #     max_price = price
            #
            # if avg_price is None:
            #     avg_price = price

            if line.child_bom_id:
                factor = line.product_uom_id._compute_quantity(line_quantity, line.child_bom_id.product_uom_id)
                sub_total = self._get_price(line.child_bom_id, factor, line.product_id)
                sub_total_min = self._get_price_min(line.child_bom_id, factor, line.product_id)
                sub_total_max = self._get_price_max(line.child_bom_id, factor, line.product_id)
                sub_total_avg = self._get_price_avg(line.child_bom_id, factor, line.product_id)
            else:
                sub_total = price
                sub_total_min = min_price
                sub_total_max = max_price
                sub_total_avg = avg_price
            sub_total = self.env.company.currency_id.round(sub_total)
            sub_total_min = self.env.company.currency_id.round(sub_total_min)
            sub_total_max = self.env.company.currency_id.round(sub_total_max)
            sub_total_avg = self.env.company.currency_id.round(sub_total_avg)
            components.append({
                'linked' : linked,
                'prod_id': line.product_id.id,
                'prod_name': line.product_id.display_name,
                'code': line.child_bom_id and line.child_bom_id.display_name or '',
                'prod_qty': line_quantity,
                'prod_uom': line.product_uom_id.name,
                'prod_cost': company.currency_id.round(price),
                'min_prod_cost': company.currency_id.round(min_price),
                'max_prod_cost': company.currency_id.round(max_price),
                'avg_prod_cost': company.currency_id.round(avg_price),
                'parent_id': bom.id,
                'line_id': line.id,
                'level': level or 0,
                'total': sub_total,
                'total_min': sub_total_min,
                'total_max': sub_total_max,
                'total_avg': sub_total_avg,
                'child_bom': line.child_bom_id.id,
                'phantom_bom': line.child_bom_id and line.child_bom_id.type == 'phantom' or False,
                'attachments': self.env['mrp.document'].search(['|', '&',
                    ('res_model', '=', 'product.product'), ('res_id', '=', line.product_id.id), '&', ('res_model', '=', 'product.template'), ('res_id', '=', line.product_id.product_tmpl_id.id)]),

            })
            total += sub_total
            total_min += sub_total_min
            total_max += sub_total_max
            total_avg += sub_total_avg
        return components, total, total_min, total_max, total_avg

    def _get_operation_line(self, bom, qty, level):
        operations = []
        total = 0.0
        qty = bom.product_uom_id._compute_quantity(qty, bom.product_tmpl_id.uom_id)
        for operation in bom.operation_ids:
            operation_cycle = float_round(qty / operation.workcenter_id.capacity, precision_rounding=1, rounding_method='UP')
            duration_expected = operation_cycle * (operation.time_cycle + (operation.workcenter_id.time_stop + operation.workcenter_id.time_start))
            total = ((duration_expected / 60.0) * operation.workcenter_id.costs_hour)
            operations.append({
                'level': level or 0,
                'operation': operation,
                'name': operation.name + ' - ' + operation.workcenter_id.name,
                'duration_expected': duration_expected,
                'total': self.env.company.currency_id.round(total),
            })
        return operations

    def _get_price(self, bom, factor, product):
        price = 0
        if bom.operation_ids:
            # routing are defined on a BoM and don't have a concept of quantity.
            # It means that the operation time are defined for the quantity on
            # the BoM (the user produces a batch of products). E.g the user
            # product a batch of 10 units with a 5 minutes operation, the time
            # will be the 5 for a quantity between 1-10, then doubled for
            # 11-20,...
            operation_cycle = float_round(factor, precision_rounding=1, rounding_method='UP')
            operations = self._get_operation_line(bom, operation_cycle, 0)
            price += sum([op['total'] for op in operations])

        for line in bom.bom_line_ids:
            if line._skip_bom_line(product):
                continue
            if line.child_bom_id:
                qty = line.product_uom_id._compute_quantity(line.product_qty * (factor / bom.product_qty) , line.child_bom_id.product_uom_id) / line.child_bom_id.product_qty
                sub_price = self._get_price(line.child_bom_id, qty, line.product_id)
                price += sub_price
            else:
                prod_qty = line.product_qty * factor / bom.product_qty
                company = bom.company_id or self.env.company
                not_rounded_price = line.product_id.uom_id._compute_price(line.product_id.with_context(force_comany=company.id).standard_price, line.product_uom_id) * prod_qty
                not_rounded_price_min = line.product_id.uom_id._compute_price(line.product_id.with_context(force_comany=company.id).min_price, line.product_uom_id) * prod_qty
                price += company.currency_id.round(not_rounded_price)
                min_price +=company.currency_id.round(not_rounded_price_min)
        return price

    def _get_price_min(self, bom, factor, product):
        price = 0
        if bom.operation_ids:
            # routing are defined on a BoM and don't have a concept of quantity.
            # It means that the operation time are defined for the quantity on
            # the BoM (the user produces a batch of products). E.g the user
            # product a batch of 10 units with a 5 minutes operation, the time
            # will be the 5 for a quantity between 1-10, then doubled for
            # 11-20,...
            operation_cycle = float_round(factor, precision_rounding=1, rounding_method='UP')
            operations = self._get_operation_line(bom, operation_cycle, 0)
            price += sum([op['total_min'] for op in operations])

        for line in bom.bom_line_ids:
            if line._skip_bom_line(product):
                continue
            if line.child_bom_id:
                qty = line.product_uom_id._compute_quantity(line.product_qty * (factor / bom.product_qty) , line.child_bom_id.product_uom_id) / line.child_bom_id.product_qty
                sub_price = self._get_price_min(line.child_bom_id, qty, line.product_id)
                price += sub_price
            else:
                prod_qty = line.product_qty * factor / bom.product_qty
                company = bom.company_id or self.env.company
                not_rounded_price =  line.product_id.uom_id._compute_price(line.product_id.with_context(force_comany=company.id).min_price, line.product_uom_id) * prod_qty

        return price

    def _get_price_max(self, bom, factor, product):
        price = 0
        if bom.operation_ids:
            # routing are defined on a BoM and don't have a concept of quantity.
            # It means that the operation time are defined for the quantity on
            # the BoM (the user produces a batch of products). E.g the user
            # product a batch of 10 units with a 5 minutes operation, the time
            # will be the 5 for a quantity between 1-10, then doubled for
            # 11-20,...
            operation_cycle = float_round(factor, precision_rounding=1, rounding_method='UP')
            operations = self._get_operation_line(bom, operation_cycle, 0)
            price += sum([op['total_max'] for op in operations])

        for line in bom.bom_line_ids:
            if line._skip_bom_line(product):
                continue
            if line.child_bom_id:
                qty = line.product_uom_id._compute_quantity(line.product_qty * (factor / bom.product_qty) , line.child_bom_id.product_uom_id) / line.child_bom_id.product_qty
                sub_price = self._get_price_max(line.child_bom_id, qty, line.product_id)
                price += sub_price
            else:
                prod_qty = line.product_qty * factor / bom.product_qty
                company = bom.company_id or self.env.company
                not_rounded_price =  line.product_id.uom_id._compute_price(line.product_id.with_context(force_comany=company.id).max_price, line.product_uom_id) * prod_qty

        return price


    def _get_price_avg(self, bom, factor, product):
        price = 0
        if bom.operation_ids:
            # routing are defined on a BoM and don't have a concept of quantity.
            # It means that the operation time are defined for the quantity on
            # the BoM (the user produces a batch of products). E.g the user
            # product a batch of 10 units with a 5 minutes operation, the time
            # will be the 5 for a quantity between 1-10, then doubled for
            # 11-20,...
            operation_cycle = float_round(factor, precision_rounding=1, rounding_method='UP')
            operations = self._get_operation_line(bom, operation_cycle, 0)
            price += sum([op['total_avg'] for op in operations])

        for line in bom.bom_line_ids:
            if line._skip_bom_line(product):
                continue
            if line.child_bom_id:
                qty = line.product_uom_id._compute_quantity(line.product_qty * (factor / bom.product_qty) , line.child_bom_id.product_uom_id) / line.child_bom_id.product_qty
                sub_price = self._get_price_max(line.child_bom_id, qty, line.product_id)
                price += sub_price
            else:
                prod_qty = line.product_qty * factor / bom.product_qty
                company = bom.company_id or self.env.company
                not_rounded_price =  line.product_id.uom_id._compute_price(line.product_id.with_context(force_comany=company.id).avg_price, line.product_uom_id) * prod_qty

        return price
    def _get_pdf_line(self, bom_id, product_id=False, qty=1, child_bom_ids=[], unfolded=False):

        def get_sub_lines(bom, product_id, line_qty, line_id, level):
            data = self._get_bom(bom_id=bom.id, product_id=product_id, line_qty=line_qty, line_id=line_id, level=level)
            bom_lines = data['components']
            lines = []
            for bom_line in bom_lines:
                lines.append({
                    'name': bom_line['prod_name'],
                    'type': 'bom',
                    'quantity': bom_line['prod_qty'],
                    'uom': bom_line['prod_uom'],
                    'prod_cost': bom_line['prod_cost'],
                    'bom_cost': bom_line['total'],
                    'level': bom_line['level'],
                    'code': bom_line['code'],
                    'child_bom': bom_line['child_bom'],
                    'prod_id': bom_line['prod_id']
                })
                if bom_line['child_bom'] and (unfolded or bom_line['child_bom'] in child_bom_ids):
                    line = self.env['mrp.bom.line'].browse(bom_line['line_id'])
                    lines += (get_sub_lines(line.child_bom_id, line.product_id.id, bom_line['prod_qty'], line, level + 1))
            if data['operations']:
                lines.append({
                    'name': _('Operations'),
                    'type': 'operation',
                    'quantity': data['operations_time'],
                    'uom': _('minutes'),
                    'bom_cost': data['operations_cost'],
                    'level': level,
                })
                for operation in data['operations']:
                    if unfolded or 'operation-' + str(bom.id) in child_bom_ids:
                        lines.append({
                            'name': operation['name'],
                            'type': 'operation',
                            'quantity': operation['duration_expected'],
                            'uom': _('minutes'),
                            'bom_cost': operation['total'],
                            'level': level + 1,
                        })
            return lines

        bom = self.env['mrp.bom'].browse(bom_id)
        product_id = product_id or bom.product_id.id or bom.product_tmpl_id.product_variant_id.id
        data = self._get_bom(bom_id=bom_id, product_id=product_id, line_qty=qty)
        pdf_lines = get_sub_lines(bom, product_id, qty, False, 1)
        data['components'] = []
        data['lines'] = pdf_lines
        return data
