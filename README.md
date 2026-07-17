# 💰 SIP Calculator Dashboard

A modern, responsive, and interactive **SIP (Systematic Investment Plan) Calculator** — because doing compound-interest math in your head is nobody's idea of a good time. Slide, type, and watch your future wealth (hypothetically) grow in real time. 📈

### 🚀 [Try the Live Demo →](https://srivastav-asutosh.github.io/SIP_Calculator/)

---

## ✨ Features

- 🎚️ **Dual input controls** — editable text fields *and* sliders for amount, years, and expected returns. Type it, drag it, your call.
- ⚡ **Real-time calculations** — updates instantly as you type or slide. No submit button, no waiting around.
- 🍩 **Interactive charts** — a donut chart visualizing invested amount vs. estimated returns, powered by Chart.js.
- 📱 **Responsive design** — looks sharp on desktop, tablet, and mobile.
- 🌗 **Light/Dark mode** — toggle to match your vibe (or your battery-saving habits).
- 🛠️ **Robust backend** — a Flask REST API with validation, error handling, and modular code, ready to plug in when you need server-side calculations.
- 🏗️ **Production-ready** — configured for deployment with Gunicorn, built to scale beyond a weekend project.

## 🧮 How It Works

Under the hood it's the standard SIP compound-growth formula:

```
FV = P × ({[1 + i]^n – 1} / i) × (1 + i)
```

Where `P` is your monthly investment, `i` is the monthly rate of return, and `n` is the total number of months. The dashboard also supports a **Lumpsum** mode for one-time investments.

## 🖥️ Tech Stack

| Layer      | Tech                                  |
|------------|----------------------------------------|
| Frontend   | HTML, CSS, vanilla JS, Chart.js        |
| Backend    | Flask, Flask-CORS, pandas              |
| Deployment | GitHub Pages (static demo), Gunicorn-ready for full-stack hosting |

## 🏃 Running Locally

```bash
cd SIP_Calculator
python -m venv venv
venv\Scripts\activate       # on Windows
pip install -r requirements.txt
python app.py
```

Then open http://localhost:5000 and start crunching numbers.

> **Note:** The [live demo](https://srivastav-asutosh.github.io/SIP_Calculator/) runs the frontend only — all the math happens right in your browser via `app.js`. Run it locally to light up the Flask backend too.

## ⚠️ Disclaimer

This is a demo calculator for illustrative purposes. Returns are indicative, markets are moody, and past performance guarantees nothing. Please consult an actual financial advisor before making real investment decisions. 🙂
