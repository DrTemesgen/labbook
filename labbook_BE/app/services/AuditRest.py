# -*- coding:utf-8 -*-
import logging
import json
import os

from datetime import datetime
from flask import request, send_file
from flask_restful import Resource

from app.models.General import compose_ret
from app.models.Constants import Constants
from app.models.Audit import Audit
from app.models.Logs import Logs
from app.security.oauth_routes import require_oauth


class AuditList(Resource):
    log = logging.getLogger('log_services')

    @require_oauth()
    def post(self):
        """Return latest audit trail entries as JSON list for DataTables server-side."""
        try:
            args = request.get_json(silent=True) or {}

            start = int(args.get('start', 0) or 0)
            length = int(args.get('length', 25) or 25)
            draw = args.get('draw', 1)

            order = args.get('order', [])
            order_col_index = 1
            order_dir = "desc"
            if isinstance(order, list) and len(order) > 0:
                try:
                    order_col_index = int(order[0].get('column', 1))
                    order_dir = order[0].get('dir', 'desc')
                except Exception:
                    order_col_index = 1
                    order_dir = "desc"

            search_value = ""
            search = args.get('search')
            if isinstance(search, dict):
                search_value = search.get('value') or ""

            def get_filter_value(key):
                value = args.get(key)
                if isinstance(value, str):
                    return value.strip()
                return ""

            filter_date_start = get_filter_value('filter_date_start')
            filter_date_end = get_filter_value('filter_date_end')
            filter_user = get_filter_value('filter_user')
            filter_role = get_filter_value('filter_role')
            filter_action = get_filter_value('filter_action')
            filter_status = get_filter_value('filter_status')
            filter_ip = get_filter_value('filter_ip')
            filter_resource = get_filter_value('filter_resource')

            filters = {
                "date_start": filter_date_start,
                "date_end": filter_date_end,
                "user": filter_user,
                "role": filter_role,
                "action": filter_action,
                "status": filter_status,
                "ip": filter_ip,
                "resource": filter_resource
            }

            data = Audit.listAudit(start, length, order_col_index, order_dir, search_value, filters)
            total = Audit.countAuditTotal()
            filtered = Audit.countAuditFiltered(search_value, filters)

            payload = {
                "draw": draw,
                "recordsTotal": total,
                "recordsFiltered": filtered,
                "data": data
            }
        except Exception as err:
            self.log.error(Logs.fileline() + " : AuditList ERROR listAudit err=" + str(err))
            return compose_ret('', Constants.cst_content_type_json, 500)

        self.log.info(Logs.fileline() + " : TRACE AuditList OK")
        return compose_ret(payload, Constants.cst_content_type_json, 200)


class AuditDet(Resource):
    log = logging.getLogger('log_services')

    @require_oauth()
    def get(self, aud_ser):
        try:
            data = Audit.getAuditById(aud_ser)
        except Exception as err:
            # Log error with audit id
            self.log.error(Logs.fileline() + " : AuditDet ERROR getAuditById err=" + str(err))
            return compose_ret('', Constants.cst_content_type_json, 500)

        if not data:
            self.log.error(Logs.fileline() + " : TRACE AuditDet no audit aud_ser=" + str(aud_ser))
            return compose_ret('', Constants.cst_content_type_json, 404)

        self.log.info(Logs.fileline() + " : TRACE AuditDet aud_ser=" + str(aud_ser))
        # Return dict directly so compose_ret handles JSON encoding
        return compose_ret(data, Constants.cst_content_type_json, 200)


