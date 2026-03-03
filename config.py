from dotenv import load_dotenv
load_dotenv() 
import os

# --------------------------------------------------------------------------------
# ## TELEGRAM CREDENTIALS ##
# --------------------------------------------------------------------------------
# Get these from https://my.telegram.org
API_ID = int(os.environ.get("API_ID", "12345678"))
API_HASH = os.environ.get("API_HASH", "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")

# Get this from https://t.me/BotFather
BOT_TOKEN = os.environ.get("BOT_TOKEN", "xxxxxxxxxx:xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")

# --------------------------------------------------------------------------------
# ## BOT OWNER & PERMISSIONS ##
# --------------------------------------------------------------------------------
# Your personal user ID. Get via https://t.me/userinfobot
OWNER_ID = int(os.environ.get("OWNER_ID", "7958067256"))

# --------------------------------------------------------------------------------
# ## DATABASE & STORAGE ##
# --------------------------------------------------------------------------------
# Connection string for your MongoDB Atlas database
MONGO_URI = os.environ.get("MONGO_URI", "mongodb+srv://Username:Password@cluster0.a1l08cq.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")

# Directory to store M3U8 channel list (.json) files
M3U8_FILES_DIRECTORY = os.environ.get("M3U8_FILES_DIRECTORY", "./m3u8_channels")

# --------------------------------------------------------------------------------
# ## CORE BOT SETTINGS ##
# --------------------------------------------------------------------------------
# Group where the bot primarily operates and sends notifications
WORKING_GROUP = int(os.environ.get("WORKING_GROUP", "-100xxxxxxxxxx"))

# Timezone for displaying dates and times (e.g., "Asia/Kolkata", "UTC")
TIMEZONE = os.environ.get("TIMEZONE", "Asia/Kolkata")

# Invite link to your group, shown in some messages
GROUP_LINK = os.environ.get("GROUP_LINK", "https://t.me/+xxxxxxxxxx") # **Replace with your actual group link**

# --------------------------------------------------------------------------------
# ## PERFORMANCE & LIMITS ##
# --------------------------------------------------------------------------------
# Number of recordings to process simultaneously (i.e., the number of workers)
NUM_WORKERS = int(os.environ.get("NUM_WORKERS", "4"))

# Global limit: Maximum number of recordings running or queued across ALL users
GLOBAL_MAX_PARALLEL_TASKS = int(os.environ.get("GLOBAL_MAX_PARALLEL_TASKS", "10"))

# Timeout in seconds for fetching stream info with ffprobe
FFPROBE_TIMEOUT = int(os.environ.get("FFPROBE_TIMEOUT", "30"))

# --- User Tier Limits ---
# Premium users
PREMIUM_MAX_DURATION_SEC = 2 * 3600  # 2 hours per task
PREMIUM_PARALLEL_TASKS = 2           # 3 parallel tasks at a time

# Verified users (if shortlink verification is enabled)
VERIFIED_MAX_DURATION_SEC = 45 * 60  # 45 minutes per task
VERIFIED_PARALLEL_TASKS = 2          # 2 parallel tasks at a time

# --------------------------------------------------------------------------------
# ## VERIFICATION SYSTEM ##
# --------------------------------------------------------------------------------
# Set to 'false' to disable the /verify command entirely
ENABLE_SHORTLINK = os.environ.get("ENABLE_SHORTLINK", "true").lower() == "true"
VERIFICATION_EXPIRY_SECONDS = 4 * 60 * 60  # 4 hours

# Your chosen shortlink provider URL and API key
SHORTLINK_URL = os.environ.get("SHORTLINK_URL", "https://vplink.in")
SHORTLINK_API = os.environ.get("SHORTLINK_API", "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")

# --------------------------------------------------------------------------------
# ## DISPLAY SETTINGS ##
# --------------------------------------------------------------------------------
# Number of tasks to display per page in the /tasks command
STATUS_PAGE_SIZE = 10

# --------------------------------------------------------------------------------
# ## PROGRESS MESSAGE UPDATE SETTINGS ##
# --------------------------------------------------------------------------------
# Interval in seconds to update progress messages (recording and uploading).
# A higher value reduces API spam. Recommended: 20-30 seconds.

PROGRESS_UPDATE_INTERVAL = int(os.environ.get("PROGRESS_UPDATE_INTERVAL", "60"))

