import os
import sys
import argparse
import json
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

SCOPES = ['https://www.googleapis.com/auth/youtube.upload']

def get_authenticated_service():
    """Handles the OAuth2 flow, reusing tokens or buidling a new permanent one."""
    creds = None
    token_path = os.path.join('data','token.json')
    client_secret_path = os.path.join('data', 'client_secret.json')

    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("Refreshing expired access token...")
            creds.refresh(Request())
        else:
            if not os.path.exists(client_secret_path):
                print(f"FATAL: Client secret file not found at: {client_secret_path}")
                print("Make sure you downloaded the JSON from Google Cloud and renamed it correctly.")
                sys.exit(1)

            print("Launching browser for Google authentication...")
            flow = InstalledAppFlow.from_client_secrets_file(client_secret_path, SCOPES)
            creds = flow.run_local_server(port=0)
        
        with open(token_path, 'w') as token:
            token.write(creds.to_json())
            print(f"Permanent non-expiring token saved to {token_path}")
    return build('youtube', 'v3', credentials=creds)

def upload_video(youtube, video_path, privacy_status):
    """Performs resumable, chunked video upload to the linked YouTube channel."""
    if not os.path.exists(video_path):
        print(f"FATAL: Target video file not found at: {video_path}")
        sys.exit(1)
    
    title = "Tech Discovery Series"
    description = "Automated tech short exploring novel engineering concepts. #shorts #tech"
    tags = ["shorts", "tech", "automation"]

    metadata_path = os.path.join('data', 'metadata.json')
    if os.path.exists(metadata_path):
        try:
            with open(metadata_path, 'r') as f:
                meta_data = json.load(f)
                title = meta_data.get('title',title)
                description = meta_data.get('description', description)
                tags = meta_data.get('tags',tags)
            print("Successfully parsed dynamic metadata from data/metadata.json")
        except Exception as e:
            print(f"Warning: Could not parse metadata.json ({e}). Defaulting metadata.")
    
    body = {
        'snippet' : {
            'title' : title,
            'description': description,
            'tags': tags,
            'category': '28'
        },
        'status' : {
            'privacyStatus': privacy_status,
            'selfDeclaredMadeForKids': False
        }
    }

    print(f"Initiating chunked upload stream for: {video_path}")

    media = MediaFileUpload(video_path, chunksize=1024*1024, resumable=True, mimetype='video/mp4')
    request = youtube.videos().insert(
        part=','.join(body.keys()),
        body=body,
        media_body=media
    )

    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"Upload Verification Progress: {int(status.progress() * 100)}%")
    print("\n VIDEO DISPATCHED SUCCESSFULLY!")
    print(f"YouTube Video ID: {response['id']}")
    print(f"Public Short URL: https://youtu.be/{response['id']}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='YouTube Video Uploader Agent Interface')
    parser.add_argument('--privacy', default='private', choices=['public', 'private', 'unlisted'],
                        help='Privacy state configuration (default: private)')
    parser.add_argument('--video', default=os.path.join('output', 'final_short.mp4'),
                        help='Path configuration to targeted mp4 file asset')
    args = parser.parse_args()

    try:
        youtube_service = get_authenticated_service()
        upload_video(youtube_service, args.video, args.privacy)
    except HttpError as e:
        print(f"❌ API Network Exception Encountered: {e.resp.status} - {e.content}")
    except Exception as e:
        print(f"❌ System Exception Encountered: {e}")