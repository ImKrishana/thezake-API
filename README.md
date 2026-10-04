**Lightweight API that fetches POSTERS from TMDB, IMDb, AniList, and multiple OTT(s) platforms, and Bypass DIRECT LINKS from cloud sites.**

## Deployment

<details>
  <summary><strong>Vercel (One-Click Deploy)</strong></summary>

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/ImKrishana/thezake-API)

</details>

<details>
  <summary><strong>Heroku (One-Click Deploy)</strong></summary>

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy?template=https://github.com/ImKrishana/thezake-API/tree/main)

</details>

<details>
  <summary><strong>Render (One-Click Deploy)</strong></summary>

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/ImKrishana/thezake-API&branch=main)

</details>

<details>
  <summary><strong>VPS / Locally (Manual Setup)</strong></summary>

Clone the repository, create a virtual environment, install dependencies, and start the API:

```bash
git clone https://github.com/ImKrishana/thezake-API.git
cd thezake-API
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000
```

On Windows PowerShell, activate the environment with `.venv\Scripts\Activate.ps1` instead of `source .venv/bin/activate`.

Open `http://127.0.0.1:8000` locally, or `http://<your-server-ip>:8000` on a VPS. For production, run the process with a service manager and put it behind a reverse proxy with HTTPS.

</details>

## Extras

**Live Demo:** [Click Here](https://thezakeapi.vercel.app)

**Supported Platforms:** [View Here](https://thezakeapi.vercel.app/supported)

**API Documentation:** [View Here](https://thezakeapi.vercel.app/docs)

U can test all features to see how it works!

<details>
  <summary><strong>Disclaimer</strong></summary>

<br>

This API is developed strictly for **educational and research purposes only**.

This project makes requests to third-party platforms and metadata providers. Their availability, response formats, access rules, and rate limits are outside this API's control.

</details>

[![License](https://img.shields.io/github/license/ImKrishana/thezake-API)](https://github.com/ImKrishana/thezake-API/blob/main/LICENSE)
[![Telegram](https://img.shields.io/badge/Telegram-26A5E4?logo=telegram&logoColor=white)](https://t.me/LeechBots)

**If you like this project, don't forget to give it a Star !**

**Developer:** [The Zake](https://t.me/TheZake)
