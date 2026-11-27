# Copyright (C) 2026 Vertel Sverige AB (<https://vertel.se>).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

"""HR workforce analytics adapters for dashboard_vrtl.

Covers: headcount trends, department distribution, gender balance,
age demographics, tenure analysis, and turnover/retention.
"""

from datetime import date, timedelta

from odoo import api, fields, models
from odoo.tools import float_round


class HRWorkforceHeadcountSource(models.AbstractModel):
    _name = "dashboard.source.hr.headcount"
    _inherit = "dashboard.source.mixin"
    _description = "HR: Headcount Trend"

    @api.model
    def get_schema(self):
        return {
            "name": "Headcount Trend",
            "description": "Monthly employee headcount with new hires and departures",
            "icon": "fa-users", "category": "Human Resources",
            "measures": [
                {"name": "headcount", "label": "Headcount", "type": "integer", "color": "#2196F3"},
                {"name": "new_hires", "label": "New Hires", "type": "integer", "color": "#4CAF50"},
                {"name": "departures", "label": "Departures", "type": "integer", "color": "#F44336"},
            ],
            "dimensions": [{"name": "month", "label": "Month", "type": "date"}],
            "filters": [
                {"name": "date_from", "label": "From", "type": "date", "default": (date.today() - timedelta(days=365)).isoformat()},
                {"name": "date_to", "label": "To", "type": "date", "default": date.today().isoformat()},
                {"name": "department_ids", "label": "Departments", "type": "many2many", "model": "hr.department"},
            ],
            "chart_types": ["line", "bar", "area", "kpi"],
            "drill_enabled": True,
            "security": {"respects_ir_rule": True, "row_level": True, "safe_for_shared_cache": False},
            "interactions": {
                "emit_filters": [],
                "accept_filters": ["period", "department", "company"],
                "drill": {
                    "enabled": True,
                    "path": [
                        {"field": "department_id", "label": "Department"},
                        {"type": "action", "action": "hr.open_view_employee_list_my"},
                    ],
                },
            },
        }

    @api.model
    def get_data(self, measures=None, dimensions=None, filters=None, options=None):
        measures = measures or ["headcount", "new_hires", "departures"]
        filters = filters or {}
        date_from = filters.get("date_from", (date.today() - timedelta(days=365)).isoformat())
        date_to = filters.get("date_to", date.today().isoformat())
        department_ids = filters.get("department_ids", [])

        Employee = self.env["hr.employee"]
        company_ids = filters.get("company_ids", self.env.companies.ids)

        # Monthly headcount snapshots via _read_group on hr.employee
        base_domain = [("company_id", "in", company_ids)]
        if department_ids:
            base_domain.append(("department_id", "in", department_ids))

        # Get months between date_from and date_to
        from_date = fields.Date.from_string(date_from).replace(day=1)
        to_date = fields.Date.from_string(date_to).replace(day=1)
        months = []
        cursor = from_date
        while cursor <= to_date:
            months.append(cursor.strftime("%Y-%m"))
            if cursor.month == 12:
                cursor = cursor.replace(year=cursor.year + 1, month=1)
            else:
                cursor = cursor.replace(month=cursor.month + 1)

        labels = []
        headcount_values = []
        hire_values = []
        departure_values = []

        for month in months:
            year, m = int(month[:4]), int(month[5:7])
            month_start = date(year, m, 1)
            if m == 12:
                month_end = date(year + 1, 1, 1) - timedelta(days=1)
            else:
                month_end = date(year, m + 1, 1) - timedelta(days=1)

            labels.append(f"{year}-{m:02d}")

            # Headcount at end of month: employees who joined before or on month_end, AND
            # who haven't left before month_end (or left on/after month_start)
            self.env.cr.execute("""
                SELECT COUNT(*)
                FROM hr_employee
                WHERE company_id = ANY(%s)
                  AND (%s::int[] IS NULL OR %s::int[] = '{}' OR department_id = ANY(%s))
                  AND create_date <= %s
                  AND (active = TRUE OR write_date >= %s)
            """, (company_ids, department_ids, department_ids, department_ids,
                  month_end.isoformat(), month_start.isoformat()))
            headcount = self.env.cr.fetchone()[0]
            headcount_values.append(headcount)

            # New hires in this month
            self.env.cr.execute("""
                SELECT COUNT(*) FROM hr_employee
                WHERE company_id = ANY(%s)
                  AND (%s::int[] IS NULL OR %s::int[] = '{}' OR department_id = ANY(%s))
                  AND create_date::date BETWEEN %s AND %s
            """, (company_ids, department_ids, department_ids, department_ids,
                  month_start.isoformat(), month_end.isoformat()))
            hires = self.env.cr.fetchone()[0]
            hire_values.append(hires)

            # Departures in this month (deactivated)
            self.env.cr.execute("""
                SELECT COUNT(*) FROM hr_employee
                WHERE company_id = ANY(%s)
                  AND (%s::int[] IS NULL OR %s::int[] = '{}' OR department_id = ANY(%s))
                  AND active = FALSE
                  AND write_date::date BETWEEN %s AND %s
            """, (company_ids, department_ids, department_ids, department_ids,
                  month_start.isoformat(), month_end.isoformat()))
            departures = self.env.cr.fetchone()[0]
            departure_values.append(departures)

        series = []
        if "headcount" in measures:
            series.append({"name": "Headcount", "values": headcount_values, "color": "#2196F3"})
        if "new_hires" in measures:
            series.append({"name": "New Hires", "values": hire_values, "color": "#4CAF50"})
        if "departures" in measures:
            series.append({"name": "Departures", "values": departure_values, "color": "#F44336"})

        return {"labels": labels, "series": series}


