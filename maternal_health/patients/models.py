from django.db import models

# 
class Patient(models.Model):
    user = models.OneToOneField('users.CustomUser', on_delete=models.CASCADE)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    medical_record_number = models.CharField(max_length=30, unique=True, db_index=True)
    date_of_birth = models.DateField(null=True, blank=True)
    address = models.TextField()
    marital_status = models.CharField(max_length=15)
    national_id = models.CharField(max_length=30, unique=True, db_index=True)
    phone_number = models.CharField(max_length=20, db_index=True)
    educational_level = models.CharField(max_length=50)
    occupation = models.CharField(max_length=50)
    gravidity = models.PositiveSmallIntegerField(default=0)  # total number of times a woman has been pregnant
    parity = models.PositiveSmallIntegerField(default=0)  # number of pregnancies reaching viable gestational age
    communication_language = models.CharField(max_length=30)

    class Meta:
        indexes = [
            models.Index(fields=['medical_record_number']),
            models.Index(fields=['national_id']),
            models.Index(fields=['phone_number']),
            models.Index(fields=['last_name', 'first_name']),
            models.Index(fields=['date_of_birth']),
        ]
    @property
    def age(self):
        if self.date_of_birth:
            today = models.DateField().today()
            age = today.year - self.date_of_birth.year - ((today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))
            return age
        return None

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.national_id}"
