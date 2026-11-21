from odoo import api, fields, models

# A rating belongs to a visit, not to the restaurant. The same restaurant can
# be good one day and bad the next, and the average must be able to say so.
# The rating scale is a Selection, not an Integer: it is a fixed set of
# choices, and a Selection keeps the value readable in the database.
RATING_SELECTION = [
    ('1', '1'),
    ('2', '2'),
    ('3', '3'),
    ('4', '4'),
    ('5', '5'),
]


class LunchVisit(models.Model):
    _name = "lunch.visit"
    _description = "Visit at a restaurant"
    _order = "visit_date desc, id desc"

    restaurant_id = fields.Many2one(
        comodel_name="lunch.choice",
        string="Restaurant",
        required=True,
        ondelete="cascade",
    )
    user_id = fields.Many2one(
        comodel_name="res.users",
        string="User",
        required=True,
        ondelete="cascade",
        default=lambda self: self.env.user,
    )
    # A Date, not a Datetime: the rating is about the lunch, not the second
    # it was written down. The default is today so that "sitting at the
    # restaurant and updating" needs no date picker.
    visit_date = fields.Date(
        string="Visit date",
        required=True,
        default=fields.Date.context_today,
    )
    rating = fields.Selection(
        selection=RATING_SELECTION,
        string="Rating",
        required=True,
    )
    comment = fields.Text(string="Comment")

    # A person rates a lunch once. Changing one's mind the same day updates
    # the row; it does not add a second one. Enforced by the database, so two
    # concurrent writes cannot both pass a search-then-create check.
    _sql_constraints = [
        ('visit_unique',
            'UNIQUE(restaurant_id, user_id, visit_date)',
            "You have already rated this restaurant today."),
    ]

    @api.model
    def rate(self, restaurant, rating, visit_date=None, comment=None):
        """Create or update this user's visit at `restaurant` on `visit_date`.

        Idempotent per (restaurant, user, date): a second call with another
        rating changes the existing visit instead of adding one.
        """
        if rating not in dict(RATING_SELECTION):
            raise ValueError("Rating must be one of 1-5, got %r." % (rating,))
        visit_date = visit_date or fields.Date.context_today(self)
        visit = self.search([
            ("restaurant_id", "=", restaurant.id),
            ("user_id", "=", self.env.user.id),
            ("visit_date", "=", visit_date),
        ], limit=1)
        values = {"rating": rating}
        if comment is not None:
            values["comment"] = comment
        if visit:
            visit.write(values)
        else:
            values.update({
                "restaurant_id": restaurant.id,
                "user_id": self.env.user.id,
                "visit_date": visit_date,
            })
            visit = self.create(values)
        return visit