class AuditCreate(Resource):
    log = logging.getLogger('log_services')

    @require_oauth()
    def post(self):
        """Create a new audit event."""
        data = request.get_json(force=True, silent=True)
        if not isinstance(data, dict):
            self.log.error(Logs.fileline() + " : AuditCreate ERROR invalid payload")
            return compose_ret('', Constants.cst_content_type_json, 400)

        action = data.get('action')
        if not action:
            self.log.error(Logs.fileline() + " : AuditCreate ERROR missing action")
            return compose_ret('', Constants.cst_content_type_json, 400)

        resource_type = data.get('resource_type')
        resource_id = data.get('resource_id')
        status = data.get('status')
        details = data.get('details')

        details_json = None
        if isinstance(details, dict):
            try:
                details_json = json.dumps(details, default=str)
            except Exception as err:
                self.log.error(Logs.fileline() + " : AuditCreate ERROR json.dumps details err=" + str(err))
        elif isinstance(details, str):
            details_json = details

        user_login = data.get('user_login')
        user_display = data.get('user_display')
        user_role = data.get('user_role')

        event_type = data.get('event_type') or "E"

        try:
            aud_ser = Audit.insertAudit(user_login, user_display, user_role, action, resource_type, resource_id, request.remote_addr, status, details_json, event_type)
        except Exception as err:
            self.log.error(Logs.fileline() + " : AuditCreate ERROR insertAudit err=" + str(err))
            return compose_ret('', Constants.cst_content_type_json, 500)

        self.log.info(Logs.fileline() + " : TRACE AuditCreate OK aud_ser=" + str(aud_ser))
        payload = {"aud_ser": aud_ser}
        return compose_ret(payload, Constants.cst_content_type_json, 200)


