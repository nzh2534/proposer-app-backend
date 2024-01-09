import numpy as np
import fitz
from PIL import Image
import layoutparser.ocr as ocr
import boto3
import os
import gc
import io
import requests

from botocore.exceptions import ClientError

# -- Only needed for Detectron2 testing/logs
# from detectron2.utils.logger import setup_logger
# setup_logger()

from django.conf import settings

session = boto3.Session(
    aws_access_key_id= os.environ['AWS_ACCESS_KEY_ID'],
    aws_secret_access_key= os.environ['AWS_SECRET_ACCESS_KEY'],
    )
s3_client = session.client('s3')
s3_resource = session.resource('s3')


gc.enable()

def add_import(a, b):
    print("adding")
    x = a + b
    print("done adding")
    return x

def upload_src(src, filename, bucketName):
    success = False
    try:
        bucket = s3_resource.Bucket(bucketName)
    except ClientError as e:
        print(e)
        bucket = None
    try:
        s3_obj = bucket.Object(filename)
    except (ClientError, AttributeError) as e:
        print(e)
        s3_obj = None

    try:
        s3_obj.upload_fileobj(src, ExtraArgs={'ACL':'public-read'})
    except (ClientError, AttributeError) as e:
        print(e)
        pass

    return success

def image_to_inmemory_and_s3 (id, pk, img, suffix):
    new_file_name = str(pk) + "_" + id + "_" + suffix
    in_mem_file = io.BytesIO()
    img.save(in_mem_file, format="PNG")
    in_mem_file.seek(0)
    upload_src(in_mem_file, "media/" + new_file_name, os.environ['AWS_STORAGE_BUCKET_NAME'])
    return new_file_name

