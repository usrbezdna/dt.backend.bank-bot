# Python image based on apline
FROM python:3.10.10-alpine3.17 as base

# sys.stdout и sys.stderr will be unbuffered
ENV PYTHONUNBUFFERED 1
# .pyc files will be absent
ENV PYTHONDONTWRITEBYTECODE 1
WORKDIR /backend

# Installing pipenv and exporting dep. to req.txt file

# NOTE: I don't want to store req.txt file in init repo,
# cause I'll have to regenerate it manually on every addition
# done with `pipenv install <package>`. 
# So instead, I will always have latest req.txt on this 
# stage and pass it to the next one.  

FROM base as pipenv-dep

COPY Pipfile Pipfile.lock ./
RUN pip install pipenv --no-cache-dir && \
    pipenv requirements > req.txt


# Starting app stage
FROM base as runtime

COPY --from=pipenv-dep /backend/req.txt ./req.txt
COPY Makefile shell .env ./

RUN chmod +x docker-entry.sh && \
    apk add --no-cache make bash  && \
    pip install --no-cache-dir -r ./req.txt

COPY src src

CMD [ "sh", "docker-entry.sh" ]