from djgeojson.fields import PolygonField
from django.db import models


class MushroomSpot(models.Model):

    geom = PolygonField()
