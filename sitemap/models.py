from django.db import models

class Node(models.Model):
    nodeId = models.PositiveIntegerField(primary_key=True)
    nodeType = models.PositiveSmallIntegerField()
    korName = models.CharField(max_length=20)
    latitude = models.FloatField()
    longitude = models.FloatField()
    linkedNode = models.JSONField()

    def __str__(self):
        return self.korName

    class Meta:
        db_table = "node_information"

class Edge(models.Model):
    edgeId = models.PositiveIntegerField(primary_key=True)
    fnodeId = models.PositiveIntegerField()
    enodeId = models.PositiveIntegerField()
    korName = models.CharField(max_length=20)
    roadLength = models.PositiveSmallIntegerField()

    class Meta:
        db_table = "edge_information"