# -*- coding:utf-8 -*-
import logging
import gettext
import os

from flask import request
from flask_restful import Resource

from app.models.General import compose_ret
from app.models.Constants import Constants
from app.models.Pdf import Pdf
from app.models.Logs import Logs
from app.models.Report import Report
from app.models.Setting import Setting
from app.models.File import File
from app.models.Various import Various
from app.security.oauth_routes import require_oauth


class PdfBillList(Resource):
    log = logging.getLogger('log_services')

    @require_oauth()
    def post(self):
        args = request.get_json()

        if 'date_beg' not in args or 'date_end' not in args or 'tpl_file' not in args or 'filename' not in args:
            self.log.error(Logs.fileline() + ' : PdfBillList ERROR args missing')
            return compose_ret('', Constants.cst_content_type_json, 400)

        l_datas = Report.getBillingStatus(args['date_beg'], args['date_end'], 0)

        if not l_datas:
            self.log.error(Logs.fileline() + ' : TRACE list current billing not found')
            return compose_ret('', Constants.cst_content_type_json, 404)

        for data in l_datas:
            for key, value in list(data.items()):
                if data[key] is None:
                    data[key] = ''

        ret = Pdf.getPdfBillList(l_datas, args['date_beg'], args['date_end'], args['tpl_file'], args['filename'])

        if not ret:
            self.log.error(Logs.fileline() + ' : PdfBillList failed')
            return compose_ret('', Constants.cst_content_type_json, 500)

        self.log.info(Logs.fileline() + ' : TRACE PdfBillList')
        return compose_ret('', Constants.cst_content_type_json)


class PdfInvoice(Resource):
    log = logging.getLogger('log_services')

    @require_oauth()
    def get(self, id_rec, template, filename):
        tpl = Setting.getTemplateByFile(template)

        if not tpl:
            self.log.error(Logs.fileline() + ' : PdfInvoice template not found, template=%s', str(template))
            return compose_ret(-1, Constants.cst_content_type_json, 500)

        ret = Pdf.getPdfInvoice(id_rec, template, filename)

        if not ret:
            self.log.error(Logs.fileline() + ' : PdfInvoice failed id_rec=%s', str(id_rec))
            return compose_ret(-1, Constants.cst_content_type_json, 500)

        self.log.info(Logs.fileline() + ' : TRACE PdfInvoice')
        return compose_ret(0, Constants.cst_content_type_json)


class PdfReport(Resource):
    log = logging.getLogger('log_services')

    @require_oauth()
    def get(self, id_rec, template, filename, reedit='N', id_user=0):
        if reedit == 'Y':
            tpl = Setting.getTemplateByFile(template)

            id_tpl = 0

            if tpl:
                id_tpl = tpl['tpl_ser']

            ret = File.insertFileReport(id_owner=id_user,
                                        id_dos=id_rec,
                                        doc_type=257,
                                        id_tpl=id_tpl)

            if ret <= 0:
                self.log.error(Logs.fileline() + ' : PdfReport insertFileReport failed id_rec=%s', str(id_rec))
                return compose_ret('', Constants.cst_content_type_json, 500)

            # Get uuid filename
            fileReport = File.getFileReport(id_rec)

            if fileReport:
                ret = Pdf.getPdfReport(id_rec, template, fileReport['file'], reedit)

                if not ret:
                    ret_del = File.deleteFileReportById(fileReport['id_data'])

                    if not ret_del:
                        self.log.error(Logs.fileline() + ' : PdfReport failed delete id_file=%s', str(fileReport['id_data']))
                    return compose_ret('', Constants.cst_content_type_json, 500)
            else:
                self.log.error(Logs.fileline() + ' : PdfReport failed id_rec=%s', str(id_rec))
                return compose_ret('', Constants.cst_content_type_json, 500)
        else:
            ret = Pdf.getPdfReport(id_rec, template, filename, reedit)

        if not ret:
            self.log.error(Logs.fileline() + ' : PdfReport failed id_rec=%s', str(id_rec))
            return compose_ret('', Constants.cst_content_type_json, 500)

        self.log.info(Logs.fileline() + ' : TRACE PdfReport')
        return compose_ret('', Constants.cst_content_type_json)


class PdfReportGeneric(Resource):
    log = logging.getLogger('log_services')

    @require_oauth()
    def post(self):
        args = request.get_json()

        if 'html' not in args or 'filename' not in args:
            self.log.error(Logs.fileline() + ' : PdfReportGeneric ERROR args missing')
            return compose_ret('', Constants.cst_content_type_json, 400)

        ret = Pdf.getPdfReportGeneric(args['html'], args['filename'])

        if not ret:
            self.log.error(Logs.fileline() + ' : PdfReportGeneric failed')
            return compose_ret('', Constants.cst_content_type_json, 500)

        self.log.info(Logs.fileline() + ' : TRACE PdfReportGeneric')
        return compose_ret('', Constants.cst_content_type_json)


