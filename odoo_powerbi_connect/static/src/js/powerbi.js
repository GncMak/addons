/* Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>) */
/* See LICENSE file for full copyright and licensing details. */
/* License URL : <https://store.webkul.com/license.html/> */

odoo.define('odoo_powerbi_connect.PowerbiReports', function (require) {
    "use strict";
        
    var core = require('web.core');
    var ajax = require("web.ajax");
    var FormRenderer = require("web.FormRenderer");
    var _t = core._t;

    FormRenderer.include({
        _renderView: function () {
            var self = this;
            var res = this._super.apply(this, arguments);
            return res.then(function () {
                self._report = self.$el.find('#powerbi_report_container');
                self._dashboard = self.$el.find('#powerbi_dashboard_container');
                self.powerbi_id = self.$el.find('span[name="powerbi_id"]').text();
                console.log(self.powerbi_id);
                console.log(self._report.length);
                console.log(self._dashboard.length);
                if (self._report.length > 0 && self.powerbi_id) {
                    console.log("embedding report");
                    self.render_powerbi_report();
                }
                else if (self._dashboard.length > 0 && self.powerbi_id) {
                    console.log("embedding dashboard");
                    self.render_powerbi_dashboard();
                }
            })
        },

        render_powerbi_report: function () {
            var container = this._report[0];

            // jsonRpc call for getting Embed Token and Embed Url
            ajax.jsonRpc('/get/reportparameter', 'call', {
                'report_id': this.powerbi_id,
            })
            .then( function(data){
    
                var reportContainer = container;
    
                // Initializing iframe for embedding report
                powerbi.bootstrap(reportContainer, { type: "report" });
    
                var models = window["powerbi-client"].models;
                var reportData = {
                    type: "report",
                    tokenType: models.TokenType.Embed,
        
                    // Enable this setting to remove gray shoulders from embedded report
                    settings: {
                            background: models.BackgroundType.Transparent
                        }
                };
                reportData.accessToken = data.embed_token;
                reportData.embedUrl = data.embed_url;
    
                // Embedding Power BI report using Access token and Embed Url
                var report = powerbi.embed(reportContainer, reportData);
    
                // This will be triggered when a report schema is successfully loaded
                report.on("loaded", function () {
                    console.log("Report successfully loaded.")
                });
    
                // This will be triggered when a report is successfully embedded in UI
                report.on("rendered", function () {
                    console.log("Report successfully rendered.")
                });
    
                // Clear any other error handler event
                report.off("error");
    
                // Printing errors that occur during embedding
                report.on("error", function (event) {
                    var errorMsg = event.detail;
                    console.error(errorMsg);
                    return;
                });
            });
        },

        render_powerbi_dashboard: function() {
            var container = this._dashboard[0];

            // jsonRpc call for getting Embed Token and Embed Url
            ajax.jsonRpc('/get/dashboardparameter', 'call', {
                'dashboard_id': this.powerbi_id,
            })
            .then( function(data){
    
                var dashboardContainer = container;
    
                // Initializing iframe for embedding dashboard
                powerbi.bootstrap(dashboardContainer, { type: "dashboard" });
                        
                var models = window["powerbi-client"].models;
                var dashboardData = {
                    type: "dashboard",
                    tokenType: models.TokenType.Embed,
        
                    // Enable this setting to remove gray shoulders from embedded dashboard
                    settings: {
                        background: models.BackgroundType.Transparent
                    }
                };
                dashboardData.accessToken = data.embed_token;
                dashboardData.embedUrl = data.embed_url;

                // Embedding Power BI dashboard using Access token and Embed URL
                var dashboard = powerbi.embed(dashboardContainer, dashboardData);
    
                // This will be triggered when a dashboard schema is successfully loaded
                dashboard.on("loaded", function () {
                    console.log("Dashboard load successful")
                });
                    
                // This will be triggered when a dashboard is successfully embedded in UI
                dashboard.on("rendered", function () {
                    console.log("Dashboard render successful")
                });
                    
                // Clear any other error handler event
                dashboard.off("error");
                    
                // Printing errors that occur during embedding
                dashboard.on("error", function (event) {
                    var errorMsg = event.detail;
                    console.error(errorMsg);
                    return;
                });
            });
        }

    });

});