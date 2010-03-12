from django.db import models

# Create your models here.
class Base(models.Model):

    def __repr__(self):
        return u'<%s[%s]: %s>' % ( self.__class__.__name__, self.pk, str(self) )

    class Meta:
        abstract = True