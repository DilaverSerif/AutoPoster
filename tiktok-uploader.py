from tiktok_uploader.upload import upload_videos
from tiktok_uploader.auth import AuthBackend
import datetime

auth = AuthBackend(cookies='cookies.txt')

videos = [
  {
    'video': 'clip1.mp4',
    'description': '#foryoumerhaba @dilaver620',
    'comment': True,
    'duet': False,
    'stitch': True,
  },

]

fails = upload_videos(videos=videos, auth=auth)
print("Başarısız videolar:", [v['video'] for v in fails])
