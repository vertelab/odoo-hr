"""Distance helpers for the lunch catalogue.

Plain functions, no Odoo imports. The distance rule belongs to the domain,
not to a model, and keeping it importable on its own means it can be tested
without a database.
"""

import math

# Mean Earth radius in metres. The haversine formula assumes a sphere, so a
# single radius is the whole of the approximation; 6371 km is the IUGG mean.
EARTH_RADIUS_M = 6371000


def haversine(lat1, lon1, lat2, lon2):
    """Great-circle distance between two points, in metres.

    Returns 0.0 when any coordinate is missing, so a restaurant without a
    position is "unknown distance" rather than an exception. Latitude 0 and
    longitude 0 are real values (Gulf of Guinea) and are treated as such.
    """
    if None in (lat1, lon1, lat2, lon2):
        return 0.0

    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    d_phi = math.radians(lat2 - lat1)
    d_lambda = math.radians(lon2 - lon1)

    a = (math.sin(d_phi / 2) ** 2
         + math.cos(phi1) * math.cos(phi2) * math.sin(d_lambda / 2) ** 2)
    # Clamp before asin: floating point can push `a` a hair above 1 for
    # antipodal points, and asin would then raise ValueError.
    a = min(1.0, max(0.0, a))
    return 2 * EARTH_RADIUS_M * math.asin(math.sqrt(a))
