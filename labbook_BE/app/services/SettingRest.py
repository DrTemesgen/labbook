# -*- coding:utf-8 -*-
import logging
import os
import gettext
import subprocess
import csv
import re

from datetime import datetime
from flask import request, session
from flask_restful import Resource

from app.models.General import compose_ret
from app.models.Constants import Constants
from app.models.Logs import Logs
from app.models.Quality import Quality
from app.models.Setting import Setting
from app.models.Various import Various


class SettingAgeInterval(Resource):
    log = logging.getLogger('log_services')

    def get(self):
        l_datas = Setting.getAgeInterval()

        if not l_datas:
            self.log.error(Logs.fileline() + ' : ' + 'SettingAgeInterval ERROR not found')
            return compose_ret('', Constants.cst_content_type_json, 404)

        for data in l_datas:
            # Replace None by empty string
            for key, value in list(data.items()):
                if data[key] is None:
                    data[key] = ''

        self.log.info(Logs.fileline() + ' : SettingAgeInterval')
        return compose_ret(l_datas, Constants.cst_content_type_json, 200)

    def post(self):
        args = request.get_json()

        if 'list_val' not in args:
            self.log.error(Logs.fileline() + ' : SettingAgeInterval ERROR args missing')
            return compose_ret('', Constants.cst_content_type_json, 400)

        l_interval = Setting.getAgeInterval()

        if not l_interval:
            self.log.info(Logs.fileline() + ' : TRACE SettingAgeInterval ERROR notfound age interval')
            return compose_ret('', Constants.cst_content_type_json, 500)

        for val in args['list_val']:
            lower = val['ais_lower_bound']
            upper = val['ais_upper_bound']

            if lower < 0:
                lower = None

            if upper < 0:
                upper = None

            if val['ais_ser'] > 0:
                ret = Setting.updateAgeInterval(ais_ser=val['ais_ser'],
                                                ais_rank=val['ais_rank'],
                                                ais_lower_bound=lower,
                                                ais_upper_bound=upper)
            else:
                ret = Setting.insertAgeInterval(ais_rank=val['ais_rank'],
                                                ais_lower_bound=lower,
                                                ais_upper_bound=upper)

            if ret is False or ret <= 0:
                self.log.info(Logs.fileline() + ' : TRACE SettingAgeInterval ERROR update val age interval')
                return compose_ret('', Constants.cst_content_type_json, 500)

        # delete missing values compared to age interval
        for db_val in l_interval:
            exist = False
            for ihm_val in args['list_val']:
                if db_val['ais_ser'] == ihm_val['ais_ser']:
                    exist = True

            if not exist:
                ret = Setting.deleteAgeInterval(db_val['ais_ser'])

                if ret is False:
                    self.log.info(Logs.fileline() + ' : TRACE SettingAgeInterval ERROR delete val age interval')
                    return compose_ret('', Constants.cst_content_type_json, 500)

        self.log.info(Logs.fileline() + ' : TRACE SettingAgeInterval')
        return compose_ret('', Constants.cst_content_type_json)


class SettingReqServices(Resource):
    log = logging.getLogger('log_services')

    def get(self):
        l_datas = Setting.getReqServices()

        if not l_datas:
            self.log.error(Logs.fileline() + ' : ' + 'SettingReqServices ERROR not found')
            return compose_ret('', Constants.cst_content_type_json, 404)

        for data in l_datas:
            # Replace None by empty string
            for key, value in list(data.items()):
                if data[key] is None:
                    data[key] = ''

        self.log.info(Logs.fileline() + ' : SettingReqServices')
        return compose_ret(l_datas, Constants.cst_content_type_json, 200)

    def post(self):
        args = request.get_json()

        if 'list_val' not in args:
            self.log.error(Logs.fileline() + ' : SettingReqServices ERROR args missing')
            return compose_ret('', Constants.cst_content_type_json, 400)

        l_req_services = Setting.getReqServices()

        for val in args['list_val']:
            name = val['rqs_name']

            if val['rqs_ser'] > 0:
                ret = Setting.updateReqServices(rqs_ser=val['rqs_ser'],
                                                rqs_rank=val['rqs_rank'],
                                                rqs_name=name)
            else:
                ret = Setting.insertReqServices(rqs_rank=val['rqs_rank'],
                                                rqs_name=name)

            if ret is False or ret <= 0:
                self.log.info(Logs.fileline() + ' : TRACE SettingReqServices ERROR updateReqServices')
                return compose_ret('', Constants.cst_content_type_json, 500)

        # delete missing values compared to age interval
        for db_val in l_req_services:
            exist = False
            for ihm_val in args['list_val']:
                if db_val['rqs_ser'] == ihm_val['rqs_ser']:
                    exist = True

            if not exist:
                ret = Setting.deleteReqServices(db_val['rqs_ser'])

                if ret is False:
                    self.log.info(Logs.fileline() + ' : TRACE SettingReqServices ERROR deleteReqServices')
                    return compose_ret('', Constants.cst_content_type_json, 500)

        self.log.info(Logs.fileline() + ' : TRACE SettingReqServices')
        return compose_ret('', Constants.cst_content_type_json)


class SettingFuncUnitDet(Resource):
    log = logging.getLogger('log_services')

    def get(self, id_unit):
        func_unit = Setting.getFuncUnitDet(id_unit)

        if not func_unit:
            self.log.error(Logs.fileline() + ' : ' + 'SettingFuncUnit ERROR not found')
            return compose_ret('', Constants.cst_content_type_json, 404)

        # Replace None by empty string
        for key, value in list(func_unit.items()):
            if func_unit[key] is None:
                func_unit[key] = ''

        self.log.info(Logs.fileline() + ' : SettingFuncUnitDet')
        return compose_ret(func_unit, Constants.cst_content_type_json, 200)


class SettingFuncUnit(Resource):
    log = logging.getLogger('log_services')

    def get(self):
        l_datas = Setting.getFuncUnit()

        if not l_datas:
            self.log.error(Logs.fileline() + ' : ' + 'SettingFuncUnit ERROR not found')
            return compose_ret('', Constants.cst_content_type_json, 404)

        for data in l_datas:
            # Replace None by empty string
            for key, value in list(data.items()):
                if data[key] is None:
                    data[key] = ''

                data['nb_user'] = 0
                data['nb_fam']  = 0

                nb_user = Setting.getNbFuncUnitLink(data['fun_ser'], 'U')

                if nb_user:
                    data['nb_user'] = nb_user['nb_link']

                nb_fam = Setting.getNbFuncUnitLink(data['fun_ser'], 'F')

                if nb_fam:
                    data['nb_fam'] = nb_fam['nb_link']

        self.log.info(Logs.fileline() + ' : SettingFuncUnit l_datas=' + str(l_datas))
        self.log.info(Logs.fileline() + ' : SettingFuncUnit')
        return compose_ret(l_datas, Constants.cst_content_type_json, 200)

    def post(self):
        args = request.get_json()

        if 'list_val' not in args:
            self.log.error(Logs.fileline() + ' : SettingFuncUnit ERROR args missing')
            return compose_ret('', Constants.cst_content_type_json, 400)

        l_req_services = Setting.getFuncUnit()

        for val in args['list_val']:
            name = val['fun_name']

            if val['fun_ser'] > 0:
                ret = Setting.updateFuncUnit(fun_ser=val['fun_ser'],
                                             fun_rank=val['fun_rank'],
                                             fun_name=name)
            else:
                ret = Setting.insertFuncUnit(fun_rank=val['fun_rank'],
                                             fun_name=name)

            if ret is False or ret <= 0:
                self.log.info(Logs.fileline() + ' : TRACE SettingFuncUnit ERROR updateFuncUnit')
                return compose_ret('', Constants.cst_content_type_json, 500)

        # delete missing values compared to age interval
        for db_val in l_req_services:
            exist = False
            for ihm_val in args['list_val']:
                if db_val['fun_ser'] == ihm_val['fun_ser']:
                    exist = True

            if not exist:
                ret = Setting.deleteFuncUnit(db_val['fun_ser'])

                if ret is False:
                    self.log.info(Logs.fileline() + ' : TRACE SettingFuncUnit ERROR deleteFuncUnit')
                    return compose_ret('', Constants.cst_content_type_json, 500)

        self.log.info(Logs.fileline() + ' : TRACE SettingFuncUnit')
        return compose_ret('', Constants.cst_content_type_json)

    def delete(self):
        args = request.get_json()

        if 'id_unit' not in args:
            self.log.error(Logs.fileline() + ' : SettingFuncUnit ERROR args missing')
            return compose_ret('', Constants.cst_content_type_json, 400)

        ret = Setting.deleteFuncUnit(args['id_unit'])

        if not ret:
            self.log.error(Logs.fileline() + ' : TRACE SettingFuncUnit delete ERROR')
            return compose_ret('', Constants.cst_content_type_json, 500)

        self.log.info(Logs.fileline() + ' : TRACE SettingFuncUnit delete id_item=' + str(args['id_unit']))
        return compose_ret('', Constants.cst_content_type_json)


