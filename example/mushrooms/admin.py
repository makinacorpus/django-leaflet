from leaflet.admin import LeafletGeoAdmin
from django.contrib import admin

from . import models as mushrooms_models


admin.site.register(mushrooms_models.MushroomSpot, LeafletGeoAdmin)