class PdfReportGrouped(Resource):
    log = logging.getLogger('log_services')

    @require_oauth()
    def post(self):
        args = request.get_json()

        if 'l_id_rec_vld' not in args or 'filename' not in args:
            self.log.error(Logs.fileline() + ' : PdfReportGrouped ERROR args missing')
            return compose_ret(-1, Constants.cst_content_type_json, 400)

        ret = Pdf.getPdfReportGrouped(args['filename'], args['l_id_rec_vld'])

        if not ret:
            self.log.error(Logs.fileline() + ' : PdfReportGrouped failed')
            return compose_ret(-1, Constants.cst_content_type_json, 500)

        self.log.info(Logs.fileline() + ' : TRACE PdfReportGrouped')
        return compose_ret(0, Constants.cst_content_type_json)


class PdfReportGlobal(Resource):
    log = logging.getLogger('log_services')

    @require_oauth()
    def post(self):
        args = request.get_json()

        if 'exclu' not in args or 'date_beg' not in args or 'date_end' not in args or 'filename' not in args:
            self.log.error(Logs.fileline() + ' : PdfReportGlobal ERROR args missing')
            return compose_ret(-1, Constants.cst_content_type_json, 400)

        ret = Pdf.getPdfReportGlobal(args['filename'], args['exclu'], args['date_beg'], args['date_end'])

        if ret == 500:
            self.log.error(Logs.fileline() + ' : PdfReportGlobal failed')
            return compose_ret(-1, Constants.cst_content_type_json, 500)
        elif ret == 404:
            self.log.error(Logs.fileline() + ' : PdfReportGlobal failed')
            return compose_ret(0, Constants.cst_content_type_json, 404)
        elif ret == 409:
            self.log.error(Logs.fileline() + ' : PdfReportGlobal failed partially')
            return compose_ret(0, Constants.cst_content_type_json, 409)

        self.log.info(Logs.fileline() + ' : TRACE PdfReportGlobal')
        return compose_ret(0, Constants.cst_content_type_json)


class PdfSticker(Resource):
    log = logging.getLogger('log_services')

    @require_oauth()
    def post(self, template):
        args = request.get_json()

        if 'id' not in args or 'type_id' not in args:
            self.log.error(Logs.fileline() + ' : PdfSticker ERROR args missing')
            return compose_ret(-1, Constants.cst_content_type_json, 400)

        ret = Pdf.getPdfSticker(args['id'], args['type_id'], template)

        if not ret:
            self.log.error(Logs.fileline() + ' : PdfSticker failed id=%s, type_id=%s, template=%s', str(args['id']), args['type_id'], template)
            return compose_ret(-1, Constants.cst_content_type_json, 500)

        self.log.info(Logs.fileline() + ' : TRACE PdfSticker')
        return compose_ret(0, Constants.cst_content_type_json)


class PdfTemplate(Resource):
    log = logging.getLogger('log_services')

    @require_oauth()
    def get(self, id_item):
        tpl = Setting.getTemplate(id_item)

        if not tpl:
            self.log.error(Logs.fileline() + ' : PdfTemplate failed get id_item=%s', str(id_item))
            return compose_ret(-1, Constants.cst_content_type_json, 500)

        if tpl['tpl_type'] == 'RES':
            ret = Pdf.getPdfReport(0, tpl['tpl_file'], 'test_template', 'N')
        elif tpl['tpl_type'] == 'STI':
            ret = Pdf.getPdfSticker(0, 'REC', tpl['tpl_file'])
        elif tpl['tpl_type'] == 'OUT':
            ret = Pdf.getPdfOutsourced(0, tpl['tpl_file'], 'test_template')
        elif tpl['tpl_type'] == 'INV':
            ret = Pdf.getPdfInvoice(0, tpl['tpl_file'], 'test_template')
        else:
            self.log.error(Logs.fileline() + ' : PdfTemplate failed unknow type=%s', str(tpl['tpl_type']))
            return compose_ret(-1, Constants.cst_content_type_json, 500)

        if not ret:
            self.log.error(Logs.fileline() + ' : PdfTemplate print failed id=%s, type_id=%s, template=%s', str(tpl['tpl_ser']), tpl['tpl_type'], tpl['tpl_file'])
            return compose_ret(-1, Constants.cst_content_type_json, 500)

        self.log.info(Logs.fileline() + ' : TRACE PdfTemplate')
        return compose_ret(0, Constants.cst_content_type_json)


