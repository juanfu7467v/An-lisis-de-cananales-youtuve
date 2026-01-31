import os
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials

def get_youtube_client():
    creds = Credentials(
        None,
        refresh_token=os.getenv("YOUTUBE_REFRESH_TOKEN"),
        client_id=os.getenv("YOUTUBE_CLIENT_ID"),
        client_secret=os.getenv("YOUTUBE_CLIENT_SECRET"),
        token_uri="https://oauth2.googleapis.com/token"
    )
    return build("youtube", "v3", credentials=creds)

def upload_video(video_path, metadata, publish_at=None):
    """
    Sube un video a YouTube con los metadatos proporcionados.
    Si publish_at está presente, se programa la publicación.
    """
    youtube = get_youtube_client()
    
    body = {
        'snippet': {
            'title': metadata['title'],
            'description': metadata['description'],
            'tags': metadata['tags'],
            'categoryId': '22' # Gente y blogs
        },
        'status': {
            'privacyStatus': 'private' if publish_at else 'public',
            'selfDeclaredMadeForKids': False
        }
    }
    
    if publish_at:
        body['status']['publishAt'] = publish_at.isoformat() + '.000Z'
        body['status']['privacyStatus'] = 'private'

    media = MediaFileUpload(video_path, chunksize=-1, resumable=True)
    
    request = youtube.videos().insert(
        part=','.join(body.keys()),
        body=body,
        media_body=media
    )
    
    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"Subiendo... {int(status.progress() * 100)}%")
            
    return response