class SettingLinkUnit(Resource):
    log = logging.getLogger('log_services')

    def get(self, type, id_unit):
        l_datas = Setting.getLinkUnit(type, id_unit)

        if not l_datas:
            self.log.error(Logs.fileline() + ' : ' + 'SettingLinkUnit ERROR not found')
            return compose_ret('', Constants.cst_content_type_json, 404)

        Various.useLangDB()

        for data in l_datas:
            # Replace None by empty string
            for key, value in list(data.items()):
                if data[key] is None:
                    data[key] = ''
                elif key == 'role' and data[key]:
                    data[key] = _(data[key].strip())

        self.log.info(Logs.fileline() + ' : SettingLinkUnit')
        return compose_ret(l_datas, Constants.cst_content_type_json, 200)

    def post(self, type, id_unit):
        args = request.get_json()

        # self.log.info(Logs.fileline() + ' : DEBUG-TRACE args=' + str(args))

        if 'list_link' not in args:
            self.log.error(Logs.fileline() + ' : SettingLinkUnit ERROR args missing')
            return compose_ret('', Constants.cst_content_type_json, 400)

        l_link_unit = Setting.getListLinkUnit(type, id_unit)

        for link in args['list_link']:
            if link['id_item'] and link['id_item'] not in l_link_unit:
                ret = Setting.insertLinkUnit(ful_fun=id_unit,
                                             ful_ref=link['id_item'],
                                             ful_type=type)

                if not ret:
                    self.log.info(Logs.fileline() + ' : TRACE SettingLinkUnit ERROR insertLinkUnit')
                    return compose_ret('', Constants.cst_content_type_json, 500)

        # delete missing values
        for db_val in l_link_unit:
            exist = False
            for ihm_val in args['list_link']:
                if db_val == ihm_val['id_item']:
                    exist = True

            if not exist:
                ret = Setting.deleteLinkUnit(type, id_unit, db_val)

                if ret is False:
                    self.log.info(Logs.fileline() + ' : TRACE SettingLinkUnit ERROR deleteLinkUnit')
                    return compose_ret('', Constants.cst_content_type_json, 500)

        self.log.info(Logs.fileline() + ' : TRACE SettingLinkUnit')
        return compose_ret('', Constants.cst_content_type_json)


class SettingLinkByUser(Resource):
    log = logging.getLogger('log_services')

    def get(self, id_user):
        l_datas = Setting.getLinkByUser(id_user)

        if not l_datas:
            self.log.error(Logs.fileline() + ' : ' + 'SettingLinkByUser ERROR not found')
            return compose_ret('', Constants.cst_content_type_json, 404)

        self.log.info(Logs.fileline() + ' : SettingLinkByUser id_ser=' + str(id_user))
        return compose_ret(l_datas, Constants.cst_content_type_json, 200)


class SettingPref(Resource):
    log = logging.getLogger('log_services')

    def get(self):
        l_prefs = Setting.getPrefList()

        if not l_prefs:
            self.log.error(Logs.fileline() + ' : ' + 'SettingPref ERROR not found')
            return compose_ret('', Constants.cst_content_type_json, 404)

        for pref in l_prefs:
            # Replace None by empty string
            for key, value in list(pref.items()):
                if pref[key] is None:
                    pref[key] = ''

        self.log.info(Logs.fileline() + ' : SettingPref')
        return compose_ret(l_prefs, Constants.cst_content_type_json, 200)

    def post(self, id_owner):
        args = request.get_json()

        if id_owner < 1 or 'prix_acte' not in args or 'entete_1' not in args or 'entete_2' not in args or \
           'entete_3' not in args or 'entete_adr' not in args or 'entete_tel' not in args or 'entete_fax' not in args or \
           'entete_email' not in args or 'entete_ville' not in args or 'facturation_pat_hosp' not in args or \
           'unite_age_defaut' not in args or 'auto_logout' not in args or 'qualite' not in args or \
           'facturation' not in args or 'default_language' not in args or 'db_language' not in args:
            self.log.error(Logs.fileline() + ' : SettingPref ERROR args missing')
            return compose_ret('', Constants.cst_content_type_json, 400)

        for key, value in list(args.items()):
            if key == 'db_language':
                session['lang_db'] = value
                session.modified = True

            if key == 'default_language':
                session['lang_pdf'] = value
                session.modified = True

            ret = Setting.updatePref(id_owner, key, value)

            if ret is False:
                self.log.error(Logs.alert() + ' : SettingPref ERROR update')
                return compose_ret('', Constants.cst_content_type_json, 500)

        self.log.info(Logs.fileline() + ' : TRACE SettingPref')
        return compose_ret('', Constants.cst_content_type_json)


class SettingRecNum(Resource):
    log = logging.getLogger('log_services')

    def get(self):
        setting = Setting.getRecNumSetting()

        if not setting:
            self.log.error(Logs.fileline() + ' : ERROR SettingRecNum not found')
            return compose_ret('', Constants.cst_content_type_json, 404)

        # Replace None by empty string
        for key, value in list(setting.items()):
            if setting[key] is None:
                setting[key] = ''

        if setting['rstg_date']:
            setting['rstg_date'] = datetime.strftime(setting['rstg_date'], '%Y-%m-%d %H:%M:%S')

        if setting['rstg_date_upd']:
            setting['rstg_date_upd'] = datetime.strftime(setting['rstg_date_upd'], '%Y-%m-%d %H:%M:%S')

        self.log.info(Logs.fileline() + ' : TRACE SettingRecNum')
        return compose_ret(setting, Constants.cst_content_type_json)

    def post(self):
        args = request.get_json()

        if 'id_owner' not in args or 'period' not in args or 'format' not in args or 'samp_mask' not in args or 'samp_regex' not in args:
            self.log.error(Logs.fileline() + ' : SettingRecNum ERROR args missing')
            return compose_ret('', Constants.cst_content_type_json, 400)

        ret = Setting.updateRecNumSetting(id_owner=args['id_owner'],
                                          period=args['period'],
                                          format=args['format'],
                                          samp_mask=args['samp_mask'],
                                          samp_regex=args['samp_regex'])

        if ret is False:
            self.log.error(Logs.alert() + ' : SettingRecNum ERROR update')
            return compose_ret('', Constants.cst_content_type_json, 500)

        self.log.info(Logs.fileline() + ' : TRACE SettingRecNum')
        return compose_ret('', Constants.cst_content_type_json)


