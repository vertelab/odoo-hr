# Copyright (C) 2026 Vertel Sverige AB (<https://vertel.se>).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

"""HR absence and leave analytics adapters for dashboard_vrtl.

Covers: sick leave trends, vacation utilization, leave balance overview,
absence patterns by department and month.
"""

from datetime import date, timedelta

from odoo import api, fields, models


class HRAbsenceTrendSource(models.AbstractModel):
    _name = "dashboard.source.hr.absence_trend"
    _inherit = "dashboard.source.mixin"
    _description = "HR: Absence Trend (Sick Leave & Vacation)"

    @api.model
    def get_schema(self):
        return {
            "name": "Absence Trend",
            "description": "Monthly sick leave and vacation days taken, by department",
            "icon": "fa-medkit", "category": "Human Resources",
            "measures": [
                {"name": "sick_days", "label": "Sick Days", "type": "float", "color": "#F44336"},
                {"name": "vacation_days", "label": "Vacation Days", "type": "float", "color": "#4CAF50"},
                {"name": "other_leave", "label": "Other Leave", "type": "float", "color": "#FF9800"},
                {"name": "total_absence", "label": "Total Absence", "type": "float", "color": "#607D8B"},
            ],
            "dimensions": [{"name": "month", "label": "Month", "type": "date"}],
            "filters": [
                {"name": "date_from", "label": "From", "type": "date", "default": (date.today() - timedelta(days=365)).isoformat()},
                {"name": "date_to", "label": "To", "type": "date", "default": date.today().isoformat()},
                {"name": "department_ids", "label": "Departments", "type": "many2many", "model": "hr.department"},
            ],
            "chart_types": ["line", "bar", "area", "stacked_column", "kpi"],
            "drill_enabled": True,
            "security": {"respects_ir_rule": True, "row_level": True, "safe_for_shared_cache": False},
            "interactions": {
                "emit_filters": [],
                "accept_filters": ["period", "department", "company"],
                "drill": {
                    "enabled": True,
                    "path": [{"type": "action", "action": "hr_holidays.hr_leave_action"}],
                },
            },
        }

    @api.model
    def get_data(self, measures=None, dimensions=None, filters=None, options=None):
        measures = measures or ["sick_days", "vacation_days", "other_leave"]
        filters = filters or {}
        date_from = filters.get("date_from", (date.today() - timedelta(days=365)).isoformat())
        date_to = filters.get("date_to", date.today().isoformat())
        department_ids = filters.get("department_ids", [])
        company_ids = filters.get("company_ids", self.env.companies.ids)

        from_date = fields.Date.from_string(date_from).replace(day=1)
        to_date = fields.Date.from_string(date_to).replace(day=1)
        months = []
        cursor = from_date
        while cursor <= to_date:
            months.append(cursor)
            if cursor.month == 12:
                cursor = cursor.replace(year=cursor.year + 1, month=1)
            else:
                cursor = cursor.replace(month=cursor.month + 1)

        labels = []
        sick_vals = []
        vacation_vals = []
        other_vals = []

        for month_start in months:
            if month_start.month == 12:
                month_end = date(month_start.year + 1, 1, 1) - timedelta(days=1)
            else:
                month_end = date(month_start.year, month_start.month + 1, 1) - timedelta(days=1)

            labels.append(month_start.strftime("%Y-%m"))

            # Leaves validated that overlap with this month
            leave_domain = [
                ("state", "=", "validate"),
                ("date_from", "<=", month_end.isoformat()),
                ("date_to", ">=", month_start.isoformat()),
                ("employee_id.company_id", "in", company_ids),
            ]
            if department_ids:
                leave_domain.append(("employee_id.department_id", "in", department_ids))

            # We need to compute actual days taken within the month window.
            # Most reliable: use _read_group on hr.leave with custom handling.
            employee_ids = self.env["hr.employee"].search([
                ("company_id", "in", company_ids),
            ]).ids
            if department_ids:
                dept_employees = self.env["hr.employee"].search([
                    ("company_id", "in", company_ids),
                    ("department_id", "in", department_ids),
                ]).ids
                employee_ids = list(set(employee_ids) & set(dept_employees))

            if not employee_ids:
                sick_vals.append(0)
                vacation_vals.append(0)
                other_vals.append(0)
                continue

            # Compute overlapping days per leave type using SQL for efficiency
            self.env.cr.execute("""
                SELECT
                    lt.leave_validation_type,
                    COALESCE(SUM(
                        LEAST(l.date_to::date, %s::date) -
                        GREATEST(l.date_from::date, %s::date) + 1
                    ), 0) AS total_days
                FROM hr_leave l
                JOIN hr_leave_type lt ON l.holiday_status_id = lt.id
                WHERE l.employee_id = ANY(%s)
                  AND l.state = 'validate'
                  AND l.date_from <= %s
                  AND l.date_to >= %s
                  AND l.holiday_type = 'employee'
                GROUP BY lt.leave_validation_type
            """, (month_end.isoformat(), month_start.isoformat(),
                  employee_ids, month_end.isoformat(), month_start.isoformat()))

            by_type = dict(self.env.cr.fetchall())

            # 'leave' type = vacation/annual leave
            # 'sick' type = sick leave
            # 'both' or other = other leave
            sick = by_type.get("sick", 0) or 0
            vacation = by_type.get("leave", 0) or 0
            other = sum(v for k, v in by_type.items() if k not in ("sick", "leave")) or 0

            sick_vals.append(sick)
            vacation_vals.append(vacation)
            other_vals.append(other)

        series = []
        if "sick_days" in measures:
            series.append({"name": "Sick Days", "values": sick_vals, "color": "#F44336"})
        if "vacation_days" in measures:
            series.append({"name": "Vacation Days", "values": vacation_vals, "color": "#4CAF50"})
        if "other_leave" in measures:
            series.append({"name": "Other Leave", "values": other_vals, "color": "#FF9800"})
        if "total_absence" in measures:
            total = [sick_vals[i] + vacation_vals[i] + other_vals[i] for i in range(len(labels))]
            series.append({"name": "Total Absence", "values": total, "color": "#607D8B"})

        return {"labels": labels, "series": series}


