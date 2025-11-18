import requests

BASE_API_URL = 'http://localhost:5000/'

DATA = [
    # TEACHER USERS
    {
        "user_details": {"name": "A", "email_id": "A@a.com", "role": "teacher", "password": "testABC12@"},
        "course_details": [
            
            {
                "course_id": "CS725",
                "course_name": "Foundations of Machine Learning",
                "course_level": "Postgraduate",
                "course_objectives": "Supervised learning: decision trees, nearest neighbor classifiers, generative classifiers like naive Bayes, linear discriminate analysis, loss regularization framework for classification, Support vector Machines. Regression methods: least-square regression, kernel regression, regression trees. Unsupervised learning: k-means, hierarchical, EM, non-negative matrix factorization, rate distortion theory.", 
                "offered_at": "Fall_2025"
            },
            
            {
                "course_id": "CS747",
                "course_name": "Foundation of Intelligent Learning Agents",
                "course_level": "Postgraduate",
                "course_objectives": "Agency, intelligence, and learning. Exploration and multi-armed bandits. Markov Decision Problems and planning. Reinforcement learning. Search. Multi-agent systems and multi-agent learning. Case studies",
                "offered_at": "Fall_2025"
            },

            {
                "course_id": "G9PHY",
                "course_name": "Grade 9 Physics",
                "course_level": "Grade 9",
                "course_objectives": "Motion, Force and Laws of Motion, Gravitation, Work and Energy, Sound, Behaviour of Light, Reflection and Refraction, Heat, Energy Conservation, Pressure in Fluids, Buoyancy.",
                "offered_at": "2025"
            }
        ]
    },

    {
        "user_details": {"name": "B", "email_id": "B@a.com", "role": "teacher", "password": "testXYZ34$"},
        "course_details": [
            {
                "course_id": "CS699",
                "course_name": "Software Lab",
                "course_level": "Postgraduate",
                "course_objectives": "Vim/emacs, HTML, CSS. Preparing reports and presentations using latex, beamer, drawing software (e.g. inkscape, xfig, open-office), and graph plotting software (e.g., pyplot, gnuplot). Unix basics: shell, file system, permissions, process hierarchy, process monitoring, ssh, rsync. Unix tools: e.g. awk, sed, grep, find, head, tail, tar, cut, sort, Bash scripting: I/O redirection, pipes. Programming using scripting language (e.g. python).",
                "offered_at": "Fall_2025"
            },

            {
                "course_id": "CS601",
                "course_name": "Algorithms and Complexity",
                "course_level": "Postgraduate",
                "course_objectives": "Techniques for the Design and Analysis of Algorithms. Formal models of computation, time and space complexity, Theory of NP-Completeness, Approximability of NP-Hard problems. Introduction to parallel, randomized and on-line algorithms.",
                "offered_at": "Fall_2025"
            },

            {
                "course_id": "G4ENG",
                "course_name": "Grade 4 English",
                "course_level": "Grade 4",
                "course_objectives": "Parts of Speech (Nouns, Pronouns, Verbs, Adjectives, Adverbs, Prepositions), Tenses (Simple Present, Past, Future), Sentence Types and Structure, Punctuation (Full stop, Comma, Question mark, Exclamation mark, Apostrophe), Synonyms and Antonyms, Homophones/Homonyms, Prefixes and Suffixes, Singular-Plural, Gender, Articles (a/an/the), Subject-Verb Agreement, Paragraph Writing, Letter Writing (Informal), Story Writing, Picture Composition, Comprehension Passages, Poem Appreciation, Notice Writing, Message Writing, Dictionary Skills, Proverbs, Idioms, Active-Passive Voice (introduction), Direct-Indirect Speech (basic), Conjunctions, Degrees of Comparison, Spelling Rules, Vocabulary Building.",
                "offered_at": "2025"
            }
        ]
    },
    
    # STUDENT USERS
    
    # ADMIN USERS
    {
        "user_details": {"name": "Anurag", "email_id": "anuragborkar@cse.iitb.ac.in", "role": "admin", "password": "testOPM99&"}
    },
    {
        "user_details": {"name": "Aniket", "email_id": "aniketw@cse.iitb.ac.in", "role": "admin", "password": "testAOT13&"}
    },
    {
        "user_details": {"name": "Ninad", "email_id": "parikhninad@cse.iitb.ac.in", "role": "student", "password": "testJJK18&"}
    }
]

def register_user(user_details):
    url = BASE_API_URL + "auth/register"
    response = requests.post(url, json=user_details)
    return response.json() if response.status_code == 201 else None

def login_user(user_details):
    url = BASE_API_URL + "auth/login"
    response = requests.post(url, json={
        "email_id": user_details["email_id"],
        "password": user_details["password"]
    })
    return response.json()['access_token'] if response.status_code == 200 else None

def register_course(user, course_details, token):
    url = BASE_API_URL + "teacher/register_course"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(url, json=course_details, headers=headers)

for user in DATA:
    user_details = user["user_details"]
    user_register_response = register_user(user_details)

    if user_register_response:
        print(f"Registered the user {user_details["name"]}")
        token = login_user(user_details)
        print(f"{user_details["name"]} has logged in")

        if token and user_details['role'] == 'teacher':
            for course in user["course_details"]:
                register_course(user_details, course, token)
                print(f"Registered course {course["course_id"]}")