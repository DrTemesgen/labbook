# -*- coding:utf-8 -*-
import json
import logging
import calendar

from datetime import datetime, date, time, timedelta
from app.models.DB import DB
from app.models.Logs import Logs

# map schedule kind to month span
SPAN_BY_KIND = {'M': 1, 'B': 2, 'T': 3, 'Q': 4, 'S': 6, 'A': 12}


class Automation:
    log = logging.getLogger('log_services')

    # ---------------------------
    # Automation JOBS
    # ---------------------------
    @staticmethod
    def getAutomationJobs(job_type=None,
                          is_active=None,
                          limit=100,
                          offset=0,
                          order_by='ajb_next_run_at',
                          order_dir='asc'):
        cursor = DB.cursor()

        valid_order_by = {
            'ajb_next_run_at',
            'ajb_created_at',
            'ajb_updated_at',
            'ajb_label',
            'ajb_type'
        }
        valid_order_dir = {'asc', 'desc'}

        order_by_sql = order_by if order_by in valid_order_by else 'ajb_next_run_at'
        order_dir_sql = order_dir.lower() if order_dir and order_dir.lower() in valid_order_dir else 'asc'

        req = (
            'select '
            '  ajb_ser, ajb_type, ajb_label, ajb_is_active, '
            '  ajb_schedule_kind, ajb_schedule_time, ajb_schedule_dow, '
            '  ajb_schedule_dom, ajb_schedule_last_dom, ajb_schedule_anchor_jan, '
            '  ajb_fire_on, ajb_schedule_start_on, ajb_next_run_at, ajb_last_run_at, '
            '  ajb_last_status, ajb_params, ajb_created_at, ajb_updated_at '
            'from automation_job '
            'where 1=1 '
        )
        params = []

        if job_type:
            req += ' and ajb_type = %s'
            params.append(job_type)

        if is_active in ('Y', 'N'):
            req += ' and ajb_is_active = %s'
            params.append(is_active)

        req += f' order by {order_by_sql} {order_dir_sql} limit %s offset %s'
        params.extend([int(limit), int(offset)])

        cursor.execute(req, tuple(params))
        rows = cursor.fetchall() or []

        for row in rows:
            if 'ajb_params' in row and isinstance(row['ajb_params'], str):
                try:
                    row['ajb_params'] = json.loads(row['ajb_params'])
                except Exception:
                    pass

        return rows

    @staticmethod
    def getAutomationJob(ajb_ser: int):
        cursor = DB.cursor()

        req = (
            'select '
            '  ajb_ser, ajb_type, ajb_label, ajb_is_active, '
            '  ajb_schedule_kind, ajb_schedule_time, ajb_schedule_dow, '
            '  ajb_schedule_dom, ajb_schedule_last_dom, ajb_schedule_anchor_jan, '
            '  ajb_fire_on, ajb_schedule_start_on, ajb_next_run_at, ajb_last_run_at, '
            '  ajb_last_status, ajb_params, ajb_created_at, ajb_updated_at '
            'from automation_job '
            'where ajb_ser = %s'
        )

        cursor.execute(req, (ajb_ser,))
        row = cursor.fetchone()
        if not row:
            return None

        if 'ajb_params' in row and isinstance(row['ajb_params'], str):
            try:
                row['ajb_params'] = json.loads(row['ajb_params'])
            except Exception:
                pass

        params = row.get('ajb_params') or {}

        recipient_keys = [
            'dhis2_internal_recipient',
            'activity_internal_recipient',
            'billing_internal_recipient',
        ]

        id_list = []
        key_to_id = {}
        for key in recipient_keys:
            raw_val = params.get(key)
            if raw_val is None or raw_val == '':
                continue
            try:
                recipient_id = int(raw_val)
                if recipient_id > 0:
                    key_to_id[key] = recipient_id
                    id_list.append(recipient_id)
            except (TypeError, ValueError):
                continue

        if id_list:
            placeholders = ','.join(['%s'] * len(id_list))
            try:
                req = (
                    "select id_data, firstname, lastname, username "
                    f"from sigl_user_data where id_data in ({placeholders})"
                )
                cursor.execute(req, tuple(id_list))
                users = cursor.fetchall() or []
            except Exception:
                users = []

            user_label = {}
            for user in users:
                first = (user.get('firstname') or '').strip()
                last = (user.get('lastname') or '').strip()
                label = (first + ' ' + last).strip()
                if not label:
                    label = (user.get('username') or '').strip()
                user_label[user.get('id_data')] = label

            for key, recipient_id in key_to_id.items():
                params[f"{key}_label"] = user_label.get(recipient_id, str(recipient_id))

            row['ajb_params'] = params

        return row

    @staticmethod
    def createAutomationJob(payload: dict) -> int:
        """
        Insert new automation_job row.
        Required:
          payload.type in ('dhis2','activity','billing')
          payload.label non-empty
          payload.schedule.kind in ('D','W','M','B','T','Q','S','A')
        """
        job_type = (payload.get('type') or '').strip()
        label = (payload.get('label') or '').strip()
        schedule = payload.get('schedule') or {}
        params_obj = payload.get('params') or {}
        is_active = (payload.get('active') or 'Y').upper()

        if job_type not in ('dhis2', 'activity', 'billing'):
            raise ValueError('invalid job type')
        if not label:
            raise ValueError('missing label')

        schedule_kind = (schedule.get('kind') or '').upper()
        if schedule_kind not in ('D', 'W', 'M', 'B', 'T', 'Q', 'S', 'A'):
            raise ValueError('invalid schedule kind')

        schedule_time = schedule.get('time') or '02:00:00'
        if len(schedule_time) == 5:
            schedule_time += ':00'

        schedule_dow = schedule.get('dow')            # int or None
        schedule_dom = schedule.get('dom')            # int or None
        schedule_last_dom = (schedule.get('last_dom') or 'N').upper()
        schedule_anchor_jan = (schedule.get('anchor_jan') or 'Y').upper()

        fire_on = (schedule.get('fire_on') or 'period_end')
        if fire_on not in ('period_start', 'period_end'):
            fire_on = 'period_end'

        schedule_start_on = schedule.get('start_on')  # 'YYYY-MM-DD' or None

        next_run_dt = compute_next_run_at(
            kind=schedule_kind,
            time_str=schedule_time,
            schedule_dow=schedule_dow,
            schedule_dom=schedule_dom,
            schedule_last_dom=schedule_last_dom,
            anchor_jan=schedule_anchor_jan,
            start_on=schedule_start_on
        )

        cursor = DB.cursor(ecr=True)

        req = (
            'insert into automation_job ('
            '  ajb_type, ajb_label, ajb_is_active, '
            '  ajb_schedule_kind, ajb_schedule_time, ajb_schedule_dow, '
            '  ajb_schedule_dom, ajb_schedule_last_dom, ajb_schedule_anchor_jan, '
            '  ajb_fire_on, ajb_schedule_start_on, ajb_next_run_at, '
            '  ajb_last_run_at, ajb_last_status, ajb_params'
            ') values ('
            '  %s, %s, %s, '
            '  %s, %s, %s, '
            '  %s, %s, %s, '
            '  %s, %s, %s, '
            '  NULL, %s, %s'
            ')'
        )

        params = [
            job_type,
            label,
            ('Y' if is_active == 'Y' else 'N'),
            schedule_kind,
            schedule_time,
            schedule_dow,
            schedule_dom,
            schedule_last_dom,
            schedule_anchor_jan,
            fire_on,
            schedule_start_on,
            next_run_dt.strftime('%Y-%m-%d %H:%M:%S'),
            'never',
            json.dumps(params_obj, ensure_ascii=False)
        ]

        try:
            cursor.execute(req, tuple(params))
            new_id = cursor.lastrowid
        except Exception as err:
            Automation.log.error(Logs.fileline() + ' : createAutomationJob SQL error=%s', err)
            return 0

        return new_id or 0

    @staticmethod
    def updateAutomationJob(ajb_ser: int, payload: dict) -> bool:
        """
        Update only fields present in payload.
        Recompute ajb_next_run_at if any schedule field changes.
        """
        if not ajb_ser:
            return False

        current = Automation.getAutomationJob(ajb_ser)
        if not current:
            return False

        set_clauses = []
        values = []

        if 'type' in payload:
            job_type = (payload.get('type') or '').strip()
            if job_type not in ('dhis2', 'activity', 'billing'):
                raise ValueError('invalid job type')
            set_clauses.append('ajb_type = %s')
            values.append(job_type)

        if 'label' in payload:
            set_clauses.append('ajb_label = %s')
            values.append((payload.get('label') or '').strip())

        if 'active' in payload:
            active_flag = 'Y' if (payload.get('active') or '').upper() == 'Y' else 'N'
            set_clauses.append('ajb_is_active = %s')
            values.append(active_flag)

        schedule = payload.get('schedule')
        schedule_changed = False

        effective_kind = current['ajb_schedule_kind']
        effective_time = current['ajb_schedule_time']
        effective_dow = current['ajb_schedule_dow']
        effective_dom = current['ajb_schedule_dom']
        effective_last_dom = current['ajb_schedule_last_dom']
        effective_anchor_jan = current['ajb_schedule_anchor_jan']
        effective_start_on = current['ajb_schedule_start_on'].strftime('%Y-%m-%d') if current['ajb_schedule_start_on'] else None

        if schedule is not None:
            if 'kind' in schedule:
                new_kind = (schedule.get('kind') or '').upper()
                if new_kind not in ('D', 'W', 'M', 'B', 'T', 'Q', 'S', 'A'):
                    raise ValueError('invalid schedule kind')
                set_clauses.append('ajb_schedule_kind = %s')
                values.append(new_kind)
                effective_kind = new_kind
                schedule_changed = True

            if 'time' in schedule:
                new_time = schedule.get('time') or '02:00:00'
                if len(new_time) == 5:
                    new_time += ':00'
                set_clauses.append('ajb_schedule_time = %s')
                values.append(new_time)
                effective_time = new_time
                schedule_changed = True

            if 'dow' in schedule:
                set_clauses.append('ajb_schedule_dow = %s')
                values.append(schedule.get('dow'))
                effective_dow = schedule.get('dow')
                schedule_changed = True

            if 'dom' in schedule:
                set_clauses.append('ajb_schedule_dom = %s')
                values.append(schedule.get('dom'))
                effective_dom = schedule.get('dom')
                schedule_changed = True

            if 'last_dom' in schedule:
                new_last_dom = (schedule.get('last_dom') or 'N').upper()
                set_clauses.append('ajb_schedule_last_dom = %s')
                values.append(new_last_dom)
                effective_last_dom = new_last_dom
                schedule_changed = True

            if 'anchor_jan' in schedule:
                new_anchor = (schedule.get('anchor_jan') or 'Y').upper()
                set_clauses.append('ajb_schedule_anchor_jan = %s')
                values.append(new_anchor)
                effective_anchor_jan = new_anchor
                schedule_changed = True

            if 'start_on' in schedule:
                set_clauses.append('ajb_schedule_start_on = %s')
                values.append(schedule.get('start_on'))
                effective_start_on = schedule.get('start_on')
                schedule_changed = True

            if 'fire_on' in schedule:
                new_fire = schedule.get('fire_on')
                if new_fire not in ('period_start', 'period_end'):
                    new_fire = 'period_end'
                set_clauses.append('ajb_fire_on = %s')
                values.append(new_fire)

        if schedule_changed:
            next_run_dt = compute_next_run_at(
                kind=effective_kind,
                time_str=effective_time,
                schedule_dow=effective_dow,
                schedule_dom=effective_dom,
                schedule_last_dom=effective_last_dom,
                anchor_jan=effective_anchor_jan,
                start_on=effective_start_on
            )
            set_clauses.append('ajb_next_run_at = %s')
            values.append(next_run_dt.strftime('%Y-%m-%d %H:%M:%S'))

        if not set_clauses:
            return True

        set_sql = ', '.join(set_clauses)
        req = f'update automation_job set {set_sql} where ajb_ser = %s'
        values.append(ajb_ser)

        cursor = DB.cursor(ecr=True)
        try:
            cursor.execute(req, tuple(values))
            return cursor.rowcount > 0
        except Exception as err:
            Automation.log.error(Logs.fileline() + ' : updateAutomationJob SQL error=%s', err)
            return False

    @staticmethod
    def deleteAutomationJob(ajb_ser: int) -> bool:
        cursor = DB.cursor(ecr=True)
        try:
            req = 'delete from automation_job where ajb_ser = %s'
            cursor.execute(req, (ajb_ser,))
            return cursor.rowcount > 0
        except Exception as err:
            Automation.log.error(Logs.fileline() + ' : deleteAutomationJob SQL error=%s', err)
            return False

    # ---------------------------
    # Automation RUNS (history)
    # ---------------------------
    @staticmethod
    def getAutomationRuns(job_id=None,
                          status=None,
                          date_from=None,
                          date_to=None,
                          limit=100,
                          offset=0):
        cursor = DB.cursor()

        req = (
            'select '
            '  arn_ser, arn_job_id, arn_started_at, arn_finished_at, arn_status, '
            '  arn_output_uri, arn_rows_count, arn_message, arn_error_trace '
            'from automation_run '
            'where 1=1 '
        )
        params = []

        if job_id:
            req += ' and arn_job_id = %s'
            params.append(int(job_id))

        if status in ('running', 'success', 'error', 'timeout'):
            req += ' and arn_status = %s'
            params.append(status)

        if date_from:
            req += ' and arn_started_at >= %s'
            params.append(date_from)

        if date_to:
            req += ' and arn_started_at <= %s'
            params.append(date_to)

        req += ' order by arn_started_at desc limit %s offset %s'
        params.extend([int(limit), int(offset)])

        try:
            cursor.execute(req, tuple(params))
            return cursor.fetchall() or []
        except Exception as err:
            Automation.log.error(Logs.fileline() + ' : getAutomationRuns SQL error=%s', err)
            return []

    # ---------------------------
    # Trigger "run now"
    # ---------------------------
    @staticmethod
    def forceAutomationRunNow(ajb_ser: int, message: str = '') -> bool:
        """
        Force next_run_at = now() so scheduler will execute ASAP.
        We do NOT pre-create a run row here, UI will see it once real run starts.
        """
        cursor = DB.cursor(ecr=True)
        try:
            req = (
                'update automation_job '
                'set ajb_next_run_at = now() '
                'where ajb_ser = %s'
            )
            cursor.execute(req, (ajb_ser,))
            if cursor.rowcount <= 0:
                return False
        except Exception as err:
            Automation.log.error(Logs.fileline() + ' : forceAutomationRunNow SQL error=%s', err)
            return False
        return True

    # ---------------------------
    # Lightweight scheduler (DB only)
    # ---------------------------
    @staticmethod
    def scheduler_process_due(max_jobs: int = 5) -> int:
        """
        Pick up to max_jobs due jobs (active, next_run_at <= now), run them sequentially.
        This method only handles DB state (start/finish runs, compute next_run_at).
        The actual job execution (HTTP, files, etc.) must be done by the runner/REST.
        """
        cursor = DB.cursor()

        req = (
            'select '
            '  ajb_ser, ajb_type, ajb_label, ajb_is_active, '
            '  ajb_schedule_kind, ajb_schedule_time, ajb_schedule_dow, '
            '  ajb_schedule_dom, ajb_schedule_last_dom, ajb_schedule_anchor_jan, '
            '  ajb_fire_on, ajb_schedule_start_on, ajb_next_run_at, ajb_last_run_at, '
            '  ajb_last_status, ajb_params '
            'from automation_job '
            'where ajb_is_active = "Y" and ajb_next_run_at is not null and ajb_next_run_at <= now() '
            'order by ajb_next_run_at asc '
            'limit %s'
        )
        cursor.execute(req, (int(max_jobs),))
        jobs = cursor.fetchall() or []
        if not jobs:
            return 0

        processed = 0
        for job in jobs:
            job_id = int(job['ajb_ser'])

            run_id = _start_run(job_id)
            if not run_id:
                continue

            cursor2 = DB.cursor(ecr=True)
            try:
                req2 = (
                    'update automation_job '
                    'set ajb_last_status = %s, ajb_last_run_at = now() '
                    'where ajb_ser = %s'
                )
                cursor2.execute(req2, ('running', job_id))
            except Exception as err:
                Automation.log.error(Logs.fileline() + ' : scheduler mark running SQL error=%s', err)

            try:
                result = _execute_job(job)  # placeholder: computes window only
                status = result.get('status') or 'error'
                rows_count = result.get('rows_count')
                output_uri = result.get('output_uri')
                message = result.get('message')
                error_trace = result.get('error_trace')
            except Exception as ex:
                status = 'error'
                rows_count = None
                output_uri = None
                message = 'unhandled exception'
                error_trace = str(ex)

            _finish_run(run_id, status, rows_count, output_uri, message, error_trace)

            try:
                next_dt = _recompute_next_from_row(job)
                cursor3 = DB.cursor(ecr=True)
                req3 = (
                    'update automation_job '
                    'set ajb_next_run_at = %s, ajb_last_status = %s '
                    'where ajb_ser = %s'
                )
                cursor3.execute(req3, (next_dt.strftime('%Y-%m-%d %H:%M:%S'), status, job_id))
            except Exception as err:
                Automation.log.error(Logs.fileline() + ' : scheduler persist next_run_at SQL error=%s', err)

            processed += 1

        return processed

    # --- aliases / helpers expected by FE ---
    @staticmethod
    def listActiveJobs():
        """Return all active jobs (Y)."""
        cursor = DB.cursor()
        req = (
            "SELECT ajb_ser, ajb_type, ajb_label, ajb_is_active, "
            "ajb_schedule_kind, ajb_schedule_time, ajb_schedule_dow, "
            "ajb_schedule_dom, ajb_schedule_last_dom, ajb_schedule_anchor_jan, "
            "ajb_fire_on, ajb_schedule_start_on, ajb_next_run_at, ajb_last_run_at, "
            "ajb_last_status, ajb_params, ajb_created_at, ajb_updated_at "
            "FROM automation_job WHERE ajb_is_active = 'Y'"
        )
        cursor.execute(req)
        rows = cursor.fetchall() or []
        for row in rows:
            param_blob = row.get('ajb_params')
            if isinstance(param_blob, str):
                try:
                    row['ajb_params'] = json.loads(param_blob)
                except Exception:
                    pass
        return rows

    @staticmethod
    def get_due_jobs(now_str):
        """Return active jobs whose next_run_at <= now_str."""
        cursor = DB.cursor()
        req = (
            "SELECT ajb_ser, ajb_type, ajb_label, ajb_is_active, "
            "ajb_schedule_kind, ajb_schedule_time, ajb_schedule_dow, "
            "ajb_schedule_dom, ajb_schedule_last_dom, ajb_schedule_anchor_jan, "
            "ajb_fire_on, ajb_schedule_start_on, ajb_next_run_at, ajb_last_run_at, "
            "ajb_last_status, ajb_params, ajb_created_at, ajb_updated_at "
            "FROM automation_job "
            "WHERE ajb_is_active = 'Y' "
            "AND ajb_next_run_at IS NOT NULL "
            "AND ajb_next_run_at <= %s"
        )
        cursor.execute(req, (now_str,))
        rows = cursor.fetchall()
        for row in rows:
            param_blob = row.get('ajb_params')
            if isinstance(param_blob, str):
                try:
                    row['ajb_params'] = json.loads(param_blob)
                except Exception:
                    pass
        return rows

    @staticmethod
    def update_next_run_at(ajb_ser, next_run_at_str):
        """Set next_run_at (on ne touche pas à last_status ici)."""
        cursor = DB.cursor()
        req = (
            "UPDATE automation_job "
            "SET ajb_next_run_at = %s, ajb_last_status = ajb_last_status "
            "WHERE ajb_ser = %s"
        )
        cursor.execute(req, (next_run_at_str, ajb_ser))
        DB.commit()

    @staticmethod
    def execute_job(job_row: dict) -> dict:
        """
        Public, sans HTTP : calcule seulement la fenêtre et retourne un message.
        L’exécution réelle (DHIS2/activity/billing) doit se faire côté REST/runner.
        """
        return _execute_job(job_row)