def compliance_tool(file_path, pk, toc_page, proposal):
    from .models import ComplianceImages
    from detectron2.config import get_cfg
    from detectron2.engine import DefaultPredictor
    from detectron2 import model_zoo
    cfg = get_cfg()
    cfg.merge_from_file(model_zoo.get_config_file("COCO-Detection/faster_rcnn_R_50_FPN_3x.yaml"))
    cfg.MODEL.DEVICE = "cpu"
    cfg.MODEL.ROI_HEADS.SCORE_THRESH_TEST = 0.3 # Set threshold for this model
    cfg.MODEL.WEIGHTS = os.environ['AWS_MODEL_PATH'] # Set path model .pth
    cfg.MODEL.ROI_HEADS.NUM_CLASSES = 1
    print("loading model")
    predictor = DefaultPredictor(cfg)
    ocr_agent = ocr.TesseractAgent(languages='eng')
    print("model loaded")

    res = requests.get(settings.MEDIA_URL + file_path)
    print("getting images")
    try:
        doc = fitz.open(stream=res.content, filetype="pdf")
    except Exception as e:
        print(e)
        doc = fitz.open(stream=res.content.read(), filetype="pdf")

    del file_path
    gc.collect()

    index = toc_page

    pages = int(os.environ['PAGE_COUNT'])
    if pages == 0:
        pages = doc.page_count

    zoom_x = 1.5
    zoom_y = 1.5
    mat = fitz.Matrix(zoom_x, zoom_y)

    previous_content = 0
    title_count = 0
    title_names = [] 
    content_names = [] 
    title_text = []
    content_text = []
    page_number = []
    while index < pages:
        print(index)
        pix = doc.load_page(index).get_pixmap(matrix=mat)
        print("a")
        mode = "RGBA" if pix.alpha else "RGB"
        print("b")
        base_img = Image.frombytes(mode, [pix.width, pix.height], pix.samples)
        print("c")
        img = np.array(base_img)
        print("d")
        prediction = predictor(img)
        print("e")

        outputs = prediction
        tb_list = []

        outputs_filtered = outputs['instances'][outputs['instances'].scores > 0.84]

        scores_list = []
        lines_list = []
        for l in outputs_filtered.pred_boxes:
            lines_list.append([float(l[0]),float(l[1]),float(l[2]),float(l[3])])
        for s in outputs_filtered.scores:
            scores_list.append(float(s))

        line_num = 0
        for l in lines_list:
            check = l[1]
            score = scores_list[line_num]
            for l2 in lines_list:
                if lines_list.index(l2) != line_num: 
                    if check > l2[1] and check < l2[3]:
                        if score > scores_list[lines_list.index(l2)]:
                            lines_list.remove(l2)
                            print("deleted an overlap")
                        else:
                            lines_list.remove(l)
                            print("deleted an overlap")
            line_num += 1
        
        for i in lines_list:
            tb_list.append([i[0],i[1],i[2],i[3]])

        order_list = sorted([b[1] for b in tb_list]) 

        ordered_tb_list = []
        for y in order_list:
            for tb in tb_list:
                if tb[1] == y:
                    ordered_tb_list.append(tb)

        print("done with TB list")
        if len(ordered_tb_list) != 0:
            for i in ordered_tb_list:
                pred_index = ordered_tb_list.index(i)
                if ordered_tb_list.index(i) == 0 and previous_content != 0:
                    print("f_1")
                    final_content = base_img.crop((0,0,pix.width,i[1]))
                    print("f_2")
                    blank_content = Image.new("RGB", (pix.width, previous_content.height + final_content.height), "white")
                    print("f_3")
                    blank_content.paste(previous_content,(0,0))
                    print("f_4")
                    blank_content.paste(final_content, (0,previous_content.height))

                    title_name = str(pk) + "_" + str(title_count) + "_" + "title.jpg"
                    content_name = str(pk) + "_" + str(title_count) + "_" + "content.jpg"
                    
                    print("f_5")
                    in_mem_file = io.BytesIO()
                    previous_title.save(in_mem_file, format="PNG")
                    in_mem_file.seek(0)
                    upload_src(in_mem_file, "media/" + title_name, os.environ['AWS_STORAGE_BUCKET_NAME'])

                    in_mem_file = io.BytesIO()
                    blank_content.save(in_mem_file, format="PNG")
                    in_mem_file.seek(0)
                    upload_src(in_mem_file, "media/" + content_name, os.environ['AWS_STORAGE_BUCKET_NAME'])

                    print("f_6")
                    title_names.append(title_name)
                    content_names.append(content_name)
                    title_text.append(ocr_agent.detect(previous_title))
                    content_text.append(ocr_agent.detect(blank_content))
                    page_number.append(index)

                    title_count += 1

                if pred_index + 1 != len(ordered_tb_list):
                    print("a_1")
                    i2 = ordered_tb_list[pred_index + 1]
                    print("a_2")
                    title = base_img.crop((i[0]-15,i[1]-5,i[2]+15,i[3]+5))
                    print("a_3")
                    try:
                        content = base_img.crop((0,i[1]-5,pix.width,i2[1]))
                    except:
                        content = base_img.crop((0,i[1]-5,pix.width,i[3]+5))

                    title_name = str(pk) + "_" + str(title_count) + "_" + "title.jpg"
                    content_name = str(pk) + "_" + str(title_count) + "_" + "content.jpg"

                    print("a_4")

                    in_mem_file = io.BytesIO()
                    title.save(in_mem_file, format="PNG")
                    in_mem_file.seek(0)
                    upload_src(in_mem_file, "media/" + title_name, os.environ['AWS_STORAGE_BUCKET_NAME'])

                    in_mem_file = io.BytesIO()
                    content.save(in_mem_file, format="PNG")
                    in_mem_file.seek(0)
                    upload_src(in_mem_file, "media/" + content_name, os.environ['AWS_STORAGE_BUCKET_NAME'])

                    print("a_5")
                    title_names.append(title_name)
                    content_names.append(content_name)
                    title_text.append(ocr_agent.detect(title))
                    content_text.append(ocr_agent.detect(content))
                    page_number.append(index)

                    title_count += 1
                else:
                    print("b_1")
                    previous_title = base_img.crop((i[0]-15,i[1]-5,i[2]+15,i[3]+5))
                    previous_content = base_img.crop((0,i[1]-5,pix.width,pix.height))
        else:
            if title_count != 0:
                print("c_1")
                blank_content = Image.new("RGB", (pix.width, previous_content.height + pix.height), "white")
                blank_content.paste(previous_content,(0,0))
                blank_content.paste(base_img, (0,previous_content.height))
                previous_content = blank_content
            
        index += 1

    # ---- For end of the document -----
    print("x_1")
    final_content = base_img.crop((0,0,pix.width,i[1]))
    blank_content = Image.new("RGB", (pix.width, previous_content.height + final_content.height), "white")
    blank_content.paste(previous_content,(0,0))
    blank_content.paste(final_content, (0,previous_content.height))

    title_name = str(pk) + "_" + str(title_count) + "_" + "title.jpg"
    content_name = str(pk) + "_" + str(title_count) + "_" + "content.jpg"

    print("x_2")
    in_mem_file = io.BytesIO()
    previous_title.save(in_mem_file, format="PNG")
    in_mem_file.seek(0)
    upload_src(in_mem_file, "media/" + title_name, os.environ['AWS_STORAGE_BUCKET_NAME'])

    in_mem_file = io.BytesIO()
    blank_content.save(in_mem_file, format="PNG")
    in_mem_file.seek(0)
    upload_src(in_mem_file, "media/" + content_name, os.environ['AWS_STORAGE_BUCKET_NAME'])

    title_names.append(title_name)
    content_names.append(content_name)
    title_text.append(ocr_agent.detect(previous_title))
    content_text.append(ocr_agent.detect(blank_content))
    page_number.append(index)

    result = [title_names, content_names, title_text, content_text, page_number]
    index = 0

    for i in result[0]:
        print("obj call")
        new_ci = ComplianceImages(
            proposal=proposal,
            title=(i),
            content=(result[1][index]),
            title_text=result[2][index],
            content_text=result[3][index],
            page_number=result[4][index]
            )
        print("obj")
        new_ci.save()
        print("saved")
        index += 1

    del result, title_names, content_names, title_text, content_text, page_number, Proposal, ComplianceImages
    gc.collect()

    return "DONE"

