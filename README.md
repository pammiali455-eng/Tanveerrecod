# 📺 M3U Recorder Bot

A **Telegram Bot** to record M3U8 (or M3U) streams, manage recordings, and deliver them directly in Telegram. This README is a complete reference for **admins**, **users**, and developers: configuration, commands (with detailed parameter explanations), deployment, M3U → JSON conversion, troubleshooting and examples.

---

## 🔎 Table of Contents

1. [Features](#features)
2. [Configuration (`config.py`)](#configuration-configpy--full-breakdown)
3. [Commands (User + Admin)](#commands-user--admin--detailed)
4. [M3U → JSON Converter](#m3u---json-converter-in-repo)
5. [Deployment](#deployment-full-details)
6. [Troubleshooting & FAQ](#troubleshooting--faq)
7. [Security & Notes](#security--notes)
8. [Credits](#credits)

---

<a name="features"></a>
## 🚀 Features 

<details>
<summary>🎥 Recording Features</summary>

- Record from **M3U8** URLs or from a **predefined channel list (JSON)** stored in `M3U8_FILES_DIRECTORY`.
- Support for both direct `m3u8` stream URLs and HLS playlists.
- On setup, choose **video track** and then one or more **audio tracks** to include in the final file.
- Live **progress updates**: percentage, ETA, file size, and cancel button.
- **Splits** files larger than the configured max (keeps parts under Telegram's upload limit — ~2GB per file). The bot names parts with `_part1`, `_part2`, etc.
- Generates a thumbnail for the recorded file and writes basic metadata (duration, resolution).
- Uses `ffprobe` for stream inspection; falls back to parsing if `ffprobe` fails.
- Robust `ffmpeg` invocation: supports supplying HTTP headers such as Referer and User-Agent when required by certain streams.
- Graceful cancellation: if a user cancels a running recording, `ffmpeg` is signalled to stop, partial files cleaned up (or optionally kept if configured).

</details>

<details>
<summary>👤 User Features</summary>

- Tiered access control:
  - **Default** users — limited recording duration & parallel tasks.
  - **Verified** users — verified via shortlink provider and get medium limits.
  - **Premium** users — higher limits & longer recording durations granted by admins.
- Commands for interacting with the bot: `/rec`, `/mytasks`, `/cancel`, `/status`, `/verify`, `/search`, `/channel`.
- Interactive prompts for selecting audio/video streams when necessary.
- Progress messages with inline buttons to cancel or open file links when uploaded.

</details>

<details>
<summary>🛠 Admin Features </summary>

- Grant/revoke premium access (short-lived) with `/auth` and `/deauth`.
- Add or remove **admin** accounts which can execute restricted commands.
- Add channel lists (JSON) and remove them; supports file upload (reply to `.json` file) and inline add mode.
- Export bot data (channel lists, premium users, admin users, log files) via `/pull`.
- Inspect FFmpeg logs per task with `/flog`.
- Paginated admin view of all active tasks with `/tasks` and administrative controls (force-cancel, restart, requeue).
- Admin interactive panel with `/admin_panel` for quick maintenance.

</details>

---

<a name="configuration-configpy--full-breakdown"></a>
## 📋 Configuration (`config.py`) — full breakdown
<details>
<summary>Configuration</summary>
**Tip:** Use environment variables in production. `config.py` loads from the environment when values are present.

| Variable | Type | Purpose / Where used | Example |
|---|---:|---|---|
| `API_ID` | int | Telegram API ID — required by Pyrogram to create a client. | `12345678` |
| `API_HASH` | str | Telegram API Hash — paired with API_ID for authentication. | `abcd1234efgh5678` |
| `BOT_TOKEN` | str | Bot token from BotFather used to run the bot. | `1234:ABCdefGHIjkl` |
| `OWNER_ID` | int | Owner user ID — always has full permissions & bypasses some checks. | `987654321` |
| `MONGO_URI` | str | MongoDB connection string — used for storing premium users, verification tokens, admins and task metadata. | `mongodb+srv://user:pw@cluster...` |
| `M3U8_FILES_DIRECTORY` | str | Directory where JSON channel lists live. Bot loads all `*.json` files from here on startup and on reload. | `./m3u8_channels` |
| `WORKING_GROUP` | int | Primary group id used for verification messages or admin posts. | `-1001234567890` |
| `TIMEZONE` | str | Timezone used to format timestamps in responses like `/status`. | `Asia/Kolkata` |
| `GROUP_LINK` | str | Invite link used in messages to point users to the official support group. | `https://t.me/yourgroup` |
| `NUM_WORKERS` | int | Number of concurrent recording workers (per bot instance). Increase on high-resource machines. | `4` |
| `GLOBAL_MAX_PARALLEL_TASKS` | int | Absolute cap of parallel recordings across all users to protect CPU/bandwidth. | `10` |
| `FFPROBE_TIMEOUT` | int | Timeout (seconds) for probing streams with `ffprobe`. | `30` |
| `PREMIUM_MAX_DURATION_SEC` | int | Maximum recording duration (seconds) allowed for premium users. Example: `7200` (2 hours). | `7200` |
| `PREMIUM_PARALLEL_TASKS` | int | Max parallel recordings allowed per premium user. | `2` |
| `VERIFIED_MAX_DURATION_SEC` | int | Max duration for verified users (seconds). | `2700` |
| `VERIFIED_PARALLEL_TASKS` | int | Max parallel recordings for verified users. | `2` |
| `ENABLE_SHORTLINK` | bool | Toggle shortlink verification on/off. If `false`, `/verify` is disabled. | `true` |
| `VERIFICATION_EXPIRY_SECONDS` | int | How long verification remains valid (seconds). | `14400` |
| `SHORTLINK_URL` | str | Shortlink provider base URL used to create verification links (optional). | `https://vplink.in` |
| `SHORTLINK_API` | str | API key for shortlink service (optional). | `xxx-yyy-zzz` |
| `STATUS_PAGE_SIZE` | int | How many tasks to show per page for `/tasks` pagination. | `10` |
| `PROGRESS_UPDATE_INTERVAL` | int | Interval (seconds) between progress message edits to reduce Telegram API calls. | `60` |

**Note on durations and `config.py` values**
- Numeric durations in `config.py` are stored as seconds. Admin commands like `/auth` accept human-friendly durations such as `30d`, `48h` or `12h` and the bot converts those to seconds.
- Keep `NUM_WORKERS` aligned with your server CPU, disk I/O and network bandwidth. Too many workers can saturate the machine and cause failed recordings.
</details>

---

<a name="commands-user--admin--detailed"></a>
## 💬 Commands — Full Reference, parameters, examples & behavior
<details>
<summary>COMMANDS</summary>
  
This section contains **detailed** behavior for each user and admin command. It explains optional parameters like `.L#`, `<task_id>`, `[m3u8|log|premium|admin]`, and duration formats.

> **Quick reminder:** When passing arguments that contain spaces (like channel names), wrap them in quotes: `"Channel Name"`.

### 👤 User Commands (detailed)

<details>
<summary>📝 /start</summary>

- **Usage:** `/start` or `/start verify_<token>`
- **Behavior:** Sends welcome message, shows quick help, and handles deeplink verification if `verify_` token is present.

</details>

<details>
<summary>❓ /help</summary>

- **Usage:** `/help`
- **Behavior:** Shows list of user commands and examples. Admins will see additional admin commands.

</details>

<details>
<summary>📊 /status</summary>

- **Usage:** `/status`
- **Behavior:** Shows current tier (Owner/Admin/Premium/Verified/Default), limits (max duration, parallel tasks) and premium expiry if applicable.

</details>

<details>
<summary>🎥 /rec "[URL/Channel]" [HH:MM:SS] [Optional Filename] [.L#]</summary>

- **Usage examples:**
  - `/rec "https://example.com/stream.m3u8" 00:10:00 "My Clip"`
  - `/rec "Disney Channel (4K)" 00:30:00 "Kids" .L1`
- **Parameters:**
  - `"[URL/Channel]"` — Either a direct M3U8 URL **or** the key/name of a channel contained in one of your `*.json` lists.
  - `[HH:MM:SS]` — Duration. Accepts `HH:MM:SS` or `MM:SS` formats. Plain seconds (e.g., `600`) are also accepted.
  - `[Optional Filename]` — Quoted filename used for the final Telegram-uploaded video.
  - `[.L#]` — Optional list selector. The bot sorts JSON list filenames alphabetically; `.L1` selects the first list, `.L2` the second, etc.
- **Behavior:** If channel name is provided, bot searches the chosen lists for a matching key; if a URL is given, it uses it directly. The bot may prompt to select video/audio tracks and then queues the job. A `task_id` is returned.

</details>

<details>
<summary>📋 /mytasks</summary>

- **Usage:** `/mytasks`
- **Behavior:** Shows your active and queued tasks (with short `task_id` and status). Inline buttons provide 'Cancel' actions.

</details>

<details>
<summary>❌ /cancel <task_id></summary>

- **Usage:** `/cancel` or `/cancel <task_id>`
- **Behavior:** If no `task_id` is provided, the bot lists your active tasks with cancel buttons. If `task_id` is provided and you own the job (or are admin), it cancels the job.
  - For queued jobs: removed from queue.
  - For running jobs: sends signal to `ffmpeg` to stop and attempts to remove temporary files.

</details>

<details>
<summary>📺 /channel</summary>

- **Usage:** `/channel`
- **Behavior:** Interactive browsing of loaded JSON lists and channels. Select a channel to quickly call `/rec` with it.

</details>

<details>
<summary>🔍 /search <query></summary>

- **💡 Usage:**
  - `/search "Disney"` — searches **all** loaded lists for `Disney`.
  - `/search "Disney India" .l1` — searches **list 1** only.
  - `/search "Disney SD" .l1 .l3` — searches **lists 1 and 3**.
- **Behavior:** Returns a paginated list of matching channels (name, group, short url) and inline buttons to record or view details.

</details>

<details>
<summary>✅ /verify</summary>

- **Usage:** `/verify`
- **Behavior:** If `ENABLE_SHORTLINK` is true, bot generates a verification link (optionally shortened using `SHORTLINK_URL`). When the link is opened and verified by the service, the user is marked verified for `VERIFICATION_EXPIRY_SECONDS`.

</details>

### 👑 Admin Commands (detailed)

> Admin commands are restricted to admin users saved in DB or to the `OWNER_ID`.

<details>
<summary>👑 /auth <duration> — Grant Premium</summary>

- **Recommended call pattern:** Reply to a user's message with `/auth 30d`.
- **Alternative:** `/auth <user_id> 30d` (some bot builds support this form).
- **`<duration>` formats:** `Nd` (days) or `Nh` (hours). Examples: `30d`, `7d`, `48h`, `12h`.
- **Effect:** Adds or updates an entry in `premium_users` collection with expiry epoch timestamp. Sends DM notification to the user.
- **Example:** Reply to @someuser's msg: `/auth 30d`.

</details>

<details>
<summary>🚫 /deauth — Revoke Premium</summary>

- **Usage:** Reply to a user's message with `/deauth` or `/deauth <user_id>`.
- **Effect:** Removes user from `premium_users` or marks `is_premium=false`. Attempts to notify the user.

</details>

<details>
<summary>📁 /add_m3u8 — Add Channel Lists</summary>

There are multiple modes the bot supports (depending on code):

**💡 Usage:**
1. **File Mode (recommended)** — Upload a `.json` file containing channel list to the bot (in its DM or to the configured `WORKING_GROUP`) and **reply to that file** with `/add_m3u8`.
   - The bot validates the JSON (each key should map to `{ "name":..., "url":..., "Group":... }`).
   - If validation passes, the bot saves the JSON into `M3U8_FILES_DIRECTORY` and reloads lists.

2. **Inline / Individual Link Mode** — Admin can add a single channel entry inline via:
    `/add_m3u8 "json_name.json" "https://example.com/stream.m3u8" "Channel Name" "Group Name"`
   - The bot will create or update `json_name.json` with the new channel entry (slugified key) and save it.

3. **Direct Deployment** — As an alternative, admin can manually place JSON files into the `M3U8_FILES_DIRECTORY` (for example via SFTP/SSH), then use `/admin_panel` or restart bot to load the lists.

**Notes:**
- Filenames are used as list identifiers and determine `.L#` ordering (alphabetical by filename).
- Uploaded JSON must be valid UTF-8 and follow the expected structure.

</details>

<details>
<summary>🗑️ /remove_m3u8 "json_name"</summary>

- **Usage:** `/remove_m3u8 "channels_list.json"` or reply to a file and run `/remove_m3u8`.
- **Behavior:** Removes the JSON file from `M3U8_FILES_DIRECTORY` and reloads the lists.

</details>

<details>
<summary>📤 /pull [m3u8|log|premium|admin]</summary>

- **Usage examples:**
  - `/pull m3u8` — returns a ZIP containing all JSON channel lists.
  - `/pull log` — returns the log file for Current Bot Run.
  - `/pull premium` — returns a List of premium users and expiry timestamps.
  - `/pull admin` — returns JSON list of admin users.
- **Purpose:** Backup or inspect stored bot data.

</details>

<details>
<summary>📄 /flog [file|msg] <task_id></summary>

- **Usage:**
  - `/flog file <task_id>` — send the full log file from `flogs/` if available.
  - `/flog msg <task_id>` — show last ~50 lines of the log in message form (avoids large file uploads).
- **Notes:** Logs are rotated; older logs may be archived or deleted depending on configuration.

</details>

<details>
<summary>📊 /tasks</summary>

- **Usage:** `/tasks`
- **Behavior:** Returns a paginated list of all active and queued tasks across the bot (admins only). Buttons allow page navigation and quick actions (cancel task, view logs).

</details>

<details>
<summary>⚙️ /admin_panel</summary>

- **Usage:** `/admin_panel`
- **Behavior:** Opens an inline control panel for admins — reload lists, quick `/pull`, list premium users, manage workers.

</details>
</details>

---

<a name="m3u---json-converter-in-repo"></a>
## 🗂️ M3U → JSON Converter (in repo)

<details>
<summary>M3U8 To JSON</summary>
  
File included: `M3U To Json.py` — an **interactive GUI** helper that reads `.m3u`/`.m3u8` and outputs a `.json` formatted for the bot.

### What it does
- Reads standard M3U playlists and extracts `#EXTINF` lines and `group-title` attributes if present.
- Maps each channel to a slugified key and produces JSON like:
```json
{
  "dd_tv_hd": { "name": "DD TV HD", "url": "https://.../hd.m3u8", "Group": "News" }
}
```
- Prompts the user for group descriptions for better organization.

### How to run (interactive GUI)
```bash
python "M3U To Json.py"
```
- A file picker opens to choose the `.m3u` file and then a save dialog for `.json`.
- After conversion, move the `.json` into `M3U8_FILES_DIRECTORY` or add it via `/add_m3u8`.

</details>

---

<a name="deployment-full-details"></a>
## 🖥️ Deployment (full details)
<details>
<summary>Deployment Guidelines</summary>
  
> Step-by-step guides for common deployment flows: cloning from Git, manual setup, Ubuntu with `systemd`, and Windows. Each step has clear instructions.

<details>
<summary>🔹 Clone Repository (Recommended)</summary>

**When to use:** Quick start or development.

**Steps:**

1. **Clone the repository**

```bash
git clone https://github.com/shan0174/M3U8-M3U-Recorder-Bot-.git
cd M3U8-M3U-Recorder-Bot-
```

2. **Create and activate virtual environment (optional but recommended)**

```bash
python3 -m venv venv
source venv/bin/activate   # Linux/macOS
# or
python -m venv venv
venv\Scripts\Activate  # Windows PowerShell
```

3. **Install dependencies**

```bash
# Windows
venv\Scripts\python.exe -m pip install --upgrade pip
venv\Scripts\python.exe -m pip install -r requirements.txt

# Linux/macOS
venv/bin/python -m pip install --upgrade pip
venv/bin/python -m pip install -r requirements.txt

```

4. **Prepare configuration**
- Edit `config.py` to set `API_ID`, `API_HASH`, `BOT_TOKEN`, `MONGO_URI`, `M3U8_FILES_DIRECTORY`.
- Or export environment variables.

5. **Add channel lists**
- Copy `*.json` channel files into `M3U8_FILES_DIRECTORY`.

6. **Start the bot**

```bash
python main.py
```

7. **Verify**
- Message your bot `/start` in Telegram and check logs.

8. Video Tutorial

<a href="https://drive.google.com/file/d/1yBVNL7ULqm5h1v47ro1n3_OaeYoPMn1g/preview" target="_blank">
  <img src="https://drive.google.com/uc?export=view&id=1QbJlquCTwgVJUymvBj52s9--fXRubWQJ" 
       alt="Video Thumbnail"
       width="300"
       style="border-radius:15px;">
</a>




</details>

<details>
<summary>🔹 Manual Setup</summary>

**When to use:** You downloaded a ZIP or want to manually install on desktop without virtual environments.

**Steps:**

1. **Download and extract** the repository ZIP file.
2. Open terminal in extracted folder.
3. **Install dependencies**:

```bash
pip install -r requirements.txt
```

4. **Configure**
- Edit `config.py` with `API_ID`, `API_HASH`, `BOT_TOKEN`, `MONGO_URI`, `M3U8_FILES_DIRECTORY`.

5. **Place channel JSON files** into `M3U8_FILES_DIRECTORY`.

6. **Run the bot**

```bash
python main.py
```

7. **Embed video guide**
- Watch the manual setup video here:

<a href="https://drive.google.com/file/d/1OGqR2QzDIX5RhnbHfXfIdVrVvmn2HZn8/preview" target="_blank">
  <img src="https://drive.google.com/uc?export=view&id=16qkAe8WGSk-9GWKzoBv9cZDfH9y1Wzyu" 
       alt="Manual Setup Video"
       width="300"
       style="border-radius:15px;">
</a>




</details>

<details>
<summary>🔹 Ubuntu Deployment with systemd (Production)</summary>

**Steps:**

1. **Prepare server**

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install python3 python3-pip ffmpeg -y
```

2. **Clone & setup**

```bash
git clone https://github.com/your/repo.git
cd repo
pip install -r requirements.txt
```

3. **Configure**
- Set `API_ID`, `API_HASH`, `BOT_TOKEN`, `MONGO_URI` in `.env` or `config.py`.

4. **Create systemd service file** `/etc/systemd/system/m3u-recorder.service`:

```
[Unit]
Description=M3U Recorder Bot
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/m3u-recorder
EnvironmentFile=/home/ubuntu/m3u-recorder/.env
ExecStart=/usr/bin/python3 main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

5. **Enable & start service**

```bash
sudo systemctl daemon-reload
sudo systemctl enable m3u-recorder
sudo systemctl start m3u-recorder
sudo journalctl -u m3u-recorder -f
```

</details>

<details>
<summary>🔹 Windows Quick Run</summary>

**Steps:**

1. **Install Python** and add to PATH.
2. **Install ffmpeg** and add `bin` to PATH.
3. **Install dependencies**

```powershell
pip install -r requirements.txt
```

4. **Configure**
- Edit `config.py` with required credentials.

5. **Place JSON files** into `M3U8_FILES_DIRECTORY`.

6. **Run the bot**

```powershell
python main.py
```

7. **Embed video guide**



</details>
</details>

<a name="troubleshooting--faq"></a>
## ❗ Troubleshooting & FAQ
<details>
<summary>Troubleshooting</summary>

<details>
<summary>FFmpeg not found</summary>

**Symptoms:** `FileNotFoundError: [Errno 2] No such file or directory: 'ffmpeg'` or `ffmpeg: command not found`.

**Fix:**
- Install ffmpeg and ensure it is on PATH.
  - Ubuntu: `sudo apt install ffmpeg`
  - Debian: `sudo apt-get install ffmpeg`
  - Windows: download static build and add `C:\path\to\ffmpeg\bin` to PATH.
- Verify with `ffmpeg -version`.

</details>

<details>
<summary>MongoDB issues (connection, network access)</summary>

**Symptoms:** Bot cannot connect to MongoDB, `ServerSelectionTimeoutError`, or operations fail with authentication errors.

**Checklist & fixes:**
- Double-check `MONGO_URI` for typos and correct username/password.
- If using **MongoDB Atlas**, ensure your cluster's Network Access (IP whitelist) includes the server IP. For public access you may temporarily set `0.0.0.0/0` — **but this is not recommended** in production unless you have strong authentication and firewall rules.
- Confirm the database user has the required roles (readWrite) on the database.
- Try connecting from the server using `mongo` client or `mongosh` to verify connectivity.
- If using SRV connection string (`mongodb+srv://`), ensure DNS SRV lookup works from the host.

</details>

<details>
<summary>Bot cannot post to group</summary>

**Symptoms:** Errors such as `PeerIdInvalid`, `ChatWriteForbidden`, or uploads failing with permission errors.

**Fixes:**
- Ensure the bot was **added to the group**.
- Give the bot permission to send messages and upload media.
- If the group is a supergroup, ensure the chat ID in `WORKING_GROUP` is correct (starts with `-100`).

</details>

<details>
<summary>Recording fails</summary>

**Symptoms:** Recording starts but `ffmpeg` exits with an error; missing segments; file upload fails.

**What to check:**
- Use admin `/flog msg <task_id>` to inspect the last 50 lines of the ffmpeg log.
- If the stream requires HTTP headers or referrer, add those headers where the bot supports them.
- Check network connectivity and stream URL health (try `ffmpeg -i <url>` locally).
- Check disk space and temp directory permissions.

</details>

<details>
<summary>Task stuck / cannot cancel</summary>

**Symptoms:** The UI shows a running task but `ffmpeg` process isn't responding to cancel.

**Fixes:**
- Admin `/cancel <task_id>` should stop it. If not:
  - Inspect running `ffmpeg` processes and kill the appropriate PID.
  - Restart the bot process to clear in-memory state.
- Add health checks and periodic cleanup if tasks frequently become stale.

</details>
</details>

---

<a name="security--notes"></a>
## 🔐 Security & Notes
<details>
<summary>Security</summary>
  
- Always Host bot Privately [Hosting Publicly may slowdown bot, bot might crash at larger file uploads]
- **Do not commit secrets** (`BOT_TOKEN`, `API_HASH`, `MONGO_URI`) into git. Use environment variables or a protected `.env` file stored outside the repo.
- Limit `NUM_WORKERS` based on actual hardware capabilities to avoid resource exhaustion.
- Always keep `ffmpeg` updated to the latest stable build for best compatibility.
- If exposing MongoDB to public networks temporarily (e.g. `0.0.0.0/0`), ensure credentials are strong and prefer restricting IP ranges.
</details>

---

<a name="credits"></a>
## 🙌 Credits
<details>
<summary>Credits</summary>
  
- Built By ***@Shan_0103*** And **@Dora_Toonz** In Telegram.
- Built using **Pyrogram** for Telegram interaction.
- Stream recording powered by **FFmpeg** and **ffprobe**.
- Data persistence via **MongoDB**.
- `M3U To Json.py` is a small utility included in the repo for converting `.m3u` playlists into bot-friendly JSON lists.
</details>

---

