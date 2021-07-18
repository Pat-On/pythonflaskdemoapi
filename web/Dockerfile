#You may think about it like about the machine build step by step

#Python with linux
FROM python:3
#directory on machine - docker
WORKDIR /usr/src/app
#copy requirments
COPY requirments.txt ./
#installing every dependencies in our case it would be flask and flask_restful
RUN pip install --no-cache-dir -r requirments.txt
#coppying everything
COPY . .
# my test if i can install anything here
RUN pip install -U pip setuptools wheel
RUN pip install -U spacy
RUN python -m spacy download en_core_web_sm
#running app
CMD ["python", "app.py"]