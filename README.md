# Quick-Quiz

GenAI Quiz engine leverages generative AI to instantly generate customized quizzes on any given topic, eliminating the need for manual question creation. Users simply enter a topic, and the AI crafts a full quiz complete with multiple-choice, multiple-select, true/false type questions. 
Beyond simple question generation, the platform integrates an advanced grading and analysis system. After a user completes a quiz, it not only provides a score but also gives detailed feedback on correct and incorrect answers, highlighting areas of strength and weakness.

## Architecture:

<ul>
<li>Backend: Flask
<li>Frontend: Vite+React
<li>DB: SQLite
</ul>

## Installation:

Clone the repository:
```sh
git clone git@github.com:Ninad1306/Quick-Quiz.git
```

Go into the directory:
```sh
cd Quick-Quiz
```

Create Virtual Environment and install Python Dependencies:
```sh
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Install Node dependencies in the frontend directory:
```sh
cd quick-quiz-frontend
npm install
```

## Run locally

Start the frontend using:
```sh
cd quick-quiz-frontend
npm install
npm run dev
```

Start the backend after adding the appropriate API key:
```sh
cd backend
export GEMINI_API_KEY=""
flask --debug --app app run
```

## Deployment

Build the React app:
```sh
cd quick-quiz-frontend
npm install
npm run build
```

Copy over the assets and html:
```sh
cd quick-quiz
mkdir -p backend/app/templates
mkdir -p backend/app/static/assets

cp quick-quiz-frontend/dist/vite.svg backend/app/static/
cp quick-quiz-frontend/dist/index.html backend/app/templates
cp quick-quiz-frontend/dist/assets/* backend/app/static/assets/
```

Create and activate venv:
```sh
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Start the server using gunicorn after adding the appropriate API key:
```sh
sudo GEMINI_API_KEY=<YOUR_GEMINI_API_KEY> ./venv/bin/gunicorn --bind 0.0.0.0:80 --chdir backend app:app
```