class PdfOutsourced(Resource):
    log = logging.getLogger('log_services')

    @require_oauth()
    def get(self, id_rec, template, filename):
        tpl = Setting.getTemplateByFile(template)

        if not tpl:
            self.log.error(Logs.fileline() + ' : PdfOutsourced template not found, template=%s', str(template))
            return compose_ret('', Constants.cst_content_type_json, 500)

        ret = Pdf.getPdfOutsourced(id_rec, template, filename)

        if not ret:
            self.log.error(Logs.fileline() + ' : PdfOutsourced failed id_rec=%s', str(id_rec))
            return compose_ret('', Constants.cst_content_type_json, 500)

        self.log.info(Logs.fileline() + ' : TRACE PdfOutsourced')
        return compose_ret('', Constants.cst_content_type_json)


class PdfReportToday(Resource):
    log = logging.getLogger('log_services')

    @require_oauth()
    def post(self):
        args = request.get_json()

        if 'date_beg' not in args or 'date_end' not in args or 'service_int' not in args or 'filename' not in args:
            self.log.error(Logs.fileline() + ' : PdfReportToday ERROR args missing')
            return compose_ret('', Constants.cst_content_type_json, 400)

        l_data = Report.getTodayList(args['date_beg'], args['date_end'], args['service_int'])

        # if no result to write
        if not l_data:
            return compose_ret('', Constants.cst_content_type_json, 404)

        ret = Pdf.getPdfReportToday(l_data, args['date_beg'], args['date_end'], args['service_int'], args['filename'])

        if not ret:
            self.log.error(Logs.fileline() + ' : PdfReportToday getPdfReportToday failed')
            return compose_ret('', Constants.cst_content_type_json, 500)

        self.log.info(Logs.fileline() + ' : TRACE PdfReportToday')
        return compose_ret('', Constants.cst_content_type_json)


class PdfActivityReport(Resource):
    log = logging.getLogger('log_services')

    @require_oauth()
    def post(self):
        args = request.get_json()

        if ('date_beg' not in args or 'date_end' not in args or 'type_ana' not in args or 'tpl_file' not in args or
           'filename' not in args):
            self.log.error(Logs.fileline() + ' : PdfActivityReport missing args')
            return compose_ret('', Constants.cst_content_type_json, 400)

        date_beg = args['date_beg']
        date_end = args['date_end']
        type_ana = args['type_ana']
        tpl_file = args['tpl_file']
        filename = args['filename']

        stat_type = Report.getActivityType(date_beg, date_end, type_ana)
        if not stat_type:
            self.log.error(Logs.fileline() + ' : stat_type empty')
            stat_type = []

        Various.useLangDB()

        try:
            type_ana_int = int(type_ana)
        except Exception:
            type_ana_int = 0

        family_label = ''
        if type_ana_int > 0:
            dico_row = Various.getDicoById(type_ana_int)
            if dico_row:
                family_label = dico_row['label']

        for row in stat_type:
            ana = row.get('analysis') or ''
            row['analysis'] = _(ana.strip())

        stat_age = Report.getActivityAge(date_beg, date_end, type_ana)
        if not stat_age:
            self.log.error(Logs.fileline() + ' : stat_age empty')
            stat_age = []

        Various.useLangDB()
        for row in stat_age:
            ana = row.get('analysis') or ''
            row['analysis'] = _(ana.strip())

            unit = row.get('unite')
            age  = row.get('age')
            if age is not None:
                if unit == 1034:
                    row['age'] = int(age // 365)
                elif unit == 1035:
                    row['age'] = int(age // 52)
                elif unit == 1036:
                    row['age'] = int(age // 12)

        for row in stat_type:
            for k, v in list(row.items()):
                if v is None:
                    row[k] = ''

        for row in stat_age:
            for k, v in list(row.items()):
                if v is None:
                    row[k] = ''

        ret = Pdf.getPdfActivityReport(stat_type, stat_age, date_beg, date_end, tpl_file, filename, family_label)
        if not ret:
            self.log.error(Logs.fileline() + ' : getPdfActivityReport failed')
            return compose_ret('', Constants.cst_content_type_json, 500)

        self.log.info(Logs.fileline() + ' : PdfActivityReport ok')
        return compose_ret('', Constants.cst_content_type_json)


class PrintByScript(Resource):
    log = logging.getLogger('log_services')

    @require_oauth()
    def post(self, script_name):
        # args = request.get_json()

        # TODO get args for script

        cmd = ('sh ' + Constants.cst_printer + '/' + script_name + ' > ' + Constants.cst_io + 'print.out 2>&1 &')

        self.log.error(Logs.fileline() + ' : PrintByScript cmd=' + cmd)
        ret = os.system(cmd)

        self.log.info(Logs.fileline() + ' : TRACE PrintByScript ret =' + str(ret))
        return compose_ret('', Constants.cst_content_type_json)
