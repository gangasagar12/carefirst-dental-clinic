from django.core.management.base import BaseCommand
from django.utils import timezone
from media_center.models import SocialSyncSetting, SocialImportQueue, SocialSyncLog, Video

class Command(BaseCommand):
    help = 'Synchronize videos from connected social media platforms'

    def handle(self, *args, **kwargs):
        self.stdout.write("Starting social media sync process...")
        
        settings = SocialSyncSetting.objects.filter(enable_auto_sync=True)
        if not settings.exists():
            self.stdout.write("No active auto-sync settings found. Exiting.")
            return

        for setting in settings:
            self.stdout.write(f"Syncing platform: {setting.get_platform_display()}")
            try:
                from media_center.models import ConnectedSocialAccount
                account = ConnectedSocialAccount.objects.filter(platform=setting.platform, is_connected=True).first()
                if not account:
                    self.stdout.write(f"No connected account found for {setting.platform}. Skipping.")
                    continue
                
                fetched_videos = self.fetch_from_api(setting.platform, setting.max_videos_to_import, account)
                
                imported_count = 0
                failed_count = 0
                
                for vid_data in fetched_videos:
                    # Check if already imported
                    if not Video.objects.filter(video_id=vid_data['video_id'], platform=setting.platform).exists():
                        try:
                            # 1. Add to import queue
                            queue_item = SocialImportQueue.objects.create(
                                platform=setting.platform,
                                video_id=vid_data['video_id'],
                                title=vid_data['title'],
                                thumbnail=vid_data['thumbnail'],
                                status='pending'
                            )
                            
                            # 2. Directly create video if auto_publish is set
                            Video.objects.create(
                                title=vid_data['title'],
                                platform=setting.platform,
                                video_id=vid_data['video_id'],
                                video_url=vid_data['url'],
                                thumbnail_url=vid_data['thumbnail'],
                                category=setting.default_category,
                                playlist=setting.default_playlist,
                                related_service=setting.default_related_service,
                                related_branch=setting.default_branch,
                                is_published=setting.auto_publish
                            )
                            
                            queue_item.status = 'imported'
                            queue_item.save()
                            imported_count += 1
                        except Exception as e:
                            failed_count += 1
                            self.stderr.write(f"Failed to import video {vid_data['video_id']}: {e}")
                
                # Log success
                SocialSyncLog.objects.create(
                    platform=setting.platform,
                    status='success',
                    imported_videos=imported_count,
                    failed_videos=failed_count
                )
                self.stdout.write(f"Successfully synced {setting.platform}: {imported_count} imported, {failed_count} failed.")

            except Exception as e:
                # Log error
                SocialSyncLog.objects.create(
                    platform=setting.platform,
                    status='error',
                    error_message=str(e)
                )
                self.stderr.write(f"Error syncing {setting.platform}: {e}")

    def fetch_from_api(self, platform, limit, account):
        """
        External API call handler.
        """
        import requests
        
        if platform == 'youtube':
            api_key = account.access_token
            channel_id = account.account_name  # The channel ID is saved here
            
            if not api_key or not channel_id:
                self.stderr.write("Missing YouTube API Key or Channel ID in settings.")
                return []
                
            url = f"https://www.googleapis.com/youtube/v3/search?key={api_key}&channelId={channel_id}&part=snippet,id&order=date&maxResults={limit}"
            try:
                response = requests.get(url)
                data = response.json()
                
                if 'items' not in data:
                    self.stderr.write(f"YouTube API Error: {data}")
                    return []
                    
                videos = []
                for item in data['items']:
                    if item['id'].get('kind') == 'youtube#video':
                        video_id = item['id']['videoId']
                        title = item['snippet']['title']
                        # Try to get high quality thumbnail, fallback to default
                        thumbnails = item['snippet']['thumbnails']
                        thumbnail_url = thumbnails.get('high', thumbnails.get('default', {})).get('url', '')
                        
                        videos.append({
                            'video_id': video_id,
                            'title': title,
                            'url': f"https://www.youtube.com/watch?v={video_id}",
                            'thumbnail': thumbnail_url
                        })
                return videos
            except Exception as e:
                self.stderr.write(f"YouTube API Request failed: {e}")
                return []

        if platform == 'facebook':
            access_token = account.access_token
            page_id = account.account_name  # The Facebook Page ID is saved here
            
            if not access_token or not page_id:
                self.stderr.write("Missing Facebook Access Token or Page ID in settings.")
                return []
                
            # Facebook Graph API v19.0 endpoint for Page Videos
            url = f"https://graph.facebook.com/v19.0/{page_id}/videos?fields=id,title,description,picture,permalink_url&limit={limit}&access_token={access_token}"
            try:
                response = requests.get(url)
                data = response.json()
                
                if 'error' in data:
                    self.stderr.write(f"Facebook API Error: {data['error']}")
                    return []
                    
                videos = []
                for item in data.get('data', []):
                    video_id = item.get('id')
                    # Fallback to description if title is empty
                    title = item.get('title') or item.get('description', '')[:50]
                    permalink = item.get('permalink_url', '')
                    if permalink.startswith('/'):
                        permalink = f"https://www.facebook.com{permalink}"
                    thumbnail_url = item.get('picture', '')
                    
                    videos.append({
                        'video_id': video_id,
                        'title': title or f"Facebook Video {video_id}",
                        'url': permalink,
                        'thumbnail': thumbnail_url
                    })
                return videos
            except Exception as e:
                self.stderr.write(f"Facebook API Request failed: {e}")
                return []
        
        return []
