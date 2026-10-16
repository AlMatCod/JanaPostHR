# Snalma AI 
# made #34 team

# Временно заглушка

import random

result=""
user=""



def chat(user):
    answers=["Да!","Это отличная идея","Извините я вас непонял",f"Хотите больше узнать об {user}?"]
    result=random.choice(answers)
    return result;
print(chat("Hello!"))   