class SettingReport(Resource):
    log = logging.getLogger('log_services')

    def get(self):
        setting = Setting.getReportSetting()

        if not setting:
            self.log.error(Logs.fileline() + ' : ERROR SettingReport not found')
            return compose_ret('', Constants.cst_content_type_json, 404)

        # Replace None by empty string
        for key, value in list(setting.items()):
            if setting[key] is None:
                setting[key] = ''

        if setting['sys_creation_date']:
            setting['sys_creation_date'] = datetime.strftime(setting['sys_creation_date'], '%Y-%m-%d %H:%M:%S')

        if setting['sys_last_mod_date']:
            setting['sys_last_mod_date'] = datetime.strftime(setting['sys_last_mod_date'], '%Y-%m-%d %H:%M:%S')

        self.log.info(Logs.fileline() + ' : TRACE SettingReport')
        return compose_ret(setting, Constants.cst_content_type_json)

    def post(self):
        args = request.get_json()

        if 'id_owner' not in args or 'header' not in args or 'comment' not in args or 'report_pwd' not in args:
            self.log.error(Logs.fileline() + ' : SettingReport ERROR args missing')
            return compose_ret('', Constants.cst_content_type_json, 400)

        ret = Setting.updateReportSetting(id_owner=args['id_owner'],
                                          header=args['header'],
                                          comment=args['comment'],
                                          report_pwd=args['report_pwd'])

        if ret is False:
            self.log.error(Logs.alert() + ' : SettingReport ERROR update')
            return compose_ret('', Constants.cst_content_type_json, 500)

        self.log.info(Logs.fileline() + ' : TRACE SettingReport')
        return compose_ret('', Constants.cst_content_type_json)


class SettingBackup(Resource):
    log = logging.getLogger('log_services')

    def get(self):
        setting = Setting.getBackupSetting()

        if not setting:
            self.log.error(Logs.fileline() + ' : ERROR SettingBackup not found')
            return compose_ret('1', Constants.cst_content_type_json, 404)

        # Replace None by empty string
        for key, value in list(setting.items()):
            if setting[key] is None:
                setting[key] = ''

        if setting['bks_start_time']:
            setting['bks_start_time'] = str(setting['bks_start_time'])

        self.log.info(Logs.fileline() + ' : TRACE SettingBackup')
        return compose_ret(setting, Constants.cst_content_type_json)


class ScriptBackup(Resource):
    log = logging.getLogger('log_services')

    def post(self, media):
        cmd = ('sh ' + Constants.cst_path_script + '/' + Constants.cst_script_backup + ' -m "' + media +
               '" ' + Constants.cst_io_backup + ' > ' + Constants.cst_io + 'backup.out 2>&1 &')

        self.log.error(Logs.fileline() + ' : ScriptBackup cmd=' + cmd)
        ret = os.system(cmd)

        self.log.info(Logs.fileline() + ' : TRACE ScriptBackup ret=' + str(ret))
        return compose_ret(ret, Constants.cst_content_type_json)


class ScriptGenkey(Resource):
    log = logging.getLogger('log_services')

    def post(self):
        args = request.get_json()

        if 'pwd_key' not in args:
            self.log.error(Logs.fileline() + ' : ScriptGenkey ERROR args missing')
            return compose_ret('1', Constants.cst_content_type_json, 400)

        os.environ['LABBOOK_KEY_PWD'] = args['pwd_key']

        cmd = 'sh ' + Constants.cst_path_script + '/' + Constants.cst_script_backup + Constants.cst_io_genkey

        self.log.error(Logs.fileline() + ' : ScriptGenkey cmd=' + cmd)
        ret = os.system(cmd)

        self.log.info(Logs.fileline() + ' : TRACE ScriptGenkey ret=' + str(ret))
        return compose_ret(ret, Constants.cst_content_type_json)


class ScriptInitMedia(Resource):
    log = logging.getLogger('log_services')

    def post(self, media):
        cmd = ('sh ' + Constants.cst_path_script + '/' + Constants.cst_script_backup + ' -m "' + media +
               '" ' + Constants.cst_io_initmedia)

        self.log.error(Logs.fileline() + ' : ScriptInitMedia cmd=' + cmd)
        ret = os.system(cmd)

        self.log.info(Logs.fileline() + ' : TRACE ScriptInitMedia ret=' + str(ret))
        return compose_ret(ret, Constants.cst_content_type_json)


class ScriptKeyexist(Resource):
    log = logging.getLogger('log_services')

    def get(self):
        cmd = 'sh ' + Constants.cst_path_script + '/' + Constants.cst_script_backup + Constants.cst_io_keyexist

        self.log.error(Logs.fileline() + ' : ScriptKeyexist cmd=' + cmd)
        ret = os.system(cmd)

        self.log.info(Logs.fileline() + ' : TRACE ScriptKeyexist ret=' + str(ret))
        return compose_ret(ret, Constants.cst_content_type_json)


class ScriptListarchive(Resource):
    log = logging.getLogger('log_services')

    def post(self, media):
        args = request.get_json()

        if 'user_pwd' not in args:
            self.log.error(Logs.fileline() + ' : ScriptListmedia ERROR args missing')
            return compose_ret('1', Constants.cst_content_type_json, 400)

        os.environ['LABBOOK_USER_PWD'] = args['user_pwd']

        cmd = ('sh ' + Constants.cst_path_script + '/' + Constants.cst_script_backup + ' -m "' + media +
               '" ' + Constants.cst_io_listarchive + ' > ' + Constants.cst_io + 'listarchive.out 2>&1 &')

        self.log.error(Logs.fileline() + ' : ScriptListarchive cmd=' + cmd)
        ret = os.system(cmd)

        """
        l_archive = {}

        l_archive['ret']   = ret
        l_archive['archive'] = []

        # read listarchive file
        if ret == 0:
            try:
                # No encoding forced because script return list from system so its depend of encoding of operating system
                f = open(os.path.join(Constants.cst_io, 'listarchive'), 'r')
                for archive in f:
                    l_archive['archive'].append(archive[:-1])
            except Exception:
                self.log.info(Logs.fileline() + ' : ERROR ScriptListarchive impossible to open listarchive file')
                return compose_ret(l_archive, Constants.cst_content_type_json, 500)"""

        self.log.info(Logs.fileline() + ' : TRACE ScriptListarchive ret=' + str(ret))  # l_archive=' + str(l_archive))
        return compose_ret(ret, Constants.cst_content_type_json)


class ScriptListmedia(Resource):
    log = logging.getLogger('log_services')

    def post(self, type):
        if type == "U":
            type = ' -U '
        else:
            type = ' '

        args = request.get_json()

        if 'user_pwd' not in args:
            self.log.error(Logs.fileline() + ' : ScriptListmedia ERROR args missing')
            return compose_ret('1', Constants.cst_content_type_json, 400)

        os.environ['LABBOOK_USER_PWD'] = args['user_pwd']

        cmd = ('sh ' + Constants.cst_path_script + '/' + Constants.cst_script_backup + type +
               Constants.cst_io_listmedia + ' > ' + Constants.cst_io + 'listmedia.out 2>&1 &')

        self.log.error(Logs.fileline() + ' : ScriptListmedia cmd=' + cmd)
        ret = os.system(cmd)

        """
        l_media = {}

        l_media['ret']   = ret
        l_media['media'] = []

        # read listmedia file
        if ret == 0:
            try:
                # No encoding forced because script return list from system so its depend of encoding of operating system
                f = open(os.path.join(Constants.cst_io, 'listmedia'), 'r')
                for media in f:
                    l_media['media'].append(media[:-1])
            except Exception:
                self.log.info(Logs.fileline() + ' : ERROR ScriptListmedia impossible to open listmedia file')
                return compose_ret(l_media, Constants.cst_content_type_json, 500)"""

        self.log.info(Logs.fileline() + ' : TRACE ScriptListmedia ret=' + str(ret))  # l_media=' + str(l_media))
        return compose_ret(ret, Constants.cst_content_type_json)


