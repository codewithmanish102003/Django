from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    name = models.CharField(max_length=100, blank=True, default='')
    email = models.EmailField(blank=True, default='')
    bio = models.TextField(blank=True, default='')
    skills = models.CharField(max_length=255, blank=True, default='', help_text="Comma separated skills")
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    def __str__(self):
        return f"{self.name or self.user.username}'s Profile"

    @property
    def get_skills_list(self):
        """Return skills as a list"""
        if self.skills:
            return [skill.strip() for skill in self.skills.split(',')]
        return []

    class Meta:
        ordering = ['-created_at']

# Signal to create/update UserProfile when User is created/updated
@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(
            user=instance,
            email=instance.email,
            name=f"{instance.first_name} {instance.last_name}".strip() or instance.username
        )
    else:
        # Update email in profile if user's email changes
        profile, created = UserProfile.objects.get_or_create(user=instance)
        if not created and profile.email != instance.email:
            profile.email = instance.email
            profile.save()