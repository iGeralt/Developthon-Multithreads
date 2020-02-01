import os ,io
import re
from google.cloud import vision
from google.cloud import storage
from google.cloud.vision import types
from google.protobuf import json_format
from PIL import Image
import random
import datetime
"""
gs://som2000/CAHUMB-2019_00016704.TIF -- watermark
gs://som2000/201909190216.TIF -- poor image
gs://som2000/CASACR_2019120401175.tiff -- handwritten
"""

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = r'token.json'
client = vision.ImageAnnotatorClient()

#########################################################################################
val = input("Enter file name: ")
img = Image.open(val)

batch_size = img.n_frames
mime_type = 'image/tiff'
feature = vision.types.Feature(
    type=vision.enums.Feature.Type.DOCUMENT_TEXT_DETECTION)

gcs_source_uri = 'gs://som2000/'+val
gcs_source = vision.types.GcsSource(uri=gcs_source_uri)
input_config = vision.types.InputConfig(gcs_source=gcs_source, mime_type=mime_type)


new_files = datetime.datetime.now()


gcs_destination_uri = 'gs://som2000/output'+str(new_files)
gcs_destination = vision.types.GcsDestination(uri=gcs_destination_uri)
output_config = vision.types.OutputConfig(gcs_destination=gcs_destination, batch_size=batch_size)

async_request = vision.types.AsyncAnnotateFileRequest(
    features=[feature], input_config=input_config, output_config=output_config)

operation = client.async_batch_annotate_files(requests=[async_request])
operation.result(timeout=180)

storage_client = storage.Client()
match = re.match(r'gs://([^/]+)/(.+)', gcs_destination_uri)
bucket_name = match.group(1)
prefix = match.group(2)
bucket = storage_client.get_bucket(bucket_name)

# List object with the given prefix
blob_list = list(bucket.list_blobs(prefix=prefix))
print('Output files:')
"""for blob in blob_list:
    print(blob.name)"""

output = blob_list[0]
json_string = output.download_as_string()
response = json_format.Parse(
            json_string, vision.types.AnnotateFileResponse())
for i in range(batch_size):
    first_page_response = response.responses[i]
    annotation = first_page_response.full_text_annotation
    print("\n\n")
    with open(str(new_files)+".docx", 'a') as f:
        print(annotation.text+"\n\n\n\n\n", file=f)



print("Output printed to "+str(new_files)+" doc file")
##########################################################
# output1 = blob_list[1]
# json_string1 = output1.download_as_string()
# response1 = json_format.Parse(
#             json_string1, vision.types.AnnotateFileResponse())

# second_page_response = response1.responses[1]
# annotation1 = first_page_response.full_text_annotation

# print(u'Full text:')
# print(annotation1.text)
##########################################################