class HRSickLeaveByDepartmentSource(models.AbstractModel):
    _name = "dashboard.source.hr.sick_leave_by_dept"
    _inherit = "dashboard.source.mixin"
    _description = "HR: Sick Leave by Department"

    @api.model
    def get_schema(self):
        return {
            "name": "Sick Leave by Department",
            "description": "Sick leave days and rate per department (current year)",
            "icon": "fa-hospital-o", "category": "Human Resources",
            "measures": [
                {"name": "sick_days", "label": "Sick Days", "type": "float", "color": "#F44336"},
                {"name": "sick_rate", "label": "Sick Rate %", "type": "percentage", "color": "#FF5722"},
            ],
            "dimensions": [{"name": "department", "label": "Department", "type": "category"}],
            "filters": [],
            "chart_types": ["bar", "table", "meter"],
            "drill_enabled": True,
            "security": {"respects_ir_rule": True, "row_level": True, "safe_for_shared_cache": False},
            "interactions": {
                "emit_filters": [{"filter_key": "department", "value_field": "department_id", "label_field": "department_name"}],
                "accept_filters": ["department", "company"],
            },
        }

    @api.model
    def get_data(self, measures=None, dimensions=None, filters=None, options=None):
        measures = measures or ["sick_days", "sick_rate"]
        filters = filters or {}
        company_ids = filters.get("company_ids", self.env.companies.ids)
        department_ids = filters.get("department_ids", [])
        year_start = date(date.today().year, 1, 1).isoformat()
        year_end = date(date.today().year, 12, 31).isoformat()

        dept_domain = [("company_id", "in", company_ids)]
        if department_ids:
            dept_domain.append(("id", "in", department_ids))

        departments = self.env["hr.department"].search(dept_domain)
        result = []

        for dept in departments:
            emp_ids = self.env["hr.employee"].search([
                ("company_id", "in", company_ids),
                ("department_id", "=", dept.id),
            ]).ids

            if not emp_ids:
                result.append({"department": dept.display_name, "sick_days": 0,
                               "sick_rate": 0, "employee_count": 0})
                continue

            emp_count = len(emp_ids)

            # Total sick days in current year for this department
            self.env.cr.execute("""
                SELECT COALESCE(SUM(
                    LEAST(l.date_to::date, %s::date) -
                    GREATEST(l.date_from::date, %s::date) + 1
                ), 0)
                FROM hr_leave l
                JOIN hr_leave_type lt ON l.holiday_status_id = lt.id
                WHERE l.employee_id = ANY(%s)
                  AND l.state = 'validate'
                  AND l.date_from <= %s AND l.date_to >= %s
                  AND l.holiday_type = 'employee'
                  AND lt.leave_validation_type = 'sick'
            """, (year_end, year_start, emp_ids, year_end, year_start))
            sick_days = self.env.cr.fetchone()[0]

            # Sick rate: sick_days / (emp_count * working_days_in_year) * 100
            working_days_per_year = 251  # Swedish standard
            sick_rate = round(sick_days / (emp_count * working_days_per_year) * 100, 2) if emp_count else 0

            result.append({
                "department": dept.display_name, "department_id": dept.id,
                "sick_days": sick_days, "sick_rate": sick_rate,
                "employee_count": emp_count,
            })

        if not result:
            return {"labels": [], "series": []}

        labels = [r["department"] for r in result]

        series = []
        if "sick_days" in measures:
            series.append({"name": "Sick Days", "values": [r["sick_days"] for r in result], "color": "#F44336"})
        if "sick_rate" in measures:
            series.append({"name": "Sick Rate %", "values": [r["sick_rate"] for r in result], "color": "#FF5722"})

        return {"labels": labels, "series": series, "rows": result}