# ---------------------------
# Helpers (dates & runs)
# ---------------------------
def _parse_time(hhmmss: str) -> time:
    """Return a time object from 'HH:MM[:SS]' (default seconds=00)."""
    if not hhmmss:
        hhmmss = '02:00:00'
    if len(hhmmss) == 5:
        hhmmss += ':00'
    hour, minute, second = hhmmss.split(':')
    return time(int(hour), int(minute), int(second))


def _end_of_month(year: int, month: int) -> date:
    """Return last day of (year, month)."""
    last_dom = calendar.monthrange(year, month)[1]
    return date(year, month, last_dom)


def _add_months(year: int, month: int, delta: int) -> (int, int):
    """Add delta months to (year, month). Return (year, month)."""
    index = (year * 12 + (month - 1)) + delta
    whole_years, month_index = divmod(index, 12)
    return whole_years, (month_index + 1)


def _next_weekly_occurrence(base_day: date, now_dt: datetime, dow: int, run_at: time) -> datetime:
    """Compute next weekly run (1=Mon..7=Sun)."""
    target_wd = (dow - 1) % 7
    delta_days = (target_wd - base_day.weekday()) % 7
    candidate_day = base_day + timedelta(days=delta_days)
    candidate_dt = datetime.combine(candidate_day, run_at)
    if delta_days == 0 and candidate_dt <= now_dt:
        candidate_dt += timedelta(days=7)
    return candidate_dt


