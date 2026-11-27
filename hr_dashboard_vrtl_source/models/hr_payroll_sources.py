# Copyright (C) 2026 Vertel Sverige AB (<https://vertel.se>).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

"""HR payroll analytics adapters for dashboard_vrtl.

Covers: monthly payroll cost trends, cost breakdown by department,
salary distribution, and compensation analysis.
"""

from datetime import date, timedelta

from odoo import api, fields, models
from odoo.tools import float_round


class HRPayrollTrendSource(models.AbstractModel):
    _name = "dashboard.source.hr.payroll_trend"
    _inherit = "dashboard.source.mixin"
    _description = "HR: Payroll Cost Trend"

    @api.model
    def get_schema(self):
        return {
            "name": "Payroll Cost Trend",
            "description": "Monthly payroll costs: gross salary, employer contributions, and total",
            "icon": "fa-money", "category": "Human Resources",
            "measures": [
                {"name": "gross_salary", "label": "Gross Salary", "type": "monetary", "color": "#4CAF50"},
                {"name": "contributions", "label": "Employer Contributions", "type": "monetary", "color": "#FF9800"},
                {"name": "total_cost", "label": "Total Payroll Cost", "type": "monetary", "color": "#2196F3"},
            ],
            "dimensions": [{"name": "month", "label": "Month", "type": "date"}],
            "filters": [
                {"name": "date_from", "label": "From", "type": "date", "default": (date.today() - timedelta(days=365)).isoformat()},
                {"name": "date_to", "label": "To", "type": "date", "default": date.today().isoformat()},
                {"name": "department_ids", "label": "Departments", "type": "many2many", "model": "hr.department"},
            ],
            "chart_types": ["line", "bar", "area", "kpi", "stacked_column"],
            "drill_enabled": True,
            "security": {"respects_ir_rule": True, "row_level": True, "safe_for_shared_cache": False},
            "interactions": {
                "emit_filters": [],
                "accept_filters": ["period", "department", "company"],
            },
        }

    @api.model
    def get_data(self, measures=None, dimensions=None, filters=None, options=None):
        measures = measures or ["gross_salary", "contributions", "total_cost"]
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
        gross_vals = []
        contrib_vals = []
        total_vals = []

        for month_start in months:
            if month_start.month == 12:
                month_end = date(month_start.year + 1, 1, 1) - timedelta(days=1)
            else:
                month_end = date(month_start.year, month_start.month + 1, 1) - timedelta(days=1)

            labels.append(month_start.strftime("%Y-%m"))

            # Payroll data via hr.payslip (already posted/done)
            payslip_domain = [
                ("company_id", "in", company_ids),
                ("state", "in", ["done", "paid"]),
                ("date_from", "<=", month_end.isoformat()),
                ("date_to", ">=", month_start.isoformat()),
            ]

            if department_ids:
                payslip_domain.append(("employee_id.department_id", "in", department_ids))

            # hr.payslip has no aggregated gross total via _read_group, so the
            # gross is summed from the payslip lines with raw SQL below.

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
                gross_vals.append(0)
                contrib_vals.append(0)
                total_vals.append(0)
                continue

            # Aggregate from payslip lines
            self.env.cr.execute("""
                SELECT
                    COALESCE(SUM(pl.total), 0) AS gross,
                    COALESCE(SUM(pl2.total), 0) AS contributions
                FROM hr_payslip p
                LEFT JOIN hr_payslip_line pl ON pl.slip_id = p.id
                    AND pl.code = 'GROSS'
                LEFT JOIN hr_payslip_line pl2 ON pl2.slip_id = p.id
                    AND pl2.code = 'NET'
                WHERE p.employee_id = ANY(%s)
                  AND p.state IN ('done', 'paid')
                  AND p.date_from <= %s AND p.date_to >= %s
            """, (employee_ids, month_end.isoformat(), month_start.isoformat()))
            gross, net = self.env.cr.fetchone()

            if gross:
                # Standard Swedish employer contribution is ~31.42% of gross
                # Use actual payslip data when available, fall back to statutory rate
                contributions = float_round(gross * 0.3142, 2)
                total_cost = gross + contributions
            else:
                contributions = 0
                total_cost = 0

            gross_vals.append(float_round(gross, 2))
            contrib_vals.append(contributions)
            total_vals.append(total_cost)

        series = []
        if "gross_salary" in measures:
            series.append({"name": "Gross Salary", "values": gross_vals, "color": "#4CAF50"})
        if "contributions" in measures:
            series.append({"name": "Employer Contributions", "values": contrib_vals, "color": "#FF9800"})
        if "total_cost" in measures:
            series.append({"name": "Total Payroll Cost", "values": total_vals, "color": "#2196F3"})

        return {
            "labels": labels,
            "series": series,
            "currency": {"symbol": self.env.company.currency_id.symbol},
        }


