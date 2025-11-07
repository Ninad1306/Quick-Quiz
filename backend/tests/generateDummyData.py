import requests

BASE_API_URL = 'http://localhost:5000/'

DATA = [
    # TEACHER USERS
    {
        "user_details": {"name": "A", "email_id": "A@a.com", "role": "teacher", "password": "testABC12@"},
        "course_details": [
            {"course_id": "CS725", "course_name": "FML", "course_level": "Postgraduate", "course_objectives": "", "offered_at": "Fall_2025"},
            {"course_id": "CS747", "course_name": "FILA", "course_level": "Postgraduate", "course_objectives": "", "offered_at": "Fall_2025"}
        ]
    },

    {
        "user_details": {"name": "B", "email_id": "B@a.com", "role": "teacher", "password": "testXYZ34$"},
        "course_details": [
            {"course_id": "CS699", "course_name": "SL", "course_level": "Postgraduate", "course_objectives": "", "offered_at": "Fall_2025"},
            {"course_id": "CS791", "course_name": "PFAI", "course_level": "Postgraduate", "course_objectives": "", "offered_at": "Fall_2025"},
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