def _period_end_anchored_jan(base_day: date, span: int) -> date:
    """End date of the period containing base_day, anchored to January."""
    group_index = (base_day.month - 1) // span
    start_month = group_index * span + 1
    start_year = base_day.year
    end_year, end_month = _add_months(start_year, start_month, span - 1)
    return _end_of_month(end_year, end_month)


def _period_end_rolling(base_day: date, span: int) -> date:
    """End date of the rolling period starting at base_day's month."""
    start_year, start_month = base_day.year, base_day.month
    end_year, end_month = _add_months(start_year, start_month, span - 1)
    return _end_of_month(end_year, end_month)


def _apply_day_choice(month_end: date, schedule_dom: int | None, last_dom_flag: str) -> date:
    """Choose execution day within the end month: last_dom or specific dom (bounded)."""
    if (last_dom_flag or 'N').upper() == 'Y' or not schedule_dom:
        return month_end
    safe_dom = min(schedule_dom, month_end.day)
    return date(month_end.year, month_end.month, safe_dom)


def compute_next_run_at(kind: str,
                        time_str: str,
                        schedule_dow: int | None,
                        schedule_dom: int | None,
                        schedule_last_dom: str | None,
                        anchor_jan: str | None,
                        start_on: str | None,
                        now_dt: datetime | None = None) -> datetime:
    """Compute the first next_run_at >= now()"""
    run_at = _parse_time(time_str or '02:00:00')
    now_dt = now_dt or datetime.now()
    today = now_dt.date()
    base_day = today

    if start_on:
        try:
            start_day = datetime.strptime(start_on, '%Y-%m-%d').date()
            if start_day > base_day:
                base_day = start_day
        except Exception:
            pass

    if kind == 'D':
        candidate_dt = datetime.combine(base_day, run_at)
        if candidate_dt <= now_dt:
            candidate_dt = datetime.combine(base_day + timedelta(days=1), run_at)
        return candidate_dt

    if kind == 'W':
        desired_dow = int(schedule_dow or 1)
        return _next_weekly_occurrence(base_day, now_dt, desired_dow, run_at)

    span = SPAN_BY_KIND.get(kind, 1)
    use_anchor_jan = (anchor_jan or 'Y').upper() == 'Y'
    last_dom_flag = (schedule_last_dom or 'N').upper()

    def candidate_for(basis: date) -> datetime:
        month_end = _period_end_anchored_jan(basis, span) if use_anchor_jan else _period_end_rolling(basis, span)
        exec_day = _apply_day_choice(month_end, int(schedule_dom) if schedule_dom else None, last_dom_flag)
        return datetime.combine(exec_day, run_at)

    candidate_dt = candidate_for(base_day)
    if candidate_dt <= now_dt:
        jump_year, jump_month = _add_months(base_day.year, base_day.month, span)
        base_day = date(jump_year, jump_month, 1)
        candidate_dt = candidate_for(base_day)

    if start_on:
        start_day = datetime.strptime(start_on, '%Y-%m-%d').date()
        if candidate_dt.date() < start_day:
            base_day = date(start_day.year, start_day.month, 1)
            candidate_dt = candidate_for(base_day)
            if candidate_dt <= now_dt:
                jump_year, jump_month = _add_months(base_day.year, base_day.month, span)
                candidate_dt = candidate_for(date(jump_year, jump_month, 1))

    return candidate_dt