class ScriptProgbackup(Resource):
    log = logging.getLogger('log_services')

    def post(self):
        args = request.get_json()

        if 'start_time' not in args or 'user_pwd' not in args:
            self.log.error(Logs.fileline() + ' : ScriptProgbackup ERROR args missing')
            return compose_ret('1', Constants.cst_content_type_json, 400)

        # Extract inputs
        start_time = str(args.get('start_time', ''))
        user_pwd = args.get('user_pwd', '')

        if not re.fullmatch(r"[A-Za-z0-9 _:\-./TZ]{1,64}", start_time):
            self.log.error(Logs.fileline() + ' : ScriptProgbackup ERROR invalid start_time')
            return compose_ret('1', Constants.cst_content_type_json, 400)

        # Build absolute script path without string concatenation in the shell
        script_path = os.path.join(Constants.cst_path_script, Constants.cst_script_backup)

        if not os.path.isfile(script_path):
            self.log.error(Logs.fileline() + f" : ScriptProgbackup ERROR script not found path={script_path}")
            return compose_ret('1', Constants.cst_content_type_json, 500)

        argv = [
            "sh",
            script_path,
            "-w",
            start_time,
            Constants.cst_io_progbackup
        ]

        env = os.environ.copy()
        env['LABBOOK_USER_PWD'] = user_pwd

        try:
            result = subprocess.run(
                argv,
                env=env,
                shell=False,          # Critical: no shell
                check=False,          # We handle return code ourselves
                capture_output=True,
                text=True,
                timeout=60            # Optional: avoid hanging
            )
        except Exception as exc:
            self.log.error(Logs.fileline() + f" : ScriptProgbackup ERROR execution failed err={exc}")
            return compose_ret('1', Constants.cst_content_type_json, 500)

        # Handle return code
        if result.returncode != 0:
            self.log.error(
                Logs.fileline() + f" : ScriptProgbackup ERROR rc={result.returncode} stdout_len={len(result.stdout or '')} stderr_len={len(result.stderr or '')}"
            )
            return compose_ret('1', Constants.cst_content_type_json, 500)

        start_time_db = start_time
        if re.fullmatch(r"\d{2}:\d{2}", start_time):
            start_time_db = start_time + ':00'

        try:
            ret_db = Setting.updateBackupSetting(bks_start_time=start_time_db)
        except Exception as exc:
            self.log.error(Logs.fileline() + f" : ScriptProgbackup ERROR DB update failed err={exc}")
            return compose_ret('1', Constants.cst_content_type_json, 500)

        if not ret_db:
            self.log.error(Logs.fileline() + " : ScriptProgbackup ERROR DB update returned falsy")
            return compose_ret('1', Constants.cst_content_type_json, 500)

        self.log.info(
            Logs.fileline() + f" : ScriptProgbackup done rc=0 stdout_len={len(result.stdout or '')} stderr_len={len(result.stderr or '')}"
        )
        return compose_ret('0', Constants.cst_content_type_json, 200)


class ScriptRestart(Resource):
    log = logging.getLogger('log_services')

    def post(self):
        args = request.get_json()

        if 'pwd_user' not in args:
            self.log.error(Logs.fileline() + ' : ScriptRestart ERROR args missing')
            return compose_ret('1', Constants.cst_content_type_json, 400)

        os.environ['LABBOOK_USER_PWD'] = args['pwd_user']

        cmd = 'sh ' + Constants.cst_path_script + '/' + Constants.cst_script_backup + Constants.cst_io_restart

        self.log.error(Logs.fileline() + ' : ScriptRestart cmd=' + cmd)
        ret = os.system(cmd)

        self.log.info(Logs.fileline() + ' : TRACE ScriptRestart ret=' + str(ret))
        return compose_ret(ret, Constants.cst_content_type_json)


class ScriptRestore(Resource):
    log = logging.getLogger('log_services')

    def post(self):
        args = request.get_json()

        if 'media' not in args or 'pwd_key' not in args or 'archive' not in args:
            self.log.error(Logs.fileline() + ' : ScriptRestore ERROR args missing')
            return compose_ret('1', Constants.cst_content_type_json, 400)

        media   = str(args['media'])
        archive = str(args['archive'])

        os.environ['LABBOOK_KEY_PWD'] = args['pwd_key']

        cmd = ('sh ' + Constants.cst_path_script + '/' + Constants.cst_script_backup + ' -m "' + media +
               '" -a "' + archive + '" ' + Constants.cst_io_restore + ' > ' + Constants.cst_io + 'restore.out 2>&1 &')

        self.log.error(Logs.fileline() + ' : ScriptRestore cmd=' + cmd)
        ret = os.system(cmd)

        self.log.info(Logs.fileline() + ' : TRACE ScriptRestore ret=' + str(ret))
        return compose_ret(ret, Constants.cst_content_type_json)


class ScriptStatus(Resource):
    log = logging.getLogger('log_services')

    def get(self, mode):
        date_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        try:
            if mode == 'R':
                path = os.path.join(Constants.cst_io, Constants.cst_io_restore)
            elif mode == 'B':
                path = os.path.join(Constants.cst_io, Constants.cst_io_backup)
            elif mode == 'M':
                path = os.path.join(Constants.cst_io, Constants.cst_io_listmedia)
            elif mode == 'A':
                path = os.path.join(Constants.cst_io, Constants.cst_io_listarchive)
            else:
                self.log.info(Logs.fileline() + ' : ERROR ScriptStatus wrong mode : ' + str(mode))
                ret = "ERR;" + str(date_now) + ";Wrong mode"
                return compose_ret(ret, Constants.cst_content_type_json, 500)

            if not os.path.exists(path) or os.stat(path).st_size == 0:
                self.log.info(Logs.fileline() + ' : ERROR ScriptStatus impossible to open or empty : ' + str(path))
                ret = "WAIT;" + str(date_now) + ";Impossible to open : " + str(path)
                return compose_ret(ret, Constants.cst_content_type_json, 200)

            # No encoding forced because script return list from system so its depend of encoding of operating system
            last_line = ''

            with open(path, 'r') as f:
                for line in f:
                    pass
                last_line = line

            if not last_line:
                self.log.info(Logs.fileline() + ' : ERROR ScriptStatus impossible to open or read file, last line is empty')
                ret = "WAIT;" + str(date_now) + ";Impossible to open or read file, last line is empty"
                return compose_ret(ret, Constants.cst_content_type_json, 200)

            ret = last_line[:-1]

            if not ret or ((mode == 'M' or mode == 'A') and not ret.startswith('OK') and not ret.startswith('ERR')):
                ret = "WAIT;" + str(date_now) + ";Not finished"
            elif mode == 'M' and ret.startswith('OK'):
                l_media = {}

                l_media['ret']   = ret
                l_media['media'] = []

                try:
                    # No encoding forced because script return list from system so its depend of encoding of operating system
                    f = open(os.path.join(Constants.cst_io, 'listmedia'), 'r')
                    for media in f:
                        l_media['media'].append(media[:-1])

                    l_media['media'] = l_media['media'][:-1]  # Remove last line

                    self.log.info(Logs.fileline() + ' : l_media=' + str(l_media))
                except Exception:
                    self.log.info(Logs.fileline() + ' : ERROR ScriptStatus impossible to open listmedia file')
                    ret = "WAIT;" + str(date_now) + ";Impossible to read listmedia file"
                    return compose_ret(ret, Constants.cst_content_type_json, 200)

                self.log.info(Logs.fileline() + ' : TRACE ScriptStatus l_media=' + str(l_media))
                return compose_ret(l_media, Constants.cst_content_type_json)

            elif mode == 'A' and ret.startswith('OK'):
                l_archive = {}

                l_archive['ret']   = ret
                l_archive['archive'] = []

                # read listarchive file
                try:
                    # No encoding forced because script return list from system so its depend of encoding of operating system
                    f = open(os.path.join(Constants.cst_io, 'listarchive'), 'r')
                    for archive in f:
                        l_archive['archive'].append(archive[:-1])

                    l_archive['archive'] = l_archive['archive'][:-1]  # Remove last line

                    self.log.info(Logs.fileline() + ' : l_archive=' + str(l_archive))
                except Exception:
                    self.log.info(Logs.fileline() + ' : ERROR ScriptStatus impossible to open listarchive file')
                    ret = "WAIT;" + str(date_now) + ";Impossible to read listarchive file"
                    return compose_ret(l_archive, Constants.cst_content_type_json, 200)

                self.log.info(Logs.fileline() + ' : TRACE ScriptStatus l_archive=' + str(l_archive))
                return compose_ret(l_archive, Constants.cst_content_type_json)

        except Exception as e:
            date_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.log.info(Logs.fileline() + ' : ERROR ScriptStatus impossible to open status file exception : ' + str(e))
            ret = "ERR;" + str(date_now) + ";Impossible to read status file"
            return compose_ret(ret, Constants.cst_content_type_json, 200)  # 200 : dont want to stop poll in ihm

        self.log.info(Logs.fileline() + ' : TRACE ScriptStatus ret=' + str(ret))
        return compose_ret(ret, Constants.cst_content_type_json)


