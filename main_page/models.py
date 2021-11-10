from django.db import models

# Create your models here.
class AD_LIST(models.Model):
    ad_url = models.CharField(max_length=300)
    ad_name = models.CharField(max_length=100)
    name = models.CharField(max_length=100)
    main_key_word = models.CharField(max_length=100)
    tag1 = models.CharField(max_length=100)
    tag2 = models.CharField(max_length=100)
    tag3 = models.CharField(max_length=100)
    tag4 = models.CharField(max_length=100, blank=True)
    tmp = models.CharField(max_length=100, blank=True)
    weight = models.FloatField(default=0)
    call_count = models.IntegerField(default=0)
    feedback_value = models.IntegerField(default=0)
    pub_date = models.DateTimeField('date published')

    def __str__(self):
        return self.ad_url