def _start_run(job_id: int, message: str = '') -> int:
    """Create a new automation_run row with status=running."""
    cursor = DB.cursor(ecr=True)
    try:
        req = (
            'insert into automation_run (arn_job_id, arn_started_at, arn_status, arn_message) '
            'values (%s, now(), %s, %s)'
        )
        cursor.execute(req, (job_id, 'running', message or ''))
        return cursor.lastrowid or 0
    except Exception as err:
        logging.getLogger('log_db').error(Logs.fileline() + ' : _start_run SQL error=%s', err)
        return 0


def _finish_run(run_id: int,
                status: str,
                rows_count: int | None = None,
                output_uri: str | None = None,
                message: str | None = None,
                error_trace: str | None = None) -> None:
    """Finalize automation_run row."""
    cursor = DB.cursor(ecr=True)
    try:
        req = (
            'update automation_run '
            'set arn_finished_at = now(), arn_status = %s, '
            '    arn_rows_count = %s, arn_output_uri = %s, '
            '    arn_message = %s, arn_error_trace = %s '
            'where arn_ser = %s'
        )
        cursor.execute(req, (status, rows_count, output_uri, message, error_trace, run_id))
    except Exception as err:
        logging.getLogger('log_db').error(Logs.fileline() + ' : _finish_run SQL error=%s', err)