class HRVacationUtilizationSource(models.AbstractModel):
    _name = "dashboard.source.hr.vacation_utilization"
    _inherit = "dashboard.source.mixin"
    _description = "HR: Vacation Utilization"

    @api.model
    def get_schema(self):
        return {
            "name": "Vacation Utilization",
            "description": "Allocated vs taken vacation days per employee, with department aggregation",
            "icon": "fa-sun-o", "category": "Human Resources",
            "measures": [
                {"name": "allocated", "label": "Allocated Days", "type": "float", "color": "#2196F3"},
                {"name": "taken", "label": "Taken Days", "type": "float", "color": "#4CAF50"},
                {"name": "remaining", "label": "Remaining Days", "type": "float", "color": "#FF9800"},
                {"name": "utilization_pct", "label": "Utilization %", "type": "percentage", "color": "#9C27B0"},
            ],
            "dimensions": [{"name": "department", "label": "Department", "type": "category"}],
            "filters": [{"name": "year", "label": "Year", "type": "integer", "default": date.today().year}],
            "chart_types": ["bar", "stacked_column", "table", "meter"],
            "drill_enabled": True,
            "security": {"respects_ir_rule": True, "row_level": True, "safe_for_shared_cache": False},
            "interactions": {
                "emit_filters": [{"filter_key": "department", "value_field": "department_id", "label_field": "department_name"}],
                "accept_filters": ["department", "company"],
            },
        }

    @api.model
    def get_data(self, measures=None, dimensions=None, filters=None, options=None):
        measures = measures or ["allocated", "taken", "remaining", "utilization_pct"]
        filters = filters or {}
        company_ids = filters.get("company_ids", self.env.companies.ids)
        department_ids = filters.get("department_ids", [])
        year = filters.get("year", date.today().year)
        year_start = date(year, 1, 1).isoformat()
        year_end = date(year, 12, 31).isoformat()

        dept_domain = [("company_id", "in", company_ids)]
        if department_ids:
            dept_domain.append(("id", "in", department_ids))

        departments = self.env["hr.department"].search(dept_domain)
        result = []

        for dept in departments:
            emp_ids = self.env["hr.employee"].search([
                ("company_id", "in", company_ids),
                ("department_id", "=", dept.id),
            ]).ids

            if not emp_ids:
                result.append({"department": dept.display_name, "allocated": 0,
                               "taken": 0, "remaining": 0, "utilization_pct": 0})
                continue

            # Total allocated vacation days from allocations valid this year
            self.env.cr.execute("""
                SELECT COALESCE(SUM(la.number_of_days), 0)
                FROM hr_leave_allocation la
                JOIN hr_leave_type lt ON la.holiday_status_id = lt.id
                WHERE la.employee_id = ANY(%s)
                  AND la.state = 'validate'
                  AND lt.leave_validation_type = 'leave'
                  AND la.date_from <= %s
                  AND (la.date_to IS NULL OR la.date_to >= %s)
            """, (emp_ids, year_end, year_start))
            allocated = float(self.env.cr.fetchone()[0] or 0)

            # Total taken vacation days this year
            self.env.cr.execute("""
                SELECT COALESCE(SUM(
                    LEAST(l.date_to::date, %s::date) -
                    GREATEST(l.date_from::date, %s::date) + 1
                ), 0)
                FROM hr_leave l
                JOIN hr_leave_type lt ON l.holiday_status_id = lt.id
                WHERE l.employee_id = ANY(%s)
                  AND l.state = 'validate'
                  AND l.date_from <= %s AND l.date_to >= %s
                  AND l.holiday_type = 'employee'
                  AND lt.leave_validation_type = 'leave'
            """, (year_end, year_start, emp_ids, year_end, year_start))
            taken = float(self.env.cr.fetchone()[0] or 0)

            remaining = max(allocated - taken, 0)
            utilization = round(taken / allocated * 100, 1) if allocated else 0

            result.append({
                "department": dept.display_name, "department_id": dept.id,
                "allocated": allocated, "taken": taken,
                "remaining": remaining, "utilization_pct": utilization,
            })

        if not result:
            return {"labels": [], "series": []}

        labels = [r["department"] for r in result]

        series = []
        if "allocated" in measures:
            series.append({"name": "Allocated", "values": [r["allocated"] for r in result], "color": "#2196F3"})
        if "taken" in measures:
            series.append({"name": "Taken", "values": [r["taken"] for r in result], "color": "#4CAF50"})
        if "remaining" in measures:
            series.append({"name": "Remaining", "values": [r["remaining"] for r in result], "color": "#FF9800"})
        if "utilization_pct" in measures:
            series.append({"name": "Utilization %", "values": [r["utilization_pct"] for r in result], "color": "#9C27B0"})

        return {"labels": labels, "series": series, "rows": result}
