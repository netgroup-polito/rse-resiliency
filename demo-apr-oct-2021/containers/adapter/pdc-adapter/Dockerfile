FROM python:3.8.11-alpine3.13

COPY src /adapter

RUN pip install -r /adapter/requirements.txt

ENTRYPOINT ["python", "/adapter/pdc_adapter.py"]
CMD ["1", "2"]
