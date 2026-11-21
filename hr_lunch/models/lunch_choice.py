from odoo import api, models, fields, _
import json
import logging
import random
import urllib.request
from urllib.parse import urlparse
from odoo.exceptions import UserError

from .lunch_geo import haversine
from .res_config_settings import NOMINATIM_USER_AGENT

_logger = logging.getLogger(__name__)

class lunchChoiceWinnerHistory(models.Model):
    _name = "lunch.choice.winner.history"
    _description = "History of winners"
    _order = "date desc"

    # Same fix as lunch.choice.line.vote_date: a default, not a compute.
    date = fields.Date(default=fields.Date.context_today, store=True)
    winner_id = fields.Many2one(comodel_name="lunch.choice", string="Winner", required=True, ondelete="cascade")
    winner_restaurant = fields.Char(string="Name of restaurant", related="winner_id.rest_name")
    winner_url = fields.Char(string="Url to menu", related="winner_id.link_to_menu")
    winner_address = fields.Char(string="Address", related="winner_id.rest_address")
    winner_highscore = fields.Integer(string="Amounts of wins", related="winner_id.highscore")
    winner_tags = fields.Many2many(comodel_name='lunch.tag', string='Tags', related="winner_id.tag_ids")



class LunchChoiceLine(models.Model):
    _name = "lunch.choice.line"
    _description = "Votes on a lunch choice"

    parent_id = fields.Many2one("lunch.choice", string="Lunch field", required=True, ondelete="cascade")
    vote_user = fields.Many2one("res.users", string="Votes", required=True, ondelete="cascade")
    # A default is set once; a compute is re-evaluated. The old compute used
    # now() and was recomputed whenever parent_id or vote_user changed, which
    # moved an old vote to today. The vote date must stay where it was cast.
    vote_date = fields.Datetime(default=fields.Datetime.now, store=True)

    # One vote per user per restaurant, guaranteed by the database. The old
    # code searched before creating, which is a time-of-check/time-of-use bug:
    # two concurrent clicks both saw "no votes" and both created one.
    _sql_constraints = [
        ('vote_unique',
            'UNIQUE(parent_id, vote_user)',
            "You have already voted for this restaurant."),
    ]

