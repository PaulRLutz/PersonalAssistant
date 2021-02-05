from django.db import models

# Create your models here.

class Hub(models.Model):
  name = models.CharField(max_length=200)

class Device(models.Model):
  name = models.CharField(max_length=200)
  hub = models.ForeignKey(Hub, on_delete=models.PROTECT)

class IRCommand(models.Model):
  name = models.CharField(max_length=200)
  device = models.ForeignKey(Device, on_delete=models.PROTECT)

  value = models.CharField(max_length=100)
  bits = models.IntegerField(default=0)
  brand = models.CharField(max_length=30)

class RFCommand(models.Model):
  name = models.CharField(max_length=200)
  device = models.ForeignKey(Device, on_delete=models.PROTECT)

  send_type = models.CharField(max_length=20)
  send_data = models.CharField(max_length=100)
  pulse_length = models.IntegerField(default=0)