def splitter_tool(boxes, obj, ComplianceImages, Proposal, baseId):
    '''Takes as input (1) x box coordinates, (2) the ComplianceImage obj/image that the box coordinates reference,
    (3) the ComplianceImages Django Model object, (4) the Proposal Django Model object, and (5) the base heirarchy id
    of the image that the box coordinates reference
    '''

    content_path= settings.MEDIA_URL + str(obj.content.file)
    title_path = settings.MEDIA_URL + str(obj.title.file)
    content_name= str(obj.content.file)
    pk=obj.proposal.pk
    page_number = int(obj.page_number)
    ocr_agent = ocr.TesseractAgent(languages='eng')

    proposal = Proposal.objects.get(pk=pk)

    #The base img that the box coordinates reference
    img = Image.open(io.BytesIO(requests.get(content_path).content))

    for index, box in enumerate(boxes):

        # This IF statement updates the ComplianceImage obj/image that the box coordinates reference
        # The old is removed an a new ComplianceImage obj is saved below to S3 and then saved in Django
        # after splitter_tool has ran in serializers.py
        if index == 0:
            width = img.width
            x1 = box['start']['x']
            y1 = box['start']['y']
            x2 = box['end']['x']
            y2 = box['end']['y']

            updated_content = img.crop((0,0,width,y1))

            response = requests.get(title_path)
            title_img = Image.open(io.BytesIO(response.content))

            new_title_name = image_to_inmemory_and_s3(baseId, str(pk), title_img, 'title.jpg')
            new_content_name = image_to_inmemory_and_s3(baseId, str(pk), updated_content, 'content.jpg')

            updated_title_text = ocr_agent.detect(title_img)
            updated_content_text = ocr_agent.detect(updated_content)

        # A new ComplianceImage obj is saved to Django backend and S3 for each box provided in boxes var
        # after index 0
        x1 = box['start']['x']
        y1 = box['start']['y']
        x2 = box['end']['x']
        y2 = box['end']['y']
        id = box['id']

        if index + 1 < len(boxes):
            print('g')
            y3 = boxes[index + 1]['start']['y']
        else:
            print('h')
            y3 = img.height

        print(y2)
        print(y3)
        title = img.crop((x1,y1,x2,y2))
        content = img.crop((0,y2,width,y3))

        title_name = image_to_inmemory_and_s3(id, str(pk), title, "title.jpg")
        content_name = image_to_inmemory_and_s3(id, str(pk), content, "content.jpg")

        title_text = ocr_agent.detect(title)
        content_text = ocr_agent.detect(content)

        new_ci = ComplianceImages(
            proposal=proposal,
            title=title_name,
            content=content_name,
            title_text=title_text,
            content_text=content_text,
            page_number=page_number
        )
        new_ci.save()
    
    return {
        "title_text": updated_title_text, 
        "content_text": updated_content_text, 
        "title": new_title_name, 
        "content": new_content_name}