# -*- coding:utf-8 -*-
import logging

from app.models.DB import DB


class Audit:
    log = logging.getLogger('log_services')

    @staticmethod
    def listAudit(offset=0, limit=25, order_col_index=1, order_dir="desc", search_value=None, filters=None):
        cursor = DB.cursor()
        try:
            col_map = {
                1: "aud_date_utc",
                2: "aud_user_display",
                3: "aud_user_role",
                4: "aud_resource_type",
                5: "aud_action",
                6: "aud_client_ip",
                7: "aud_status",
                8: "aud_ser"
            }
            order_col = col_map.get(order_col_index, "aud_date_utc")
            order_dir = "ASC" if str(order_dir).lower() == "asc" else "DESC"

            filters = filters or {}

            sql = '''
                SELECT aud_ser,
                       aud_date_utc,
                       aud_user_login,
                       aud_user_display,
                       aud_user_role,
                       aud_resource_type,
                       aud_resource_id,
                       aud_action,
                       aud_client_ip,
                       aud_status
                FROM audit_trail
                WHERE 1=1
            '''
            params = []

            # Date filters
            if filters.get("date_start"):
                sql += " AND aud_date_utc >= %s"
                params.append(filters["date_start"] + " 00:00:00")

            if filters.get("date_end"):
                sql += " AND aud_date_utc <= %s"
                params.append(filters["date_end"] + " 23:59:59")

            # User filter (login or display)
            if filters.get("user"):
                like_user = "%" + filters["user"] + "%"
                sql += " AND (aud_user_login LIKE %s OR aud_user_display LIKE %s)"
                params.extend([like_user, like_user])

            # Role filter
            if filters.get("role"):
                role_raw = filters["role"]
                role_prefix = role_raw.split("_", 1)[0] if role_raw else ""
                if role_prefix:
                    sql += " AND LEFT(aud_user_role, 1) = %s"
                    params.append(role_prefix)

            # Action filter
            if filters.get("action"):
                sql += " AND aud_action LIKE %s"
                params.append("%" + filters["action"] + "%")

            # Status filter (exact match)
            if filters.get("status"):
                sql += " AND aud_status = %s"
                params.append(filters["status"])

            # IP filter
            if filters.get("ip"):
                sql += " AND aud_client_ip LIKE %s"
                params.append("%" + filters["ip"] + "%")

            # Resource filter on "TYPE ID"
            if filters.get("resource"):
                sql += " AND CONCAT(COALESCE(aud_resource_type, ''), ' ', COALESCE(aud_resource_id, '')) LIKE %s"
                params.append("%" + filters["resource"] + "%")

            # Global search (DataTables search box)
            if search_value:
                like = "%" + search_value + "%"
                sql += '''
                    AND (
                        aud_user_login LIKE %s OR
                        aud_user_display LIKE %s OR
                        aud_user_role LIKE %s OR
                        aud_resource_type LIKE %s OR
                        aud_resource_id LIKE %s OR
                        aud_action LIKE %s OR
                        aud_client_ip LIKE %s OR
                        aud_status LIKE %s
                    )
                '''
                params.extend([like, like, like, like, like, like, like, like])

            sql += " ORDER BY " + order_col + " " + order_dir + ", aud_ser DESC LIMIT %s, %s"
            params.extend([offset, limit])

            cursor.execute(sql, params)
            rows = cursor.fetchall()

            result = []
            for r in rows:
                item = {}
                item["aud_ser"] = r["aud_ser"]
                item["event_time_utc"] = r["aud_date_utc"].strftime("%Y-%m-%d %H:%M:%S") if r["aud_date_utc"] else ""
                item["aud_user_login"] = r["aud_user_login"] or ""
                item["user_display"] = r["aud_user_display"] or item["aud_user_login"]
                item["role_name"] = r["aud_user_role"]

                if r["aud_resource_type"] and r["aud_resource_id"]:
                    item["resource_label"] = str(r["aud_resource_type"]) + " " + str(r["aud_resource_id"])
                elif r["aud_resource_type"]:
                    item["resource_label"] = r["aud_resource_type"]
                else:
                    item["resource_label"] = r["aud_resource_id"]

                item["details_summary"] = r["aud_action"]
                item["ip_addr"] = r["aud_client_ip"]
                item["status_label"] = r["aud_status"]

                result.append(item)

            return result
        except Exception as err:
            Audit.log.error("Audit.listAudit ERROR type=" + err.__class__.__name__ + " args=" + repr(getattr(err, "args", None)))
            raise
        finally:
            try:
                cursor.close()
            except Exception:
                pass

    @staticmethod
    def countAuditTotal():
        cursor = DB.cursor()
        try:
            cursor.execute("SELECT COUNT(*) AS nb FROM audit_trail")
            row = cursor.fetchone()
            return row["nb"] if row else 0
        finally:
            try:
                cursor.close()
            except Exception:
                pass

    @staticmethod
    def countAuditFiltered(search_value=None, filters=None):
        filters = filters or {}

        # Detect if at least one filter is set
        has_filter = False
        for key in ("date_start", "date_end", "user", "role", "action", "status", "ip", "resource"):
            if filters.get(key):
                has_filter = True
                break

        # No global search, no filters => same as total
        if not search_value and not has_filter:
            return Audit.countAuditTotal()

        cursor = DB.cursor()
        try:
            sql = "SELECT COUNT(*) AS nb FROM audit_trail WHERE 1=1"
            params = []

            # Date filters
            if filters.get("date_start"):
                sql += " AND aud_date_utc >= %s"
                params.append(filters["date_start"] + " 00:00:00")

            if filters.get("date_end"):
                sql += " AND aud_date_utc <= %s"
                params.append(filters["date_end"] + " 23:59:59")

            # User filter (login or display)
            if filters.get("user"):
                like_user = "%" + filters["user"] + "%"
                sql += " AND (aud_user_login LIKE %s OR aud_user_display LIKE %s)"
                params.extend([like_user, like_user])

            # Role filter
            if filters.get("role"):
                role_raw = filters["role"]
                role_prefix = role_raw.split("_", 1)[0] if role_raw else ""
                if role_prefix:
                    sql += " AND LEFT(aud_user_role, 1) = %s"
                    params.append(role_prefix)

            # Action filter
            if filters.get("action"):
                sql += " AND aud_action LIKE %s"
                params.append("%" + filters["action"] + "%")

            # Status filter (exact match)
            if filters.get("status"):
                sql += " AND aud_status = %s"
                params.append(filters["status"])

            # IP filter
            if filters.get("ip"):
                sql += " AND aud_client_ip LIKE %s"
                params.append("%" + filters["ip"] + "%")

            # Resource filter on "TYPE ID"
            if filters.get("resource"):
                sql += " AND CONCAT(COALESCE(aud_resource_type, ''), ' ', COALESCE(aud_resource_id, '')) LIKE %s"
                params.append("%" + filters["resource"] + "%")

            # Global search (DataTables search box)
            if search_value:
                like = "%" + search_value + "%"
                sql += (
                    " AND ("
                    "aud_user_login LIKE %s OR "
                    "aud_user_display LIKE %s OR "
                    "aud_user_role LIKE %s OR "
                    "aud_resource_type LIKE %s OR "
                    "aud_resource_id LIKE %s OR "
                    "aud_action LIKE %s OR "
                    "aud_client_ip LIKE %s OR "
                    "aud_status LIKE %s)"
                )
                params.extend([like, like, like, like, like, like, like, like])

            cursor.execute(sql, params)
            row = cursor.fetchone()
            return row["nb"] if row else 0

        finally:
            try:
                cursor.close()
            except Exception:
                pass

    @staticmethod
    def listAuditByPeriod(date_beg_utc, date_end_utc):
        cursor = DB.cursor()
        try:
            sql = ('''
                SELECT aud_ser, aud_date_utc, aud_user_login, aud_user_display, aud_user_role, aud_resource_type,
                       aud_resource_id, aud_action, aud_client_ip, aud_status, aud_details, aud_event_type
                FROM audit_trail
                WHERE aud_date_utc BETWEEN %s AND %s
                ORDER BY aud_date_utc, aud_ser
            ''')
            cursor.execute(sql, [date_beg_utc, date_end_utc])
            rows = cursor.fetchall()
            return rows
        except Exception as err:
            Audit.log.error("Audit.listAuditByPeriod ERROR type=" + err.__class__.__name__ + " args=" + repr(getattr(err, "args", None)))
            raise
        finally:
            try:
                cursor.close()
            except Exception:
                pass

    @staticmethod
    def getAuditById(aud_ser):
        cursor = DB.cursor()
        try:
            sql = ('''
                SELECT aud_ser, aud_date_utc, aud_user_login, aud_user_display, aud_user_role, aud_resource_type,
                       aud_resource_id, aud_action, aud_client_ip, aud_status, aud_details
                FROM audit_trail
                WHERE aud_ser = %s
            ''')
            cursor.execute(sql, [aud_ser])
            row = cursor.fetchone()
            if not row:
                return None

            item = {}
            item["aud_ser"] = row["aud_ser"]
            item["event_time_utc"] = row["aud_date_utc"].strftime("%Y-%m-%d %H:%M:%S") if row["aud_date_utc"] else ""
            item["aud_user_login"] = row["aud_user_login"] or ""
            item["user_display"] = row["aud_user_display"] or item["aud_user_login"]
            item["role_name"] = row["aud_user_role"]
            item["resource_type"] = row["aud_resource_type"]
            item["resource_id"] = row["aud_resource_id"]
            item["action"] = row["aud_action"]
            item["ip_addr"] = row["aud_client_ip"]
            item["status_label"] = row["aud_status"]
            item["details"] = row["aud_details"]
            return item
        except Exception as err:
            Audit.log.error("Audit.getAuditById ERROR type=" + err.__class__.__name__ + " args=" + repr(getattr(err, "args", None)))
            raise
        finally:
            try:
                cursor.close()
            except Exception:
                pass

    @staticmethod
    def insertAudit(user_login, user_display, user_role, action, resource_type=None, resource_id=None, client_ip=None, status=None, details_json=None, event_type="E"):
        """Insert a new audit event into audit_trail."""
        cursor = DB.cursor()
        try:
            sql = """
                INSERT INTO audit_trail (aud_date_utc, aud_user_login, aud_user_display, aud_user_role, aud_resource_type,
                    aud_resource_id, aud_action, aud_client_ip, aud_status, aud_details, aud_event_type)
                VALUES (UTC_TIMESTAMP(), %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            params = [user_login, user_display, user_role, resource_type, resource_id, action, client_ip, status, details_json, event_type]
            cursor.execute(sql, params)
            try:
                DB.commit()
            except Exception:
                pass

            aud_ser = getattr(cursor, "lastrowid", None)
            Audit.log.info("Audit.insertAudit OK user_login=" + str(user_login) + " action=" + str(action) + " aud_ser=" + str(aud_ser))
            return aud_ser

        except Exception as err:
            try:
                DB.rollback()
            except Exception:
                pass
            Audit.log.error("Audit.insertAudit ERROR user_login=" + str(user_login) + " action=" + str(action) + " err=" + str(err))
            raise
        finally:
            try:
                cursor.close()
            except Exception:
                pass
