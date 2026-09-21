# Burhanuddin Malik: personal website

One small server that runs three things:

| Address | What it is |
|---|---|
| `/` | The public website (Home, About, Journey, Work, Gallery, Achievements, Blog, Contact) |
| `/admin` | Your private dashboard (you only) |
| `/private` | The read-only portal for viewers you invite (Levels A, B, C) |

Everything you see on the public site is edited from `/admin`. No code needed.

## 1. Put it online

**Easiest path (Render):** put this folder in a GitHub repository, then on render.com choose New, then Blueprint, and pick the repository. `render.yaml` sets everything up and asks you for your `OWNER_PASSWORD`. Any other Docker host works too.

You need a host that runs a Docker app **and keeps a small persistent disk** (so your database and photos survive restarts). Fly.io, Railway and Render (with a disk) all work. Use the `Dockerfile` in this folder, mount the disk at `/data`, and set these settings (environment variables):

| Setting | Value |
|---|---|
| `OWNER_PASSWORD` | a long password you choose (this is your first sign-in) |
| `SECRET_KEY` | any long random text (keeps sign-ins secure) |
| `HTTPS` | `1` |
| `DATA_DIR` | `/data` |

Then open `https://your-site/admin`, sign in as `owner`, and go to **Settings** to add your photographs and your Instagram / WhatsApp / Gmail links.

To try it on your own computer first: `pip install -r requirements.txt`, then `OWNER_PASSWORD=choose-one python app.py`, and open http://localhost:8080.

## 2. First things to do in /admin
1. **Settings**: upload your homepage and About photographs, add your social links.
2. **Projects**: open each project and upload its cover and gallery images. Tick "Show on the homepage" for the four featured ones.
3. **Journey / Achievements**: add photos and any missing details (for example the CorelDRAW certificate).
4. **Blog**: the five starter topics are "Coming soon" placeholders. Write an article, untick "Coming soon", and publish.
5. **Private Archive**: add entries, then choose who can see each one. **Full Details** is for the complete story behind any project or chapter that you don't share publicly.

## 3. Sharing the private archive
Everything you don't want public lives in the **Private Archive** section of `/admin`. People see it at `/private`. There are two ways to let them in:

* **Shared access password (simplest).** In **Viewers & Permissions**, create an access password for a group, for example "Family". Choose a level (A, B or C) and tick which sections that password can open, then send them the password and the `/private` address. They type the password and nothing else. Use a separate password for each group. You can change permissions, change the password, or switch one off at any time, and everyone signed in with it is signed out straight away. Sign-ins last 3 days.
* **Personal accounts (optional).** Give a person their own username and password if you want to see who signed in.

Every entry also has its own "who can see it" setting (all viewers, Levels A and B, Level A only, or owner only). **Full Details** is for the complete story behind any project or chapter. Use **Preview** next to a password or level to see exactly what it opens. Viewers can only read.

## 4. Backups
The server makes a **daily** and a **weekly** backup by itself (database plus every uploaded file). In **Backups** you can back up now, download any backup, or restore one. Restoring needs your password, the word RESTORE, and it first saves a safety copy of the current site.

A backup on the same server doesn't protect you if the server is lost. So either download a backup regularly, or set up automatic copies to outside storage by adding `boto3` to `requirements.txt` and setting `BACKUP_S3_BUCKET` (and `BACKUP_S3_ENDPOINT` for non-Amazon storage such as Cloudflare R2 or Backblaze B2), plus that provider's access keys as `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY`.

## 5. Good to know
* **Contact messages** are stored in the dashboard (Messages). They are not emailed to you.
* **Analytics** uses no cookies and stores no IP addresses. Share links like `https://your-site/?src=instagram` so visits from Instagram or WhatsApp apps are counted under the right source.
* Sign-in is rate-limited, writes are protected against forged requests, uploads are checked, and private files are only served to people allowed to see them.
* Keep the app on **one** worker (the Dockerfile already does) because it uses a small SQLite database.