class TemplateList(Resource):
    log = logging.getLogger('log_services')

    def get(self, type=''):
        l_items = Setting.getTemplateList(type)

        if not l_items:
            self.log.error(Logs.fileline() + ' : TRACE TemplateList not found')

        for item in l_items:
            # Replace None by empty string
            for key, value in list(item.items()):
                if item[key] is None:
                    item[key] = ''

        self.log.info(Logs.fileline() + ' : TRACE TemplateList')
        return compose_ret(l_items, Constants.cst_content_type_json)


class TemplateDet(Resource):
    log = logging.getLogger('log_services')

    def get(self, id_item):
        item = Setting.getTemplate(id_item)

        if not item:
            self.log.error(Logs.fileline() + ' : ' + 'TemplateDet ERROR not found')
            return compose_ret('', Constants.cst_content_type_json, 404)

        # Replace None by empty string
        for key, value in list(item.items()):
            if item[key] is None:
                item[key] = ''

        self.log.info(Logs.fileline() + ' : TemplateDet id_item=' + str(id_item))
        return compose_ret(item, Constants.cst_content_type_json, 200)

    def post(self, id_item):
        args = request.get_json()

        if 'id_item' not in args or 'tpl_name' not in args or 'tpl_type' not in args or \
           'tpl_default' not in args or 'tpl_file' not in args:
            self.log.error(Logs.fileline() + ' : TemplateDet ERROR args missing')
            return compose_ret('', Constants.cst_content_type_json, 400)

        # Update item
        if id_item > 0:
            ret = Setting.updateTemplate(tpl_ser=id_item,
                                         tpl_name=args['tpl_name'],
                                         tpl_type=args['tpl_type'],
                                         tpl_default=args['tpl_default'],
                                         tpl_file=args['tpl_file'])

            if ret is False:
                self.log.error(Logs.alert() + ' : TemplateDet ERROR update')
                return compose_ret('', Constants.cst_content_type_json, 500)

        # Insert new item
        else:
            ret = Setting.insertTemplate(tpl_name=args['tpl_name'],
                                         tpl_type=args['tpl_type'],
                                         tpl_default=args['tpl_default'],
                                         tpl_file=args['tpl_file'])

            if ret <= 0:
                self.log.error(Logs.alert() + ' : TemplateDet ERROR  insert')
                return compose_ret('', Constants.cst_content_type_json, 500)

            id_item = ret

        self.log.info(Logs.fileline() + ' : TRACE TemplateDet id_item=' + str(id_item))
        return compose_ret(id_item, Constants.cst_content_type_json)

    def delete(self, id_item):
        ret = Setting.deleteTemplate(id_item)

        if not ret:
            self.log.error(Logs.fileline() + ' : TRACE TemplateDet delete ERROR')
            return compose_ret('', Constants.cst_content_type_json, 500)

        self.log.info(Logs.fileline() + ' : TRACE TemplateDet delete id_item=' + str(id_item))
        return compose_ret('', Constants.cst_content_type_json)


class ZipCityAdd(Resource):
    log = logging.getLogger('log_services')

    def post(self, filename):
        args = request.get_json()

        if not args and 'id_user' not in args:
            self.log.error(Logs.fileline() + ' : ZipCityAdd ERROR args missing')
            return compose_ret('', Constants.cst_content_type_json, 400)

        # Read CSV zipcity
        path = Constants.cst_path_tmp

        with open(os.path.join(path, filename), 'r', encoding='utf-8') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=';')
            l_rows = list(csv_reader)

        if not l_rows or len(l_rows) < 2:
            self.log.error(Logs.fileline() + ' : TRACE ZipCityAdd ERROR file empty')
            return compose_ret('', Constants.cst_content_type_json, 500)

        # remove headers line
        l_rows.pop(0)

        for row in l_rows:
            if row:
                zip_code  = str(row[0])
                city_name = str(row[1])

                # insert into sigl_pj_group
                ret = Setting.insertZipCity(zic_zip=zip_code, zic_city=city_name)

                if ret <= 0:
                    self.log.error(Logs.alert() + ' : ZipCityAdd ERROR insert')
                    return compose_ret('', Constants.cst_content_type_json, 500)

        Various.insertEvent(id_user=args['id_user'],
                            type='14',
                            name='EVT_INSERT',
                            message='insert into zip_city')

        self.log.info(Logs.fileline() + ' : TRACE ZipCityAdd')
        return compose_ret(ret, Constants.cst_content_type_json)


class ZipCityDelAll(Resource):
    log = logging.getLogger('log_services')

    def post(self):
        args = request.get_json()

        if not args and 'id_user' not in args:
            self.log.error(Logs.fileline() + ' : ZipCityDelAll ERROR args missing')
            return compose_ret('', Constants.cst_content_type_json, 400)

        ret = Setting.deleteAllZipCity()

        if not ret:
            self.log.error(Logs.fileline() + ' : TRACE ZipCityDelAll truncate ERROR')
            return compose_ret('', Constants.cst_content_type_json, 500)

        Various.insertEvent(id_user=args['id_user'],
                            type='16',
                            name='EVT_DELETE',
                            message='truncate table zip_city')

        self.log.info(Logs.fileline() + ' : TRACE ZipCityDelAll')
        return compose_ret(ret, Constants.cst_content_type_json)


class ZipCityDet(Resource):
    log = logging.getLogger('log_services')

    def get(self, id_item):
        item = Setting.getZipCity(id_item)

        if not item:
            self.log.error(Logs.fileline() + ' : ' + 'ZipCityDet ERROR not found')
            return compose_ret('', Constants.cst_content_type_json, 404)

        # Replace None by empty string
        for key, value in list(item.items()):
            if item[key] is None:
                item[key] = ''

        self.log.info(Logs.fileline() + ' : ZipCityDet id_item=' + str(id_item))
        return compose_ret(item, Constants.cst_content_type_json, 200)


