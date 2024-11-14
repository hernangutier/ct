odoo.define('ct.migrate.account.invoice.action_button', function (require) {
	"use strict";
	var core = require('web.core');
	var ListController = require('web.ListController');
	var rpc = require('web.rpc');
	var session = require('web.session');
	var _t = core._t;
	ListController.include({
		renderButtons: function ($node) {
			this._super.apply(this, arguments);
			if (this.$buttons) {
				this.$buttons.find('.o_list_migrate_button_create').click(this.proxy('action_def'));
			}
		},
		action_def: function(){
		    var self = this
		    var user = session.uid;
		    rpc.query(
		        {
		        model: 'ct.migrate.account.invoice',
		        method: 'js_python_method',
		        args: [
		            [user], {
		                'user': user
		            }
		        ]
		        }
		    ).then(function (e) {
                self.do_action({
                    name: _t('Migrar'),
                    type: 'ir.actions.act_window',
                    res_model: 'wz.migrate',
                    views: [[false, 'form']],
                    view_mode: 'form',
                    target: 'new',
                });
                window.location
            });
		}
	})
});
odoo.define('ct.migrate.product.template.action_button', function (require) {
	"use strict";
	var core = require('web.core');
	var ListController = require('web.ListController');
	var rpc = require('web.rpc');
	var session = require('web.session');
	var _t = core._t;
	ListController.include({
		renderButtons: function ($node) {
			this._super.apply(this, arguments);
			if (this.$buttons) {
				this.$buttons.find('.o_list_migrate_button_create').click(this.proxy('action_def'));
			}
		},
		action_def: function(){
		    var self = this
		    var user = session.uid;
		    rpc.query(
		        {
		        model: 'ct.migrate.product.template',
		        method: 'updateMaster',
		        args: [

		        ]
		        }
		    ).then(function (e) {
                self.do_action({
                    name: _t('Actualizar'),
                    type: 'ir.actions.act_window',
                    res_model: 'wz.migrate',
                    views: [[false, 'form']],
                    view_mode: 'form',
                    target: 'new',
                });
                window.location
            });
		}
	})
});