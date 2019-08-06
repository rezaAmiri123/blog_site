# start from an official image
FROM python:3.7-slim

# arbitrary location choice: you can change the directory
RUN mkdir -p /opt/services/djangoapp/src
WORKDIR /opt/services/djangoapp/src

# copy our project code
COPY . /opt/services/djangoapp/src

# install django app requirements
RUN pip install -r requirements.txt

# expose the port 8000
EXPOSE 8000

# define the default command to run when starting the container
# CMD ["gunicorn", "--chdir", "project", "--bind", ":8000", "config.wsgi:application"]