class AuditExportATNA(Resource):
    log = logging.getLogger('log_services')

    @require_oauth()
    def post(self):
        data = request.get_json(silent=True) or {}

        date_beg = data.get('date_beg')
        date_end = data.get('date_end')

        if not date_beg or not date_end:
            self.log.error(Logs.fileline() + " : AuditExportATNA ERROR args missing")
            return compose_ret('', Constants.cst_content_type_json, 400)

        try:
            d_beg = datetime.strptime(date_beg, "%Y-%m-%d").date()
            d_end = datetime.strptime(date_end, "%Y-%m-%d").date()
        except (ValueError, TypeError) as err:
            self.log.error(Logs.fileline() + " : AuditExportATNA ERROR invalid date format err=" + str(err))
            return compose_ret('', Constants.cst_content_type_json, 400)

        date_beg_utc = str(d_beg) + " 00:00:00"
        date_end_utc = str(d_end) + " 23:59:59"

        try:
            rows = Audit.listAuditByPeriod(date_beg_utc, date_end_utc)
        except Exception as err:
            self.log.error(Logs.fileline() + " : AuditExportATNA ERROR listAuditByPeriod err=" + str(err))
            return compose_ret('', Constants.cst_content_type_json, 500)

        if not rows:
            self.log.error(Logs.fileline() + " : TRACE AuditExportATNA no data")
            return compose_ret('', Constants.cst_content_type_json, 404)

        def escape_xml(value):
            if value is None:
                return ''
            text = str(value)
            text = text.replace("&", "&amp;")
            text = text.replace("<", "&lt;")
            text = text.replace(">", "&gt;")
            text = text.replace('"', "&quot;")
            text = text.replace("'", "&apos;")
            return text

        xml_lines = []
        xml_lines.append('<?xml version="1.0" encoding="UTF-8"?>')
        xml_lines.append('<ATNA_AuditMessages>')

        for r in rows:
            event_time = ""
            if r["aud_date_utc"]:
                event_time = r["aud_date_utc"].strftime("%Y-%m-%dT%H:%M:%SZ")

            outcome = "0"
            if r["aud_status"] and r["aud_status"] != "SUCCESS":
                outcome = "4"

            user_login = r["aud_user_login"] or ""
            user_role = r["aud_user_role"] or ""
            client_ip = r["aud_client_ip"] or ""
            action = r["aud_action"] or ""
            resource_type = r["aud_resource_type"] or ""
            resource_id = r["aud_resource_id"] or ""
            event_action_code = r["aud_event_type"] or "E"

            participant_id = resource_id or user_login

            details = r["aud_details"]
            details_str = None
            if details is not None:
                if isinstance(details, (dict, list)):
                    try:
                        details_str = json.dumps(details, default=str)
                    except Exception:
                        details_str = str(details)
                else:
                    details_str = str(details)

            xml_lines.append("  <AuditMessage>")
            xml_lines.append(
                '    <EventIdentification EventActionCode="' + escape_xml(event_action_code) +
                '" EventDateTime="' + escape_xml(event_time) +
                '" EventOutcomeIndicator="' + escape_xml(outcome) + '">'
            )
            xml_lines.append('      <EventTypeCode code="' + escape_xml(action) + '" codeSystemName="LabBook" displayName="' + escape_xml(action) + '"/>')
            xml_lines.append("    </EventIdentification>")

            xml_lines.append(
                '    <ActiveParticipant UserID="' + escape_xml(user_login) +
                '" UserIsRequestor="true" NetworkAccessPointID="' + escape_xml(client_ip) +
                '" NetworkAccessPointTypeCode="2">'
            )
            xml_lines.append(
                '      <RoleIDCode code="' + escape_xml(user_role) +
                '" codeSystemName="LabBookRole" displayName="' + escape_xml(user_role) + '"/>'
            )
            xml_lines.append("    </ActiveParticipant>")

            xml_lines.append(
                '    <ParticipantObjectIdentification ParticipantObjectID="' + escape_xml(participant_id) +
                '" ParticipantObjectTypeCode="1" ParticipantObjectTypeCodeRole="1">'
            )
            xml_lines.append('      <ParticipantObjectIDTypeCode code="2" codeSystemName="RFC-3881" displayName="Resource Identifier"/>')
            xml_lines.append('      <ParticipantObjectDetail type="resource_type" value="' + escape_xml(resource_type) + '"/>')
            xml_lines.append('      <ParticipantObjectDetail type="resource_id" value="' + escape_xml(resource_id) + '"/>')

            if details_str:
                xml_lines.append('      <ParticipantObjectDetail type="details_json" value="' + escape_xml(details_str) + '"/>')

            xml_lines.append("    </ParticipantObjectIdentification>")
            xml_lines.append('    <AuditSourceIdentification AuditSourceID="LabBook"/>')
            xml_lines.append("  </AuditMessage>")

        xml_lines.append("</ATNA_AuditMessages>")

        xml_content = "\n".join(xml_lines)

        try:
            base_path = Constants.cst_path_tmp
            os.makedirs(base_path, exist_ok=True)
            filename = "audit-atna_" + d_beg.strftime("%Y%m%d") + "_" + d_end.strftime("%Y%m%d") + ".xml"
            fullpath = os.path.join(base_path, filename)

            with open(fullpath, mode="w", encoding="utf-8") as f:
                f.write(xml_content)
        except Exception as err:
            self.log.error(Logs.fileline() + " : AuditExportATNA ERROR write file err=" + str(err))
            return compose_ret('', Constants.cst_content_type_json, 500)

        self.log.info(Logs.fileline() + " : TRACE AuditExportATNA file=" + filename)
        return compose_ret({"filename": filename}, Constants.cst_content_type_json, 200)


class AuditDownloadATNA(Resource):
    log = logging.getLogger('log_services')

    def get(self, filename):
        base_path = Constants.cst_path_tmp
        fullpath = os.path.join(base_path, filename)

        if not filename or not os.path.isfile(fullpath):
            self.log.error(Logs.fileline() + " : AuditDownloadATNA ERROR file not found filename=" + str(filename))
            return compose_ret('', Constants.cst_content_type_json, 404)

        try:
            return send_file(fullpath,
                             mimetype="application/xml",
                             as_attachment=True,
                             download_name=filename)
        except Exception as err:
            self.log.error(Logs.fileline() + " : AuditDownloadATNA ERROR send_file err=" + str(err))
            return compose_ret('', Constants.cst_content_type_json, 500)