class ZipCityList(Resource):
    log = logging.getLogger('log_services')

    def post(self):
        args = request.get_json()

        if not args:
            args = {}

        l_items = Setting.getZipCityList(args)

        if not l_items:
            self.log.error(Logs.fileline() + ' : TRACE ZipCityList not found')

        for item in l_items:
            # Replace None by empty string
            for key, value in list(item.items()):
                if item[key] is None:
                    item[key] = ''

        self.log.info(Logs.fileline() + ' : TRACE ZipCityList')
        return compose_ret(l_items, Constants.cst_content_type_json)


class ZipCitySearch(Resource):
    log = logging.getLogger('log_services')

    def post(self):
        args = request.get_json()

        l_zipcity = Setting.getZipCitySearch(args['term'])

        if not l_zipcity:
            self.log.error(Logs.fileline() + ' : TRACE ZipCitySearch not found')

        self.log.info(Logs.fileline() + ' : TRACE ZipCitySearch')
        return compose_ret(l_zipcity, Constants.cst_content_type_json)


class SettingStock(Resource):
    log = logging.getLogger('log_services')

    def get(self):
        setting = Setting.getStockSetting()

        if not setting:
            self.log.error(Logs.fileline() + ' : ERROR SettingStock not found')
            return compose_ret('', Constants.cst_content_type_json, 404)

        # Replace None by empty string
        for key, value in list(setting.items()):
            if setting[key] is None:
                setting[key] = ''

        self.log.info(Logs.fileline() + ' : TRACE SettingStock')
        return compose_ret(setting, Constants.cst_content_type_json)

    def post(self):
        args = request.get_json()

        if 'id_owner' not in args or 'expir_warning' not in args or 'expir_alert' not in args or \
           'list_local' not in args:
            self.log.error(Logs.fileline() + ' : SettingStock ERROR args missing')
            return compose_ret('', Constants.cst_content_type_json, 400)

        ret = Setting.updateStockSetting(id_owner=args['id_owner'],
                                         expir_warning=args['expir_warning'],
                                         expir_alert=args['expir_alert'])

        if ret is False:
            self.log.error(Logs.alert() + ' : SettingStock ERROR update')
            return compose_ret('', Constants.cst_content_type_json, 500)

        if args['list_local']:
            l_local = Quality.getStockLocalList()

            for local in args['list_local']:
                name = local['prl_name']

                if local['prl_ser'] > 0:
                    ret = Setting.updateStockLocal(prl_ser=local['prl_ser'],
                                                   prl_rank=local['prl_rank'],
                                                   prl_name=name)
                else:
                    ret = Setting.insertStockLocal(prl_rank=local['prl_rank'],
                                                   prl_name=name)

                if ret is False or ret <= 0:
                    self.log.info(Logs.fileline() + ' : TRACE SettingStock ERROR updateStockLocal')
                    return compose_ret('', Constants.cst_content_type_json, 500)

            # delete missing values compared to local list
            for db_local in l_local:
                exist = False
                for ihm_local in args['list_local']:
                    if db_local['prl_ser'] == ihm_local['prl_ser']:
                        exist = True

                if not exist:
                    ret = Setting.deleteStockLocal(db_local['prl_ser'])

                    if ret is False:
                        self.log.info(Logs.fileline() + ' : TRACE SettingStock ERROR deleteStockLocal')
                        return compose_ret('', Constants.cst_content_type_json, 500)

        self.log.info(Logs.fileline() + ' : TRACE SettingStock')
        return compose_ret('', Constants.cst_content_type_json)


class SettingFormList(Resource):
    log = logging.getLogger('log_services')

    def get(self):
        l_items = Setting.getSettingFormList()

        if not l_items:
            self.log.error(Logs.fileline() + ' : TRACE SettingFormList not found')

        Various.useLangPDF()

        for item in l_items:
            # Replace None by empty string
            for key, value in list(item.items()):
                if item[key] is None:
                    item[key] = ''
                elif key == 'fos_name' and item[key]:
                    item[key] = _(item[key].strip())

        self.log.info(Logs.fileline() + ' : TRACE SettingFormList')
        return compose_ret(l_items, Constants.cst_content_type_json)


class SettingFormDet(Resource):
    log = logging.getLogger('log_services')

    def post(self):
        args = request.get_json()

        if 'id_owner' not in args or 'ref' not in args or 'stat' not in args:
            self.log.error(Logs.fileline() + ' : SettingFormDet ERROR args missing')
            return compose_ret('', Constants.cst_content_type_json, 400)

        ret = Setting.updateFormSetting(ref=args['ref'],
                                        stat=args['stat'])

        if ret is False:
            self.log.error(Logs.alert() + ' : SettingFormDet ERROR update')
            return compose_ret('', Constants.cst_content_type_json, 500)

        self.log.info(Logs.fileline() + ' : TRACE SettingFormDet')
        return compose_ret('', Constants.cst_content_type_json)


class SettingManual(Resource):
    log = logging.getLogger('log_services')

    def get(self):
        l_datas = Setting.getManualSetting()

        if not l_datas:
            self.log.error(Logs.fileline() + ' : ' + 'SettingManual ERROR not found')
            return compose_ret('', Constants.cst_content_type_json, 404)

        for data in l_datas:
            # Replace None by empty string
            for key, value in list(data.items()):
                if data[key] is None:
                    data[key] = ''

        self.log.info(Logs.fileline() + ' : SettingManual')
        return compose_ret(l_datas, Constants.cst_content_type_json, 200)

    def post(self):
        args = request.get_json()

        if 'list_val' not in args:
            self.log.error(Logs.fileline() + ' : SettingManual ERROR args missing')
            return compose_ret('', Constants.cst_content_type_json, 400)

        l_manuals = Setting.getManualSetting()

        for val in args['list_val']:
            name = val['mas_name']

            if val['mas_ser'] > 0:
                ret = Setting.updateManualSetting(mas_ser=val['mas_ser'],
                                                  mas_rank=val['mas_rank'],
                                                  mas_name=name)
            else:
                ret = Setting.insertManualSetting(mas_rank=val['mas_rank'],
                                                  mas_name=name)

            if ret is False or ret <= 0:
                self.log.info(Logs.fileline() + ' : TRACE SettingManual ERROR updateManual')
                return compose_ret('', Constants.cst_content_type_json, 500)

        # delete missing values compared to age interval
        for db_val in l_manuals:
            exist = False
            for ihm_val in args['list_val']:
                if db_val['mas_ser'] == ihm_val['mas_ser']:
                    exist = True

            if not exist:
                ret = Setting.deleteManualSetting(db_val['mas_ser'])

                if ret is False:
                    self.log.info(Logs.fileline() + ' : TRACE SettingManual ERROR deleteManual')
                    return compose_ret('', Constants.cst_content_type_json, 500)

        self.log.info(Logs.fileline() + ' : TRACE SettingManual')
        return compose_ret('', Constants.cst_content_type_json)


class SettingManualCat(Resource):
    log = logging.getLogger('log_services')

    def get(self):
        l_datas = Setting.getManualCategory()

        if not l_datas:
            self.log.error(Logs.fileline() + ' : ' + 'SettingManualCat ERROR not found')
            return compose_ret('', Constants.cst_content_type_json, 404)

        for data in l_datas:
            # Replace None by empty string
            for key, value in list(data.items()):
                if data[key] is None:
                    data[key] = ''

        self.log.info(Logs.fileline() + ' : SettingManualCat')
        return compose_ret(l_datas, Constants.cst_content_type_json, 200)


