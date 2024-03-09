FROM public.ecr.aws/lambda/python:3.11

RUN pwd

COPY requirements.txt ./

RUN python3.11 -m pip install -r requirements.txt -t .

COPY *.py ./
# COPY s3Connect.py ./

# Command can be overwritten by providing a different command in the template directly.
CMD ["assignment1.lambda_handler"]