class HRWorkforceDepartmentSource(models.AbstractModel):
    _name = "dashboard.source.hr.department_distribution"
    _inherit = "dashboard.source.mixin"
    _description = "HR: Department Distribution"

    @api.model
    def get_schema(self):
        return {
            "name": "Department Distribution",
            "description": "Employee count and headcount percentage by department",
            "icon": "fa-building", "category": "Human Resources",
            "measures": [
                {"name": "count", "label": "Employees", "type": "integer"},
                {"name": "percentage", "label": "% of Total", "type": "percentage"},
            ],
            "dimensions": [{"name": "department", "label": "Department", "type": "category"}],
            "filters": [],
            "chart_types": ["pie", "doughnut", "bar", "table", "treemap"],
            "drill_enabled": True,
            "security": {"respects_ir_rule": True, "row_level": True, "safe_for_shared_cache": False},
            "interactions": {
                "emit_filters": [{"filter_key": "department", "value_field": "department_id", "label_field": "department_name"}],
                "accept_filters": ["company"],
            },
        }

    @api.model
    def get_data(self, measures=None, dimensions=None, filters=None, options=None):
        measures = measures or ["count"]
        company_ids = filters.get("company_ids", self.env.companies.ids) if filters else self.env.companies.ids

        records = self.env["hr.employee"]._read_group(
            domain=[("company_id", "in", company_ids)],
            groupby=["department_id"],
            aggregates=["__count"],
        )
        if not records:
            return {"labels": [], "series": []}

        labels = [d.display_name if d else "No Department" for (d, c) in records]
        values = [c for (d, c) in records]
        total = sum(values)

        series = []
        if "count" in measures:
            series.append({"name": "Employees", "values": values})
        if "percentage" in measures and total:
            series.append({"name": "% of Total", "values": [float_round(v / total * 100, 1) for v in values]})

        return {"labels": labels, "series": series}


class HRWorkforceGenderSource(models.AbstractModel):
    _name = "dashboard.source.hr.gender_balance"
    _inherit = "dashboard.source.mixin"
    _description = "HR: Gender Balance"

    @api.model
    def get_schema(self):
        return {
            "name": "Gender Balance",
            "description": "Employee distribution by gender, with optional department breakdown",
            "icon": "fa-venus-mars", "category": "Human Resources",
            "measures": [
                {"name": "count", "label": "Employees", "type": "integer"},
                {"name": "percentage", "label": "%", "type": "percentage"},
            ],
            "dimensions": [
                {"name": "gender", "label": "Gender", "type": "category"},
                {"name": "department", "label": "Department", "type": "category"},
            ],
            "filters": [],
            "chart_types": ["pie", "doughnut", "stacked_column", "table", "radar"],
            "drill_enabled": True,
            "security": {"respects_ir_rule": True, "row_level": True, "safe_for_shared_cache": False},
            "interactions": {
                "emit_filters": [
                    {"filter_key": "department", "value_field": "department_id", "label_field": "department_name"},
                ],
                "accept_filters": ["department", "company"],
            },
        }

    @api.model
    def get_data(self, measures=None, dimensions=None, filters=None, options=None):
        measures = measures or ["count"]
        filters = filters or {}
        company_ids = filters.get("company_ids", self.env.companies.ids)
        department_ids = filters.get("department_ids", [])

        domain = [("company_id", "in", company_ids)]
        if department_ids:
            domain.append(("department_id", "in", department_ids))

        gender_labels = dict(self.env["hr.employee"]._fields["gender"].selection)

        if dimensions and "department" in dimensions:
            # Stacked: each department gets a series, values by gender
            dept_records = self.env["hr.employee"]._read_group(
                domain=domain, groupby=["department_id", "gender"], aggregates=["__count"],
            )
            # Build department → {gender → count}
            result = {}
            all_genders = set()
            for (dept, gender, count) in dept_records:
                dept_name = dept.display_name if dept else "No Department"
                gender_name = gender_labels.get(gender, gender or "Unspecified")
                all_genders.add(gender_name)
                if dept_name not in result:
                    result[dept_name] = {}
                result[dept_name][gender_name] = count

            gender_list = sorted(all_genders)
            return {
                "labels": gender_list,
                "series": [
                    {"name": dept, "values": [result.get(dept, {}).get(g, 0) for g in gender_list]}
                    for dept in sorted(result.keys())
                ],
            }

        # Simple: count by gender
        records = self.env["hr.employee"]._read_group(
            domain=domain, groupby=["gender"], aggregates=["__count"],
        )
        labels = [gender_labels.get(g, str(g)) for (g, c) in records]
        values = [c for (g, c) in records]

        return {
            "labels": labels,
            "series": [{"name": "Employees", "values": values, "color": "#9C27B0"}],
        }