def _execute_job(job_row: dict) -> dict:
    """
    Minimal executor (placeholder): compute the date window and return it in message.
    The real execution (DHIS2, activity, billing) is done by the runner/REST.
    """
    params = job_row.get('ajb_params')
    if isinstance(params, str):
        try:
            params = json.loads(params)
        except Exception:
            params = {}
    params = params or {}

    date_beg, date_end = _compute_period_window(job_row)

    message = (
        f"window: {date_beg.strftime('%Y-%m-%d')} → {date_end.strftime('%Y-%m-%d')}; "
        f"type={job_row.get('ajb_type')}"
    )

    return {
        'status': 'success',
        'rows_count': 0,
        'output_uri': None,
        'message': message,
        'error_trace': None,
    }


def _recompute_next_from_row(job_row: dict) -> datetime:
    """Recompute next_run_at using current row fields."""
    return compute_next_run_at(
        kind=job_row['ajb_schedule_kind'],
        time_str=str(job_row['ajb_schedule_time']),
        schedule_dow=job_row['ajb_schedule_dow'],
        schedule_dom=job_row['ajb_schedule_dom'],
        schedule_last_dom=job_row['ajb_schedule_last_dom'],
        anchor_jan=job_row['ajb_schedule_anchor_jan'],
        start_on=job_row['ajb_schedule_start_on'].strftime('%Y-%m-%d') if job_row['ajb_schedule_start_on'] else None
    )