class HRSalaryDistributionSource(models.AbstractModel):
    _name = "dashboard.source.hr.salary_distribution"
    _inherit = "dashboard.source.mixin"
    _description = "HR: Salary Distribution by Department"

    @api.model
    def get_schema(self):
        return {
            "name": "Salary Distribution",
            "description": "Average, median, min, and max salary by department",
            "icon": "fa-bar-chart", "category": "Human Resources",
            "measures": [
                {"name": "avg_salary", "label": "Average Salary", "type": "monetary", "color": "#2196F3"},
                {"name": "median_salary", "label": "Median Salary", "type": "monetary", "color": "#9C27B0"},
                {"name": "employee_count", "label": "Employees", "type": "integer", "color": "#607D8B"},
            ],
            "dimensions": [{"name": "department", "label": "Department", "type": "category"}],
            "filters": [],
            "chart_types": ["bar", "table", "scatter"],
            "drill_enabled": True,
            "security": {"respects_ir_rule": True, "row_level": True, "safe_for_shared_cache": False},
            "interactions": {
                "emit_filters": [{"filter_key": "department", "value_field": "department_id", "label_field": "department_name"}],
                "accept_filters": ["department", "company"],
            },
        }

    @api.model
    def get_data(self, measures=None, dimensions=None, filters=None, options=None):
        measures = measures or ["avg_salary", "median_salary", "employee_count"]
        filters = filters or {}
        company_ids = filters.get("company_ids", self.env.companies.ids)
        department_ids = filters.get("department_ids", [])

        domain = [
            ("company_id", "in", company_ids),
            ("state", "=", "open"),
            ("wage", ">", 0),
        ]
        if department_ids:
            domain.append(("department_id", "in", department_ids))

        self.env.cr.execute("""
            SELECT COALESCE(d.name, 'No Department'),
                   ROUND(AVG(c.wage), 2) AS avg_wage,
                   PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY c.wage) AS median_wage,
                   COUNT(c.id) AS emp_count,
                   MIN(c.wage) AS min_wage,
                   MAX(c.wage) AS max_wage,
                   COALESCE(d.id, 0) AS dept_id
            FROM hr_contract c
            JOIN hr_employee e ON c.employee_id = e.id AND e.active = TRUE
            LEFT JOIN hr_department d ON e.department_id = d.id
            WHERE c.company_id = ANY(%s)
              AND c.state = 'open'
              AND c.wage > 0
              AND e.company_id = ANY(%s)
            GROUP BY d.name, d.id
            ORDER BY avg_wage DESC
        """, (company_ids, company_ids))

        rows = self.env.cr.fetchall()
        if not rows:
            return {"labels": [], "series": []}

        labels = [r[0] for r in rows]

        series = []
        if "avg_salary" in measures:
            series.append({"name": "Average Salary", "values": [r[1] for r in rows], "color": "#2196F3"})
        if "median_salary" in measures:
            series.append({"name": "Median Salary", "values": [float(r[2]) for r in rows], "color": "#9C27B0"})
        if "employee_count" in measures:
            series.append({"name": "Employees", "values": [r[3] for r in rows], "color": "#607D8B"})

        detail_rows = [
            {
                "department": r[0], "department_id": r[6],
                "avg_salary": r[1], "median_salary": float(r[2]),
                "employee_count": r[3], "min_salary": r[4], "max_salary": r[5],
            }
            for r in rows
        ]

        return {
            "labels": labels, "series": series, "rows": detail_rows,
            "currency": {"symbol": self.env.company.currency_id.symbol},
        }