class SettingDHIS2List(Resource):
    log = logging.getLogger('log_services')

    def get(self):
        l_items = Setting.getDHIS2List()

        if not l_items:
            self.log.error(Logs.fileline() + ' : TRACE SettingDHIS2List not found')

        for item in l_items:
            # Replace None by empty string
            for key, value in list(item.items()):
                if item[key] is None:
                    item[key] = ''

        self.log.info(Logs.fileline() + ' : TRACE SettingDHIS2List')
        return compose_ret(l_items, Constants.cst_content_type_json)


class SettingDHIS2Det(Resource):
    log = logging.getLogger('log_services')

    def get(self, id_item):
        item = Setting.getDHIS2Det(id_item)

        if not item:
            self.log.error(Logs.fileline() + ' : ERROR SettingDHIS2Det not found')
            return compose_ret('', Constants.cst_content_type_json, 404)

        self.log.info(Logs.fileline() + ' : TRACE SettingDHIS2Det')
        return compose_ret(item, Constants.cst_content_type_json)

    def post(self, id_item):
        args = request.get_json()

        if 'id_user' not in args or 'name' not in args or 'login' not in args or 'pwd' not in args or \
           'url' not in args or 'default' not in args:
            self.log.error(Logs.fileline() + ' : SettingDHIS2Det ERROR args missing')
            return compose_ret('', Constants.cst_content_type_json, 400)

        # Update item
        if id_item > 0:
            self.log.info(Logs.fileline() + ' : TRACE updateDHIS2Det')

            ret = Setting.updateDHIS2Det(id_item=id_item,
                                         user=args['id_user'],
                                         name=args['name'],
                                         login=args['login'],
                                         pwd=args['pwd'],
                                         url=args['url'],
                                         default=args['default'])

            if ret is False:
                self.log.error(Logs.alert() + ' : SettingDHIS2Det ERROR update')
                return compose_ret('', Constants.cst_content_type_json, 500)

        # Insert new item
        else:
            self.log.info(Logs.fileline() + ' : TRACE insertDHIS2Det')
            ret = Setting.insertDHIS2Det(user=args['id_user'],
                                         name=args['name'],
                                         login=args['login'],
                                         pwd=args['pwd'],
                                         url=args['url'],
                                         default=args['default'])

            if ret <= 0:
                self.log.error(Logs.alert() + ' : SettingDHIS2Det ERROR  insert')
                return compose_ret('', Constants.cst_content_type_json, 500)

            id_item = ret

        self.log.info(Logs.fileline() + ' : TRACE SettingDHIS2Det')
        return compose_ret('', Constants.cst_content_type_json)

    def delete(self, id_item):
        ret = Setting.deleteDHIS2Det(id_item)

        if not ret:
            self.log.error(Logs.fileline() + ' : TRACE SettingDHIS2Det delete ERROR')
            return compose_ret('', Constants.cst_content_type_json, 500)

        self.log.info(Logs.fileline() + ' : TRACE SettingDHIS2Det delete id_item=' + str(id_item))
        return compose_ret('', Constants.cst_content_type_json)


class SettingSendMethodList(Resource):
    log = logging.getLogger('log_services')

    def get(self):
        l_items = Setting.getSendingMethodList()

        if not l_items:
            self.log.info(Logs.fileline() + ' : TRACE SendingMethodList not found')

        for item in l_items:
            # Replace None by empty string
            for key, value in list(item.items()):
                if item[key] is None:
                    item[key] = ''

            if item['sdi_date']:
                item['sdi_date'] = datetime.strftime(item['sdi_date'], '%Y-%m-%d')

        self.log.info(Logs.fileline() + ' : TRACE SettingSendMethodList')
        return compose_ret(l_items, Constants.cst_content_type_json)


class SettingSendMethodDet(Resource):
    log = logging.getLogger('log_services')

    def get(self, type, id_item):
        item = Setting.getSendingMethodDet(type, id_item)

        if not item:
            self.log.error(Logs.fileline() + ' : ERROR SettingSendMethodDet not found')
            return compose_ret('', Constants.cst_content_type_json, 404)

        # Replace None by empty string
        for key, value in list(item.items()):
            if item[key] is None:
                item[key] = ''
            elif isinstance(value, (bytes, bytearray)):
                item[key] = value.decode('utf-8', errors='ignore')
            elif hasattr(value, 'strftime'):
                item[key] = value.strftime('%Y-%m-%d')

        self.log.info(Logs.fileline() + ' : TRACE SettingSendMethodDet')
        return compose_ret(item, Constants.cst_content_type_json)

    def post(self, type, id_item):
        args = request.get_json()

        if 'sdi_type' not in args or 'sdi_name' not in args or 'sdi_default' not in args:
            self.log.error(Logs.fileline() + ' : SettingSendMethodDet ERROR args missing')
            return compose_ret('', Constants.cst_content_type_json, 400)

        # Update item
        if id_item > 0:
            ret = Setting.updateSendingMethodDet(**args)

            if ret is False:
                self.log.error(Logs.alert() + ' : SettingSendMethodDet ERROR update')
                return compose_ret('', Constants.cst_content_type_json, 500)

        # Insert new item
        else:
            ret = Setting.insertSendingMethodDet(**args)

            if ret <= 0:
                self.log.error(Logs.alert() + ' : SettingSendMethodDet ERROR insert')
                return compose_ret('', Constants.cst_content_type_json, 500)

            id_item = ret

        self.log.info(Logs.fileline() + ' : TRACE SettingSendMethodDet')
        return compose_ret(id_item, Constants.cst_content_type_json)

    def delete(self, type, id_item):
        ret = Setting.deleteSendingMethodDet(type, id_item)

        if not ret:
            self.log.error(Logs.fileline() + ' : TRACE SettingSendMethodDet delete ERROR')
            return compose_ret('', Constants.cst_content_type_json, 500)

        self.log.info(Logs.fileline() + ' : TRACE SettingSendMethodDet delete id_item=' + str(id_item))
        return compose_ret('', Constants.cst_content_type_json)


class SettingSendMethodTest(Resource):
    log = logging.getLogger('log_services')

    def post(self, type, id_item):
        payload = request.get_json(silent=True) or {}
        to = payload.get('to')

        if type == 'S':
            ok, msg = Setting.testSmtpMethod(id_item, to)
        elif type == 'M':
            ok, msg = Setting.testMailjetMethod(id_item, to)
        elif type == 'W':
            ok, msg = Setting.testWhatsappMethod(id_item, to)
        else:
            return compose_ret({'error': 'Test not available for this type'},
                               Constants.cst_content_type_json, 400)

        if ok:
            self.log.info(Logs.fileline() + f' : {type} test OK for id={id_item}')
            return compose_ret({'message': msg}, Constants.cst_content_type_json)
        else:
            self.log.error(Logs.fileline() + f' : {type} test FAIL for id={id_item} -> {msg}')
            return compose_ret({'error': msg}, Constants.cst_content_type_json, 400)


class SettingSendModelList(Resource):
    log = logging.getLogger('log_services')

    def get(self):
        l_items = Setting.getSendingModelList()

        if not l_items:
            self.log.info(Logs.fileline() + ' : TRACE SendingModelList not found')

        for item in l_items:
            # Replace None by empty string
            for key, value in list(item.items()):
                if item[key] is None:
                    item[key] = ''

            if item['mdl_date']:
                item['mdl_date'] = datetime.strftime(item['mdl_date'], '%Y-%m-%d')

        self.log.info(Logs.fileline() + ' : TRACE SettingSendModelList')
        return compose_ret(l_items, Constants.cst_content_type_json)