def _compute_period_window(job_row: dict, now_dt: datetime | None = None) -> tuple[datetime, datetime]:
    """
    Compute [date_beg, date_end] for the job being fired now.
    Inclusive bounds, in local server time.
    Honors:
      - ajb_schedule_kind: 'D','W','M','B','T','Q','S','A'
      - ajb_schedule_dow (weekly)
      - ajb_schedule_dom / ajb_schedule_last_dom / ajb_schedule_anchor_jan (monthly-like)
      - ajb_fire_on: 'period_end' | 'period_start'
    """
    now_dt = now_dt or datetime.now()
    today = now_dt.date()

    kind = job_row['ajb_schedule_kind']
    schedule_dow = job_row['ajb_schedule_dow']          # 1..7 or None
    # schedule_last_dom = (job_row['ajb_schedule_last_dom'] or 'N').upper()
    schedule_anchor_jan = (job_row['ajb_schedule_anchor_jan'] or 'Y').upper()
    fire_on = job_row['ajb_fire_on'] or 'period_end'

    def day_bounds(d: date) -> tuple[datetime, datetime]:
        beg = datetime(d.year, d.month, d.day, 0, 0, 0)
        end = datetime(d.year, d.month, d.day, 23, 59, 59)
        return beg, end

    if kind == 'D':
        if fire_on == 'period_end':
            reference_day = today - timedelta(days=1)
            return day_bounds(reference_day)
        else:
            return day_bounds(today)

    if kind == 'W':
        target = ((schedule_dow or 1) - 1) % 7
        today_wd = today.weekday()

        if fire_on == 'period_end':
            end_day = today - timedelta(days=(today_wd - target) % 7)
            start_day = end_day - timedelta(days=6)
        else:
            start_day = today + timedelta(days=(target - today_wd) % 7)
            end_day = start_day + timedelta(days=6)

        return (
            datetime(start_day.year, start_day.month, start_day.day, 0, 0, 0),
            datetime(end_day.year, end_day.month, end_day.day, 23, 59, 59)
        )

    span = SPAN_BY_KIND.get(kind, 1)
    use_anchor = (schedule_anchor_jan == 'Y')

    def period_end_for(d: date) -> date:
        if use_anchor:
            group_idx = (d.month - 1) // span
            start_month = group_idx * span + 1
            end_year, end_month = _add_months(d.year, start_month, span - 1)
            return _end_of_month(end_year, end_month)
        else:
            end_year, end_month = _add_months(d.year, d.month, span - 1)
            return _end_of_month(end_year, end_month)

    def period_start_from_end(end_d: date) -> date:
        start_year, start_month = _add_months(end_d.year, end_d.month, -(span - 1))
        return date(start_year, start_month, 1)

    this_end = period_end_for(today)
    this_start = period_start_from_end(this_end)

    if fire_on == 'period_end':
        begin_dt = datetime(this_start.year, this_start.month, this_start.day, 0, 0, 0)
        end_dt = datetime(this_end.year, this_end.month, this_end.day, 23, 59, 59)
        return begin_dt, end_dt
    else:
        next_start_year, next_start_month = _add_months(this_start.year, this_start.month, span)
        next_start = date(next_start_year, next_start_month, 1)
        next_end = period_end_for(next_start)
        begin_dt = datetime(next_start.year, next_start.month, next_start.day, 0, 0, 0)
        end_dt = datetime(next_end.year, next_end.month, next_end.day, 23, 59, 59)
        return begin_dt, end_dt
