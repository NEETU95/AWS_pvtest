FROM public.ecr.aws/lambda/python:3.9
COPY . ./
RUN pip install --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host=files.pythonhosted.org -r requirements1.txt
CMD ["main.pdf_extraction"]
