from django.shortcuts import render
from django.conf import settings
import os
import pickle
from django.http import HttpResponse

def covid_prediction(request):
    if request.method == "POST":
        filename = str(os.path.join(settings.BASE_DIR, "features/model/covid.sav"))
        model = pickle.load(open(filename,'rb'))
        cough = int(request.POST['cough'])
        fever = int(request.POST['fever'])
        throat = int(request.POST['throat'])
        breath = int(request.POST['breath'])
        headache = int(request.POST['headache'])
        result = model.predict([[cough, fever, throat, breath, headache]])
        if result == 1:
            msg = "You probably have chances of Covid-19. Consult the doctor immediately."
        else:
            msg = "You don't have symptoms of Covid-19. But Stay Safe and Secure."
        return render(request, 'covid.html', {"msg":msg})
    return render(request, 'covid.html')


import nltk
from nltk.stem import WordNetLemmatizer
import pickle
import numpy as np
import random
import json
from keras.models import load_model
lemmatizer = WordNetLemmatizer()
nltk.download('punkt')
nltk.download('wordnet')


file1 = str(os.path.join(settings.BASE_DIR, "features/model/chatbot_model.h5"))
file2 = str(os.path.join(settings.BASE_DIR, "features/model/intents.json"))
file3 = str(os.path.join(settings.BASE_DIR, "features/model/words.pkl"))
file4 = str(os.path.join(settings.BASE_DIR, "features/model/classes.pkl"))
model = load_model(file1)
intents = json.loads(open(file2).read())
words = pickle.load(open(file3,'rb'))
classes = pickle.load(open(file4,'rb'))

def clean_up_sentence(sentence):
    sentence_words = nltk.word_tokenize(sentence)
    sentence_words = [lemmatizer.lemmatize(word.lower()) for word in sentence_words]
    return sentence_words

def bow(sentence, words, show_details=True):
    sentence_words = clean_up_sentence(sentence)
    bag = [0]*len(words)  
    for s in sentence_words:
        for i,w in enumerate(words):
            if w == s: 
                bag[i] = 1
                if show_details:
                    print ("found in bag: %s" % w)
    return(np.array(bag))

def predict_class(sentence, model):
    p = bow(sentence, words,show_details=False)
    res = model.predict(np.array([p]))[0]
    ERROR_THRESHOLD = 0.25
    results = [[i,r] for i,r in enumerate(res) if r>ERROR_THRESHOLD]
    results.sort(key=lambda x: x[1], reverse=True)
    return_list = []
    for r in results:
        return_list.append({"intent": classes[r[0]], "probability": str(r[1])})
    return return_list

def getResponse(ints, intents_json):
    tag = ints[0]['intent']
    list_of_intents = intents_json['intents']
    for i in list_of_intents:
        if(i['tag']== tag):
            result = random.choice(i['responses'])
            break
    return result

def chatbot_response(msg):
    ints = predict_class(msg, model)
    res = getResponse(ints, intents)
    return res



def chatbot(request):
    try:
        messages = request.session['messages']
    except:
        messages = []
    if request.method == "POST":
        text = request.POST['text']
        res = chatbot_response(text)
        messages.append({"id": len(messages)+1, 'type':'query', "message":text })
        messages.append({"id": len(messages)+1, 'type':'response', "message":res })
        request.session['messages'] = messages
    context = {'messages':messages}
    return render(request, 'chatbot.html', context)