class LunchChoice(models.Model):
    _name = "lunch.choice"
    _description = "Lets you vote for restaurants"

    rest_name = fields.Char(string="Name of restaurant")
    link_to_menu = fields.Char(string="Url to menu")
    show_vote_button = fields.Boolean(compute="_compute_show_vote_button")
    show_clear_button = fields.Boolean(compute="_compute_show_clear_button")
    voter_amount = fields.Integer(compute="_compute_voter_amount", store=True)
    show_menu_button = fields.Boolean(compute="_compute_show_menu_button")
    # The Odoo 14 default was a non-breaking space, which made an address-less
    # restaurant look like it had an address. Empty must be empty.
    rest_address = fields.Char(string="Address")
    line_ids = fields.One2many(comodel_name="lunch.choice.line", inverse_name="parent_id")
    winner_ids = fields.One2many(comodel_name="lunch.choice.winner.history", inverse_name="winner_id")
    # Derived from the history, not accumulated. The old code did
    # `highscore += 1` on a readonly field, so deleting a history row left the
    # count wrong. The number of wins IS the number of history rows.
    highscore = fields.Integer(string="Amounts of wins", compute="_compute_highscore", store=True)
    # View state, not data. Was a stored flag that a cron had to reset every
    # morning; if the cron did not run, yesterday's flag stayed.
    daily_rest = fields.Boolean(string="Daily restaurant", compute="_compute_daily_rest")
    color = fields.Integer(compute="_compute_color", string="Color")
    tag_ids = fields.Many2many(comodel_name='lunch.tag', string='Tags')
    daily_winner_rest = fields.Boolean(string="Daily Winner", compute="_compute_daily_winner_rest", search="_search_daily_winner_rest")
    show_take_away_button = fields.Boolean(compute="_compute_show_take_away_button")

    # Ratings. Our own rating is aggregated from the visits and stored, so it
    # can be sorted and filtered in the list view. The external rating is a
    # separate, labelled field: if a borrowed rating and our own shared a
    # field, a dead API agreement would empty the list of value.
    visit_ids = fields.One2many(
        comodel_name="lunch.visit",
        inverse_name="restaurant_id",
        string="Visits",
    )
    our_rating_avg = fields.Float(
        string="Our rating",
        compute="_compute_ratings",
        store=True,
        aggregator="avg",
    )
    our_rating_count = fields.Integer(
        string="Number of ratings",
        compute="_compute_ratings",
        store=True,
    )
    our_visit_count = fields.Integer(
        string="Number of visits",
        compute="_compute_visits",
        store=True,
    )
    ext_rating = fields.Float(string="External rating")
    ext_rating_count = fields.Integer(string="External rating count")
    ext_source = fields.Selection(
        selection=[('manual', 'Manual'), ('google', 'Google')],
        string="External source",
    )
    ext_fetched_at = fields.Datetime(string="External rating fetched at")
    # Price level is ordered, so it can be sorted; a tag cannot. It is a field
    # on the restaurant, not a third tag type in practice.
    price_level = fields.Selection(
        selection=[('1', '1'), ('2', '2'), ('3', '3'), ('4', '4')],
        string="Price level",
    )

    # The restaurant's own position. Filled by address enrichment or by hand;
    # this module only reads it.
    geo_lat = fields.Float(string="Latitude", digits=(10, 7))
    geo_lon = fields.Float(string="Longitude", digits=(10, 7))
    # Stored so the list can be sorted by distance. 0 means "unknown", not
    # "at the office" — see _compute_distance.
    dist_m = fields.Integer(string="Distance (m)", compute="_compute_distance", store=True)
    # Not stored. OSRM's demo server is not a production API; a stored walking
    # distance would silently go stale. Computed per read, falls back to
    # dist_m when OSRM does not answer.
    dist_walk_m = fields.Integer(string="Walking distance (m)", compute="_compute_walk")
    # Menu link health, written by check_menus() in lunch_menu_health.py.
    # Empty means "never checked", which is not the same as "dead": a new
    # restaurant has not been measured yet.
    link_status = fields.Selection(
        selection=[('ok', 'OK'), ('weak', 'Weak'), ('dead', 'Dead')],
        string="Menu link status",
    )
    link_checked_at = fields.Datetime(string="Menu link checked at")

    _sql_constraints = [
        ('rest_name_unique',
            'UNIQUE(rest_name)',
            "Restaurant name already exists!"),
    ]

    #clear votes from all restaurants
    @api.model
    def clear_all_votes(self):
        restaurants = self.search([])
        restaurants.clear_all()
        return {
        'type': 'ir.actions.client',
        'tag': 'reload'
        }
    

    def clear_all(self):
        self.line_ids.unlink()


    def clear_self_vote(self):
        self.line_ids.filtered(lambda r: r.vote_user == self.env.user).unlink()


    def valid_url(self) -> bool:
        url_string = str(self.link_to_menu).strip()
        if not url_string:
            self.link_to_menu = ""
            return False
        if url_string.lower() == "false":
            self.link_to_menu = ""
        elif not url_string.startswith("http://") and not url_string.startswith("https://"):
            self.link_to_menu = "https://" + url_string
        # Odoo 14 used the `validators` pip package here. It is not a dependency
        # of Odoo 18, and a URL check is not worth a package. The standard
        # library is enough, and the check is stricter: a menu URL must be
        # http(s) to be a menu URL.
        parsed = urlparse(url_string)
        return bool(parsed.scheme in ("http", "https") and parsed.netloc)


    def open_url(self):
        logging.warning("Opening url")
        for record in self:
            if record.valid_url():
                return {
                    "type": "ir.actions.act_url", 
                    "url": record.link_to_menu,
                    "target": "new"
                }
        return "Invalid URL"
            

    # Depended on itself before: @api.depends('link_to_menu', 'show_menu_button').
    # A field cannot be its own input; the value was unpredictable.
    @api.depends('link_to_menu')
    def _compute_show_menu_button(self):
        for record in self:
            record.show_menu_button = record.valid_url()

      
    @api.depends('line_ids')
    def _compute_voter_amount(self):
        for record in self:
            record.voter_amount = len(record.line_ids)

    @api.depends('winner_ids')
    def _compute_highscore(self):
        for record in self:
            record.highscore = len(record.winner_ids)

    # ------------------------------------------------------------------
    # Distance
    # ------------------------------------------------------------------
    # Where the office is. A company setting, not a constant: another database
    # has another office.
    COMPANY_LAT_PARAM = "hr_lunch.company_lat"
    COMPANY_LON_PARAM = "hr_lunch.company_lon"

    # OSRM's public demo server. Best effort only — see dist_walk_m.
    OSRM_URL = "https://router.project-osrm.org/route/v1/foot/{lon},{lat};{olon},{olat}"
    OSRM_TIMEOUT = 5

    @api.model
    def _company_position(self):
        """(lat, lon) from ir.config_parameter, or (None, None).

        Empty string is what Odoo stores when a float setting is cleared, and
        float('') raises. Both halves must be present: half a position is not
        a position.
        """
        params = self.env["ir.config_parameter"].sudo()
        raw_lat = params.get_param(self.COMPANY_LAT_PARAM, default="")
        raw_lon = params.get_param(self.COMPANY_LON_PARAM, default="")
        try:
            return float(raw_lat), float(raw_lon)
        except (TypeError, ValueError):
            return None, None

    @api.depends('geo_lat', 'geo_lon')
    def _compute_distance(self):
        """Straight-line distance in metres from the company position.

        Missing coordinates give 0, never an error: most of the catalogue has
        no position yet, and a compute that raises would break every write to
        lunch.choice.
        """
        company_lat, company_lon = self._company_position()
        for record in self:
            if company_lat is None or not record.geo_lat or not record.geo_lon:
                record.dist_m = 0
                continue
            record.dist_m = round(
                haversine(company_lat, company_lon, record.geo_lat, record.geo_lon)
            )

    @api.depends('dist_m', 'geo_lat', 'geo_lon')
    def _compute_walk(self):
        """Walking distance from OSRM, falling back to dist_m.

        The demo server can be down, rate-limited or gone; that is a normal
        outcome, not an error. Every failure path ends at dist_m.
        """
        company_lat, company_lon = self._company_position()
        for record in self:
            record.dist_walk_m = record._osrm_walk_distance(company_lat, company_lon)

    def _osrm_walk_distance(self, company_lat, company_lon):
        """Walking distance in metres, or dist_m when OSRM cannot answer.

        One request per record. The result is not cached across reads: the
        field is not stored, and the demo server is the only source — a
        cached answer would be a stored answer with extra steps.
        """
        self.ensure_one()
        fallback = self.dist_m or 0
        if company_lat is None or not self.geo_lat or not self.geo_lon:
            return fallback

        url = self.OSRM_URL.format(
            lon=self.geo_lon, lat=self.geo_lat,
            olon=company_lon, olat=company_lat,
        )

        try:
            request = urllib.request.Request(
                url, headers={"User-Agent": NOMINATIM_USER_AGENT}
            )
            with urllib.request.urlopen(request, timeout=self.OSRM_TIMEOUT) as response:
                payload = json.loads(response.read().decode("utf-8"))
            routes = payload.get("routes") or []
            if payload.get("code") != "Ok" or not routes:
                return fallback
            return round(routes[0]["distance"])
        except Exception as error:  # network, timeout, bad JSON, missing key
            _logger.info("OSRM walk distance unavailable for %s: %s", self.id, error)
            return fallback

    @api.depends('line_ids')
    def _compute_daily_rest(self):
        """The three restaurants with most votes today.

        Was a stored flag set by daily_procedure(). Now derived, so it cannot
        go stale when the cron does not run.
        """
        top = self.search([], order="voter_amount desc", limit=3)
        for record in self:
            record.daily_rest = record in top

    @api.depends('line_ids')
    def _compute_daily_winner_rest(self):
        """True for the single restaurant with most votes (lowest id wins a tie)."""
        restaurants = self.search([])
        voted = restaurants.filtered(lambda r: r.line_ids)
        winner = max(voted, key=lambda r: (len(r.line_ids), -r.id)) if voted else None
        for record in self:
            record.daily_winner_rest = record == winner

    def _search_daily_winner_rest(self, operator, value):
        """Non-stored fields cannot be searched without this."""
        if operator not in ("=", "!=") or not isinstance(value, bool):
            raise UserError(_("Unsupported search on Daily Winner."))
        restaurants = self.search([])
        voted = restaurants.filtered(lambda r: r.line_ids)
        winner = max(voted, key=lambda r: (len(r.line_ids), -r.id)) if voted else None
        ids = [winner.id] if winner else []
        if (operator == "=") != value:
            ids = restaurants.ids if not ids else [i for i in restaurants.ids if i not in ids]
        return [("id", "in", ids)]

    
    @api.model
    def vote_random_restaurant(self):
        """Place a random vote. Was decorated @api.depends — it is an action."""
        restaurants = self.search([])
        if restaurants:
            random_restaurant = random.choice(restaurants)
            random_restaurant.action_vote()
        return {
        'type': 'ir.actions.client',
        'tag': 'reload'
        }
        

    
    def random_rest(self):
        restaurants = self.search([('daily_rest', '=', True)])
        if restaurants:
            restaurant_ids = [restaurant.id for restaurant in restaurants]
            random.shuffle(restaurant_ids)
            random_restaurants = self.browse(restaurant_ids[:3])
            return {
                'name': 'Random Restaurants',
                'type': 'ir.actions.act_window',
                'res_model': 'lunch.choice',
                'view_mode': 'tree,form,kanban',
                'domain': [('id', 'in', random_restaurants.ids)],
            }
        else:
            raise UserError("No restaurants found")

    #This method is run as a scheduled action in odoo. This method resets the daily_winner_rest and daily_rest.
    @api.model
    def daily_procedure(self):
        """Start the day: clear yesterday's votes.

        daily_rest and daily_winner_rest are computed now, so there is nothing
        to reset — they follow the votes. What this does is clear the votes
        themselves, which is what "a new day" means.
        """
        self.search([]).clear_all()


    @api.model
    def show_top_three(self):
        lunch_records = self.search([])
        top_three_restaurants = lunch_records.filtered(lambda r: len(r.line_ids) > 0).sorted(key=lambda r: len(r.line_ids), reverse=True)[:3]
        if top_three_restaurants:
            return {
                'name': 'Top 3 Restaurants',
                'type': 'ir.actions.act_window',
                'res_model': 'lunch.choice',
                'view_mode': 'tree,form,kanban',
                'domain': [('id', 'in', top_three_restaurants.ids)],
            }
        else:
            raise UserError("No restaurants with votes found")


    @api.depends('line_ids')
    def _compute_show_vote_button(self):
        for record in self:
            record.show_vote_button = not self._user_has_voted(record)

    @api.depends('line_ids')
    def _compute_show_clear_button(self):
        for record in self:
            record.show_clear_button = self._user_has_voted(record)

    def _user_has_voted(self, record):
        return self.env.user in record.line_ids.vote_user


    # Admins may not vote. Named so the rule is visible where it is enforced.
    VOTING_BLOCKED_GROUP = "base.group_erp_manager"
    # A user may back at most this many restaurants per day.
    MAX_VOTES_PER_USER = 3

    def action_vote(self):
        """Cast a vote for this restaurant.

        Was `voted`, decorated with @api.depends — but it creates records, so
        it is not a compute and Odoo never registered it as one. It worked by
        accident: the button called it directly.

        The old version searched for the user's votes and then created one.
        That is a time-of-check/time-of-use bug; the UNIQUE constraint on
        (parent_id, vote_user) is what actually prevents a double vote. The
        three-vote limit is enforced after the insert and rolled back, so two
        concurrent votes cannot both slip past a count of two.
        """
        self.ensure_one()
        user = self.env.user

        if user.has_group(self.VOTING_BLOCKED_GROUP):
            raise UserError(_("Administrators are not allowed to vote."))

        Vote = self.env["lunch.choice.line"]
        if Vote.search_count([("parent_id", "=", self.id), ("vote_user", "=", user.id)]):
            raise UserError(_("You have already voted for this restaurant."))

        vote = Vote.create({"parent_id": self.id, "vote_user": user.id})

        # Count inside the same transaction as the insert. If the limit is
        # exceeded, the rollback removes the vote we just created.
        if Vote.search_count([("vote_user", "=", user.id)]) > self.MAX_VOTES_PER_USER:
            raise UserError(
                _("You may vote for at most %s restaurants.") % self.MAX_VOTES_PER_USER
            )

        return {"type": "ir.actions.client", "tag": "reload"}

    
    @api.model
    @api.depends('highscore')
    def _compute_color(self):
        """Kanban colour: best and second best get a colour.

        Was `compute="compute_color"` — a string, so Odoo never treated it as a
        compute and the method wrote to the database instead. It also looped
        over search([]) from a single record's compute.
        """
        restaurants = self.search([])
        ranked = sorted(restaurants, key=lambda r: r.highscore, reverse=True)
        best = ranked[0].highscore if ranked else 0
        second = ranked[1].highscore if len(ranked) > 1 else 0
        for record in self:
            if record.highscore == best and best > 0:
                record.color = 10
            elif record.highscore == second and record.highscore > 0:
                record.color = 3
            else:
                record.color = 0

    # ------------------------------------------------------------------
    # Daily tick
    # ------------------------------------------------------------------
    # The hour boundaries live here, in one place, not in two cron rows.
    MORNING_UNTIL_HOUR = 10      # before this: reset and pick three at random
    LUNCH_UNTIL_HOUR = 12        # before this: name the winner

    @api.model
    def cron_tick(self):
        """One cron entry, called daily. Decides what to do from the clock.

        Two separate cron rows would put 06:00 and 11:00 in XML, and a server
        that was down at 06:00 would simply skip the reset for that day. This
        reads the clock instead, so a late run still does the right thing.
        """
        now = fields.Datetime.context_timestamp(self, fields.Datetime.now())

        if now.weekday() >= 5:                      # Saturday, Sunday
            return

        if now.hour < self.MORNING_UNTIL_HOUR:
            if self._already_reset_today(now):
                return
            self.daily_procedure()
        elif now.hour < self.LUNCH_UNTIL_HOUR:
            self.daily_rest_winner()

    @api.model
    def _already_reset_today(self, now):
        """True when today's reset has already run.

        daily_rest is computed, so it cannot be read back as a marker. The
        marker is the cron row's last call, which Odoo updates on every run.
        """
        cron = self.env.ref("hr_lunch.ir_cron_lunch_tick", raise_if_not_found=False)
        if not cron or not cron.lastcall:
            return False
        last = fields.Datetime.context_timestamp(self, cron.lastcall)
        return last.date() == now.date()

    #This method can either be run as an menu button or scheduled action.
    @api.model
    def daily_rest_winner(self):
        """Name today's winner and write it to the history.

        Two bugs in the original:
        - It returned before calling add_to_winner_history(), so the history
          was only written when there was NO winner. That is why the table was
          empty, not because the feature was new.
        - highscore was incremented by hand (+= 1) on a readonly field. It is
          now computed from the history, so the two cannot disagree.
        """
        restaurants = self.search([])
        if not restaurants:
            return

        # daily_winner_rest is computed from the votes now, so there is no flag
        # to set. Deterministic tie-break: most votes, then the lowest id.
        # Without it the winner depended on database order, which is not stable.
        voted = restaurants.filtered(lambda r: r.line_ids)
        if not voted:
            return
        winner = max(voted, key=lambda r: (len(r.line_ids), -r.id))

        self.add_to_winner_history(winner)
        return {"type": "ir.actions.client", "tag": "reload"}

    @api.depends('daily_winner_rest')
    def _compute_show_take_away_button(self):
        for record in self:
            record.show_take_away_button = record.daily_winner_rest

    # ------------------------------------------------------------------
    # Ratings
    # ------------------------------------------------------------------
    @api.depends('visit_ids.rating')
    def _compute_ratings(self):
        """Average and count of our own ratings.

        A restaurant without visits gets 0.0 and 0, never False: the list view
        sorts on the average, and NULL does not sort like a number.
        """
        for record in self:
            ratings = [int(rating) for rating in record.visit_ids.mapped('rating') if rating]
            record.our_rating_count = len(ratings)
            record.our_rating_avg = sum(ratings) / len(ratings) if ratings else 0.0

    @api.depends('visit_ids')
    def _compute_visits(self):
        for record in self:
            record.our_visit_count = len(record.visit_ids)

    def action_rate_today(self, rating=None):
        """Rate today's lunch here, from a button on the row.

        Creates or updates this user's visit for today, so the button is
        idempotent: clicking "4" twice leaves one visit with rating 4, and
        clicking "5" afterwards changes it to 5.
        """
        self.ensure_one()
        self.env["lunch.visit"].rate(self, rating)
        return {"type": "ir.actions.client", "tag": "reload"}


    @api.model
    def add_to_winner_history(self, winner=None):
        """Write today's winner to the history.

        Was decorated with @api.depends but is not a compute — it creates
        records. It also looped over search([]) instead of working on the
        winner, so calling it on a recordset of 47 restaurants with one winner
        would have written 47 history rows for the same winner.
        """
        if winner is None:
            winner = self._todays_winner()
        if winner:
            self.env["lunch.choice.winner.history"].create({"winner_id": winner.id})

    @api.model
    def _todays_winner(self):
        voted = self.search([]).filtered(lambda r: r.line_ids)
        return max(voted, key=lambda r: (len(r.line_ids), -r.id)) if voted else None

