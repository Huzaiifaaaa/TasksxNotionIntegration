PATH="/static"

#used to set basic site parameters
#not the best method to do this as it increases vulnerability
#better way to do this is to use environment variables
#but this is a small project so....

#defines the variables which are used in the frontend/views
class frontend:
    def __init__(self):
        self.PATH=PATH #for static files
        self.WEBSITE_NAME="GoogleTasks x Notion"  #for title
        self.URL="http://127.0.0.1:5000"     #for forms URL if any

class backend:
    def __init__(self):
        self.PATH=PATH.split('/')[1] #for static files

        self.AUTO_SYNC_TIME=30  #auto sync interval in seconds
        self.TOKEN_PATH="static/config" #path to store user token
        self.CREDENTIALS_PATH="static/config/credentials.json" #path to store google account credentials

        self.WEB_LOGGING_PATH="Logs/web/" #path to store web logs
        self.SECRET_KEY="sessionSecretKey" #secret key for session
 
        #google tasks api scopes
        self.NOTION_API_KEY="secret_xsQy0SmPWfxc1bF7ohNs2OaYzRblCow7jHxs9Oqikbq"
        self.NOTION_DATABASE_ID="7adad7fdc1714bb4a8b054de85db7481"
        self.GOOGLE_API_CLIENT_ID="369709543904-tnqo9vau8iek5hv04a78io3knjc55pe1.apps.googleusercontent.com"
        self.GOOGLE_API_CLIENT_SECRET="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"


