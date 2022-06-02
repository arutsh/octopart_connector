/** @odoo-module **/

import core from 'web.core';
import framework from 'web.framework';
import stock_report_generic from 'stock.stock_report_generic';

var QWeb = core.qweb;
var _t = core._t;

var MrpBomReportOctopart = stock_report_generic.extend({
    events: {
        'click .o_mrp_bom_unfoldable': '_onClickUnfold',
        'click .o_mrp_bom_foldable': '_onClickFold',
        'click .o_mrp_bom_action': '_onClickAction',
        'click .o_mrp_show_attachment_action': '_onClickShowAttachment',
        'click .o_mrp_bom_check_availability_all':'_onClickCheckAvail',
    },
    get_html: function() {
        var self = this;
        var d = new Date();
        var args = [
            this.given_context.active_id,
            this.given_context.searchQty || false,
            this.given_context.startDate || false,
            this.given_context.endDate || false,
            this.given_context.searchVariant,
            this.given_context.checkAvail || false,
            this.given_context.auth_supplier || false,
            this.given_context.cat_supplier || false,
            this.given_context.manufacturer || false,
            this.given_context.auth_broker || false,
            this.given_context.unauth_broker || false,

        ];
        return this._rpc({
                model: 'rep_bom_oct_str',
                method: 'get_html',
                args: args,
                context: this.given_context,
            })
            .then(function (result) {
                self.data = result;
                if (! self.given_context.searchVariant) {
                    self.given_context.searchVariant = result.is_variant_applied && Object.keys(result.variants)[0];
                }
                if(self.given_context.checkAvail){
                    self.given_context.checkAvail = false
                    console.log(self.given_context.checkAvail)
                }

            });
    },
    set_html: function() {
        var self = this;
        return this._super().then(function () {
            self.$('.o_content').html(self.data.lines);
            self.renderSearch();
            self.update_cp();
        });
    },
    render_html: function(event, $el, result){
        if (result.indexOf('mrp.document') > 0) {
            if (this.$('.o_mrp_has_attachments').length === 0) {
                var column = $('<th/>', {
                    class: 'o_mrp_has_attachments',
                    title: 'Files attached to the product Attachments',
                    text: 'Attachments',
                });
                this.$('table thead th:last-child').after(column);
            }
        }
        $el.after(result);
        $(event.currentTarget).toggleClass('o_mrp_bom_foldable o_mrp_bom_unfoldable fa-caret-right fa-caret-down');
        this._reload_report_type();
    },
    get_bom: function(event) {
      var self = this;
      var $parent = $(event.currentTarget).closest('tr');
      var activeID = $parent.data('id');
      var productID = $parent.data('product_id');
      var lineID = $parent.data('line');
      var qty = $parent.data('qty');
      var level = $parent.data('level') || 0;
      return this._rpc({
              model: 'rep_bom_oct_str',
              method: 'get_bom',
              args: [
                  activeID,
                  productID,
                  parseFloat(qty),
                  lineID,
                  level + 1,
              ]
          })
          .then(function (result) {
              self.render_html(event, $parent, result);
          });
    },
    get_operations: function(event) {
      var self = this;
      var $parent = $(event.currentTarget).closest('tr');
      var activeID = $parent.data('bom-id');
      var qty = $parent.data('qty');
      var level = $parent.data('level') || 0;
      return this._rpc({
              model: 'rep_bom_oct_str',
              method: 'get_operations',
              args: [
                  activeID,
                  parseFloat(qty),
                  level + 1
              ]
          })
          .then(function (result) {
              self.render_html(event, $parent, result);
          });
    },
    update_cp: function () {
        var status = {
            cp_content: {
                $buttons: this.$buttonPrint,
                $searchview: this.$searchView
            },
        };
        return this.updateControlPanel(status);
    },
    renderSearch: function () {
        this.$buttonPrint = $(QWeb.render('mrp.button', {'is_variant_applied': this.data.is_variant_applied}));
        this.$buttonPrint.find('.o_mrp_bom_print').on('click', this._onClickPrint.bind(this));
        this.$buttonPrint.find('.o_mrp_bom_print_all_variants').on('click', this._onClickPrint.bind(this));
        this.$buttonPrint.find('.o_mrp_bom_print_unfolded').on('click', this._onClickPrint.bind(this));
        this.$buttonPrint.find('.o_mrp_bom_check_availability_all').on('click', this._onClickCheckAvail.bind(this));
        //TODO I beleive JavaScript implementation can be improved: instead of different fields one array maybe can be used.
        //knowladgabel javascript developer can fix it easily
        this.$searchView = $(QWeb.render('mrp.report_bom_search', _.omit(this.data, 'lines')));
        this.$searchView.find('.o_mrp_bom_report_qty').on('change', this._onChangeQty.bind(this)).change();
        this.$searchView.find('.o_mrp_bom_octopart_report_start_date').on('change', this._onChangeStartDate.bind(this)).change();
        this.$searchView.find('.o_mrp_bom_octopart_report_end_date').on('change', this._onChangeEndDate.bind(this)).change();
        this.$searchView.find('.o_mrp_bom_report_variants').on('change', this._onChangeVariants.bind(this)).change();
        this.$searchView.find('.o_mrp_bom_report_type').on('change', this._onChangeType.bind(this));
        this.$searchView.find('.o_mrp_bom_report_auth_supplier').on('change', this._onChangeAuthSupplier.bind(this)).change();
        this.$searchView.find('.o_mrp_bom_report_catalog_supplier').on('change', this._onChangeCatSupplier.bind(this)).change();
        this.$searchView.find('.o_mrp_bom_report_manufacturer').on('change', this._onChangeManufacturer.bind(this)).change();
        this.$searchView.find('.o_mrp_bom_report_auth_broker').on('change', this._onChangeAuthBroker.bind(this)).change();
        this.$searchView.find('.o_mrp_bom_report_unauth_broker').on('change', this._onChangeUnAuthBroker.bind(this)).change();

    },
    _onClickPrint: function (ev) {
        var childBomIDs = _.map(this.$el.find('.o_mrp_bom_foldable').closest('tr'), function (el) {
            return $(el).data('id');
        });
        framework.blockUI();
        var reportname = 'mrp.report_bom_structure?docids=' + this.given_context.active_id +
                         '&report_type=' + this.given_context.report_type +
                         '&quantity=' + (this.given_context.searchQty || 1);
        if (! $(ev.currentTarget).hasClass('o_mrp_bom_print_unfolded')) {
            reportname += '&childs=' + JSON.stringify(childBomIDs);
        }
        if ($(ev.currentTarget).hasClass('o_mrp_bom_print_all_variants')) {
            reportname += '&all_variants=' + 1;
        } else if (this.given_context.searchVariant) {
            reportname += '&variant=' + this.given_context.searchVariant;
        }
        var action = {
            'type': 'ir.actions.report',
            'report_type': 'qweb-pdf',
            'report_name': reportname,
            'report_file': 'mrp.report_bom_structure',
        };
        console.log(reportname);
        console.log(action);
        return this.do_action(action).then(function (){
            framework.unblockUI();
        });
    },

    _onClickCheckAvail: function (ev) {
        //var checkAvail = $(ev.currentTarget).val().trim();
        this.given_context.checkAvail = true;
        console.log("_onChangeCheckAvail")
        console.log(this.given_context.checkAvail)
        this._reload();
    },

    _onChangeAuthSupplier: function (ev) {

        if(ev.currentTarget.checked) {
          console.log("_onChangeAuthSupplier Checked");
          this.given_context.auth_supplier = $(ev.currentTarget).val();
          console.log(this.given_context.auth_supplier);
          this._reload();
        } else {
          console.log("_onChangeAuthSupplier not checked");
          this.given_context.auth_supplier = "";
          console.log(this.given_context.auth_supplier);
          this._reload();
        }
    },

    _onChangeCatSupplier: function (ev) {

        if(ev.currentTarget.checked) {
          console.log("_onChangeCatSupplier Checked");
          this.given_context.cat_supplier = $(ev.currentTarget).val();
          console.log(this.given_context.cat_supplier);
          this._reload();
        } else {
          console.log("_onChangeCatSupplier not checked");
          this.given_context.cat_supplier = "";
          console.log(this.given_context.cat_supplier);
          this._reload();
        }
    },

    _onChangeManufacturer: function (ev) {
        //var checkAvail = $(ev.currentTarget).val().trim();
        //this.given_context._onClickUpdate = true;
        if(ev.currentTarget.checked) {
          console.log("_onChangeManufacturer Checked");
          this.given_context.manufacturer = $(ev.currentTarget).val();
          console.log(this.given_context.manufacturer);
          this._reload();
        } else {
          console.log("_onChangeManufacturer not checked");
          this.given_context.manufacturer = "";
          console.log(this.given_context.manufacturer);
          this._reload();
        }
    },

    _onChangeAuthBroker: function (ev) {
        //var checkAvail = $(ev.currentTarget).val().trim();
        //this.given_context._onClickUpdate = true;
      //  var checkbox = $(ev.currentTarget.checked);
      //  console.log(checkbox)

        if(ev.currentTarget.checked) {
          console.log("_onChangeAuthBroker Checked");
          this.given_context.auth_broker = $(ev.currentTarget).val();
          console.log(this.given_context.auth_broker);
          this._reload();
        } else {
          console.log("_onChangeAuthBroker not checked");
          this.given_context.auth_broker = "";
          console.log(this.given_context.auth_broker);
          this._reload();
        }

    },

    _onChangeUnAuthBroker: function (ev) {
        //var checkAvail = $(ev.currentTarget).val().trim();
        //this.given_context._onClickUpdate = true;

        if(ev.currentTarget.checked) {
          console.log("_onChangeUnAuthBroker Checked");
          this.given_context.unauth_broker = $(ev.currentTarget).val();
          console.log(this.given_context.unauth_broker);
          this._reload();
        } else {
          console.log("_onChangeUnAuthBroker not checked");
          this.given_context.unauth_broker = "";
          console.log(this.given_context.unauth_broker);
          this._reload();
        }
    },


    _onChangeQty: function (ev) {
        var qty = $(ev.currentTarget).val().trim();
        if (qty) {
            this.given_context.searchQty = parseFloat(qty);
            this._reload();
        }
    },
    _onChangeStartDate: function (ev) {
        var start_date = $(ev.currentTarget).val();
        console.log("Start Date")
        console.log(start_date)
        if (start_date) {
            this.given_context.startDate = start_date;
            this._reload();
        }
    },
    _onChangeEndDate: function (ev) {
        var end_date = $(ev.currentTarget).val();
        console.log("End Date")
        console.log(end_date)
        if (end_date) {
            this.given_context.endDate = end_date;
            this._reload();
        }
    },
    _onChangeType: function (ev) {
        var report_type = $("option:selected", $(ev.currentTarget)).data('type');
        this.given_context.report_type = report_type;
        this._reload_report_type();
    },
    _onChangeVariants: function (ev) {
        this.given_context.searchVariant = $(ev.currentTarget).val();
        this._reload();
    },
    _onClickUnfold: function (ev) {
        var redirect_function = $(ev.currentTarget).data('function');
        this[redirect_function](ev);
    },
    _onClickFold: function (ev) {
        this._removeLines($(ev.currentTarget).closest('tr'));
        $(ev.currentTarget).toggleClass('o_mrp_bom_foldable o_mrp_bom_unfoldable fa-caret-right fa-caret-down');
    },
    _onClickAction: function (ev) {
        ev.preventDefault();
        return this.do_action({
            type: 'ir.actions.act_window',
            res_model: $(ev.currentTarget).data('model'),
            res_id: $(ev.currentTarget).data('res-id'),
            context: {
                'active_id': $(ev.currentTarget).data('res-id')
            },
            views: [[false, 'form']],
            target: 'current'
        });
    },
    _onClickShowAttachment: function (ev) {
        ev.preventDefault();
        var ids = $(ev.currentTarget).data('res-id');
        return this.do_action({
            name: _t('Attachments'),
            type: 'ir.actions.act_window',
            res_model: $(ev.currentTarget).data('model'),
            domain: [['id', 'in', ids]],
            views: [[false, 'kanban'], [false, 'list'], [false, 'form']],
            view_mode: 'kanban,list,form',
            target: 'current',
        });
    },
    _reload: function () {
        var self = this;
        return this.get_html().then(function () {
            self.$('.o_content').html(self.data.lines);
            self._reload_report_type();
        });
    },
    _reload_report_type: function () {
        this.$('.o_mrp_bom_cost.o_hidden, .o_mrp_prod_cost.o_hidden').toggleClass('o_hidden');
        if (this.given_context.report_type === 'bom_structure') {
           this.$('.o_mrp_bom_cost, .o_mrp_prod_cost').toggleClass('o_hidden');
        }
    },
    _removeLines: function ($el) {
        var self = this;
        var activeID = $el.data('id');
        _.each(this.$('tr[parent_id='+ activeID +']'), function (parent) {
            var $parent = self.$(parent);
            var $el = self.$('tr[parent_id='+ $parent.data('id') +']');
            if ($el.length) {
                self._removeLines($parent);
            }
            $parent.remove();
        });
    },
});

core.action_registry.add('mrp_bom_report_octopart', MrpBomReportOctopart);
export default MrpBomReportOctopart;
