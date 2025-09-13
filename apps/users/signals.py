from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from allauth.socialaccount.models import SocialAccount
from .models import Profile
import requests
import os
from django.core.files.base import ContentFile
from django.conf import settings


@receiver(post_save, sender=SocialAccount)
def create_or_update_google_user_profile(sender, instance, created, **kwargs):
    """
    当Google用户登录时，自动创建或更新用户资料
    """
    if instance.provider == 'google':
        user = instance.user
        extra_data = instance.extra_data
        
        # 获取或创建用户Profile
        profile, profile_created = Profile.objects.get_or_create(user=user)
        
        # 更新用户基本信息
        if extra_data.get('email') and not user.email:
            user.email = extra_data.get('email')
        
        if extra_data.get('name') and not user.first_name:
            user.first_name = extra_data.get('given_name', '')
            user.last_name = extra_data.get('family_name', '')
        
        if extra_data.get('name') and not user.username:
            # 使用Google用户名作为Django用户名
            user.username = extra_data.get('name', f"google_user_{user.id}")
        
        user.save()
        
        # 下载并设置Google头像
        if extra_data.get('picture') and not profile.avatar:
            try:
                # 下载Google头像
                response = requests.get(extra_data['picture'], timeout=10)
                if response.status_code == 200:
                    # 生成文件名
                    avatar_filename = f"google_avatar_{user.id}.jpg"
                    
                    # 保存头像到Profile
                    profile.avatar.save(
                        avatar_filename,
                        ContentFile(response.content),
                        save=True
                    )
                    print(f"✅ 已为Google用户 {user.username} 下载头像")
                else:
                    print(f"❌ 下载Google头像失败: HTTP {response.status_code}")
            except Exception as e:
                print(f"❌ 下载Google头像异常: {e}")
        
        # 更新Profile的其他信息
        if not profile.bio:
            profile.bio = f"通过Google账户登录的用户"
        
        profile.save()
        
        print(f"✅ Google用户资料已更新: {user.username} ({user.email})")


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    当新用户创建时，自动创建Profile
    """
    if created:
        Profile.objects.get_or_create(user=instance)
        print(f"✅ 已为新用户创建Profile: {instance.username}")