class SettingSendModelDet(Resource):
    log = logging.getLogger('log_services')

    def get(self, type, id_item):
        item = Setting.getSendingModelDet(type, id_item)

        if not item:
            self.log.error(Logs.fileline() + ' : ERROR SettingSendModelDet not found')
            return compose_ret('', Constants.cst_content_type_json, 404)

        # Replace None by empty string
        for key, value in list(item.items()):
            if item[key] is None:
                item[key] = ''
            elif hasattr(value, 'strftime'):
                item[key] = value.strftime('%Y-%m-%d')

        self.log.info(Logs.fileline() + ' : TRACE SettingSendModelDet')
        return compose_ret(item, Constants.cst_content_type_json)

    def post(self, type, id_item):
        args = request.get_json()

        if 'mdl_type' not in args or 'mdl_displayname' not in args or 'mdl_default' not in args:
            self.log.error(Logs.fileline() + ' : SettingSendModelDet ERROR args missing')
            return compose_ret('', Constants.cst_content_type_json, 400)

        # Update item
        if id_item > 0:
            ret = Setting.updateSendingModelDet(**args)

            if ret is False:
                self.log.error(Logs.alert() + ' : SettingSendModelDet ERROR update')
                return compose_ret('', Constants.cst_content_type_json, 500)

        # Insert new item
        else:
            ret = Setting.insertSendingModelDet(**args)

            if ret <= 0:
                self.log.error(Logs.alert() + ' : SettingSendModelDet ERROR insert')
                return compose_ret('', Constants.cst_content_type_json, 500)

            id_item = ret

        self.log.info(Logs.fileline() + ' : TRACE SettingSendModelDet')
        return compose_ret(id_item, Constants.cst_content_type_json)

    def delete(self, type, id_item):
        ret = Setting.deleteSendingModelDet(type, id_item)

        if not ret:
            self.log.error(Logs.fileline() + ' : TRACE SettingSendModelDet delete ERROR')
            return compose_ret('', Constants.cst_content_type_json, 500)

        self.log.info(Logs.fileline() + ' : TRACE SettingSendModelDet delete id_item=' + str(id_item))
        return compose_ret('', Constants.cst_content_type_json)


class SettingSendModelTest(Resource):
    log = logging.getLogger('log_services')

    def post(self, type, mdl_ser):
        try:
            payload = request.get_json(force=True) or {}
            to   = (payload.get('to') or '').strip()
            lang = (payload.get('lang') or 'fr').strip()
            override_method_id = payload.get('method_id')  # optional

            if not to:
                return compose_ret({'error': 'missing recipient'}, Constants.cst_content_type_json, 400)

            # Load model
            model = Setting.getSendingModelDet(type, mdl_ser)
            if not model:
                return compose_ret({'error': 'model not found'}, Constants.cst_content_type_json, 404)

            # Pick method (override -> default -> last by date)
            method_id = Setting.pickMethodIdForTest(type, override_method_id)
            if not method_id:
                return compose_ret({'error': 'no sending method configured for this type'}, Constants.cst_content_type_json, 412)

            # Dispatch by type
            ok = False
            type_up = (type or '').upper()[:1]
            subject = f"[TEST] {model.get('mdl_displayname') or 'Model'}"

            if type_up == 'S':
                # SMTP: plain text body
                body_text = model.get('mdl_text') or ''
                ok = Setting.send_test_smtp(method_id, to, subject, body_text)

            elif type_up == 'M':
                # Mailjet: HTML allowed
                html_body = model.get('mdl_text') or ''
                ok = Setting.send_test_mailjet(method_id, to, subject, html_body)

            elif type_up == 'W':
                # WhatsApp: template name
                template_name = model.get('mdl_name') or ''
                ok = Setting.send_test_whatsapp(method_id, to, template_name, lang)

            else:
                return compose_ret({'error': 'invalid type'}, Constants.cst_content_type_json, 400)

            if ok:
                return compose_ret({'message': 'test sent'}, Constants.cst_content_type_json, 200)
            else:
                return compose_ret({'error': 'send failed'}, Constants.cst_content_type_json, 502)

        except Exception as e:
            self.log.error(Logs.fileline() + f' : ERROR model test, err={e}')
            return compose_ret({'error': 'internal error'}, Constants.cst_content_type_json, 500)


class SettingSendReport(Resource):
    log = logging.getLogger('log_services')

    def post(self):

        data = request.get_json(silent=True) or {}
        method_id   = data.get("method_id") or 0
        method_type = data.get("method_type") or ''
        template_id = data.get("template_id") or 0
        recipient   = (data.get("recipient") or '').strip()
        filename    = (data.get("file") or '').strip()
        rec_num     = data.get("rec_num")
        pat_code    = data.get("pat_code") or ''
        id_user     = data.get("id_user") or 0

        try:
            ok, msg = Setting.sendReport(method_id=method_id,
                                         method_type=method_type,
                                         template_id=template_id,
                                         recipient=recipient,
                                         filename=filename,
                                         rec_num=rec_num,
                                         pat_code=pat_code,
                                         id_user=id_user)
        except Exception as e:
            self.log.error(Logs.fileline() + ' : ERROR SettingSendReport exception err=' + str(e))
            return compose_ret({'error': "Erreur lors de l’envoi."}, Constants.cst_content_type_json, 500)

        if not ok:
            self.log.error(Logs.fileline() + ' : SettingSendReport FAIL -> ' + str(msg))
            return compose_ret({'error': msg or "Échec de l’envoi."},
                               Constants.cst_content_type_json, 502)

        self.log.info(Logs.fileline() +
                      f' : SettingSendReport OK method={method_id} tpl={template_id} rec={rec_num} user={id_user}')

        return compose_ret({'message': "Envoi déclenché."}, Constants.cst_content_type_json, 200)


class SettingSendList(Resource):
    log = logging.getLogger('log_services')

    def post(self):
        """
        Return a list of sending_event rows for the DataTable.
        """
        args  = request.get_json(silent=True) or {}
        limit = args.get('limit') or 1000

        rows = Setting.getSendingList(limit=limit)

        for r in rows:
            try:
                if r.get('sde_date') and hasattr(r['sde_date'], 'strftime'):
                    r['sde_date'] = r['sde_date'].strftime('%Y-%m-%d %H:%M:%S')
            except Exception:
                pass

            for k, v in list(r.items()):
                if r[k] is None:
                    r[k] = ''

        self.log.info(Logs.fileline() + ' : SettingSendingList count=' + str(len(rows)))
        return compose_ret(rows, Constants.cst_content_type_json, 200)


class SettingSendResend(Resource):
    log = logging.getLogger('log_services')

    def post(self, sde_ser):
        data = request.get_json(silent=True) or {}

        try:
            id_user = int(data.get("id_user") or 0)
        except Exception:
            id_user = 0

        try:
            ok, msg = Setting.resend(sde_ser=sde_ser, id_user=id_user)
        except Exception as e:
            self.log.error(Logs.fileline() + ' : ERROR SettingSendResend exception err=' + str(e))
            return compose_ret({'error': "Erreur lors du réenvoi."}, Constants.cst_content_type_json, 500)

        if not ok:
            self.log.error(Logs.fileline() + ' : SettingSendResend FAIL -> ' + str(msg))
            return compose_ret({'error': msg or "Échec du réenvoi."},
                               Constants.cst_content_type_json, 502)

        self.log.info(Logs.fileline() + f' : SettingSendResend OK sde_ser={sde_ser} user={id_user}')
        return compose_ret({'message': "Réenvoi déclenché."}, Constants.cst_content_type_json, 200)
