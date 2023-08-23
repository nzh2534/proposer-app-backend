import numpy as np
import layoutparser as lp
import fitz
from PIL import Image
import layoutparser.ocr as ocr
import boto3
import io
import os
import gc

from botocore.exceptions import ClientError, WaiterError

from detectron2.utils.logger import setup_logger
setup_logger()

from detectron2.config import get_cfg
from detectron2.engine import DefaultPredictor
from detectron2 import model_zoo

session = boto3.Session(
    aws_access_key_id= os.environ['AWS_ACCESS_KEY_ID'],
    aws_secret_access_key= os.environ['AWS_SECRET_ACCESS_KEY'],
    )
s3_client = session.client('s3')
s3_resource = session.resource('s3')

cfg = get_cfg()
cfg.merge_from_file(model_zoo.get_config_file("COCO-Detection/faster_rcnn_R_50_FPN_3x.yaml"))
cfg.MODEL.DEVICE = "cpu"
cfg.MODEL.ROI_HEADS.SCORE_THRESH_TEST = 0.3 # Set threshold for this model
cfg.MODEL.WEIGHTS = os.getcwd() + "/proposals/model_final.pth" #os.environ['AWS_MODEL_PATH'] # Set path model .pth
cfg.MODEL.ROI_HEADS.NUM_CLASSES = 1
print("loading model")
predictor = DefaultPredictor(cfg)

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
        bucket = None

    try:
        head = s3_client.head_object(Bucket=bucketName, Key=filename)
    except ClientError:
        etag = ''
    else:
        etag = head['ETag'].strip('"')

    try:
        s3_obj = bucket.Object(filename)
    except (ClientError, AttributeError):
        s3_obj = None

    try:
        s3_obj.upload_fileobj(src, ExtraArgs={'ACL':'public-read'})
    except (ClientError, AttributeError):
        pass
    else:
        try:
            s3_obj.wait_until_exists(IfNoneMatch=etag)
        except WaiterError as e:
            pass
        else:
            head = s3_client.head_object(Bucket=bucketName, Key=filename)
            success = head['ContentLength']

    return success

def compliance_tool(file_path, pk, Proposal, ComplianceImages, toc_page):
    print("getting images")
    doc = fitz.open(stream=file_path.read(), filetype="pdf")

    del file_path
    gc.collect()

    index = toc_page
    image_dict = {}

    #del cfg
    gc.collect()
    print("model loaded")

    def to_pil(tb, img):
        segment_image = (tb
                        .pad(left=15, right=15, top=5, bottom=5)
                        .crop_image(img))

        return Image.fromarray(segment_image)

    def new_tb(x_1,y_1,x_2,y_2):
        return lp.TextBlock(block=lp.Rectangle(x_1=x_1, y_1=y_1, x_2=x_2, y_2=y_2))

    pages = int(os.environ['PAGE_COUNT'])
    if pages == 0:
        pages = doc.page_count

    zoom_x = 1.5
    zoom_y = 1.5
    mat = fitz.Matrix(zoom_x, zoom_y)

    outputs_list = []
    while index < pages:
        print(index)
        pix = doc.load_page(index).get_pixmap(matrix=mat)
        mode = "RGBA" if pix.alpha else "RGB"
        img = np.array(Image.frombytes(mode, [pix.width, pix.height], pix.samples))
        prediction = predictor(img)
        outputs_list.append([prediction, pix, img])
        del pix, img, mode
        gc.collect()
        index += 1

    # del predictor
    del mat
    gc.collect()

    index = 0
    for o in outputs_list:
        outputs = o[0]
        pix = o[1]
        img = o[2]
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
            tb_list.append(new_tb(i[0],i[1],i[2],i[3]))

        order_list = sorted([b.block.y_1 for b in tb_list]) 

        ordered_tb_list = []
        for y in order_list:
            for tb in tb_list:
                if tb.block.y_1 == y:
                    ordered_tb_list.append(tb)

        text_blocks = lp.Layout(ordered_tb_list)

        # if len(image_dict) == 0:
        #     try:
        #         image_dict[0] = {'Title': 'Initial','Contents': [to_pil(new_tb(0,0,pix.width,text_blocks[0].block.y_1 - 1.5),img)], 'Page':index + toc_page}
        #     except:
        #         image_dict[0] = {'Title': 'Initial','Contents': [to_pil(new_tb(0,0,pix.width,pix.height),img)],'Page':index + toc_page}

        if len(text_blocks) == 0:
            image_dict[list(image_dict)[-1]]['Contents'].append(to_pil(new_tb(0,0,pix.width,pix.height),img))
        else:
            title_order = 0
            if len(image_dict) > 1:
                image_dict[list(image_dict)[-1]]['Contents'].append(to_pil(new_tb(0,0,pix.width,text_blocks[0].block.y_1 - 1.5),img))
            for block in text_blocks:
                try:
                    contents = [to_pil(new_tb(0,block.block.y_2 + 2,pix.width,text_blocks[title_order + 1].block.y_1 - 1.5),img)]
                    image_dict[len(image_dict)] = {'Title': to_pil(block,img), 'Contents': contents, 'Page':index + toc_page}
                    title_order += 1
                except:
                    contents = [to_pil(new_tb(0,block.block.y_1,pix.width,pix.height),img)]
                    image_dict[len(image_dict)] = {'Title': to_pil(block,img), 'Contents': contents, 'Page':index + toc_page}
                    title_order += 1
            
        index += 1

    print("loop ended")
    del outputs_list, order_list, ordered_tb_list, text_blocks
    gc.collect()

    title_list = [] #title image
    title_text = [] #ocr'd title text
    content_list = [] #content image
    content_text = [] #ocr'd content text
    page_number = [] #int

    ocr_agent = ocr.TesseractAgent(languages='eng')

    for i in image_dict:
        height = 0
        for c in image_dict[i]['Contents']:
            height += c.height
        base_img = Image.new("RGB", (pix.width, height), "white")
        print("made base")
        content_y = 0
        for c in image_dict[i]['Contents']:
            base_img.paste(c, (0, content_y))
            content_y += c.height

        print("red")
        content_list.append(base_img)
        content_text.append(ocr_agent.detect(base_img))
        print("green")
        # if i == 0:
        #     title_list.append(base_img)
        #     title_text.append("Overview")
        #     page_number.append(image_dict[i]['Page'] + 1)
        # else:
        title_list.append(image_dict[i]['Title'])
        title_text.append(ocr_agent.detect(image_dict[i]['Title']))
        page_number.append(image_dict[i]['Page'] + 1)

    del image_dict
    gc.collect()

    print("purple")
    name_count = 0
    title_names = []
    content_names = []
    for i in title_list:
        title_name = str(pk) + "_" + str(name_count) + "_" + "title.jpg"
        content_name = str(pk) + "_" + str(name_count) + "_" + "content.jpg"

        # Save the image to an in-memory file
        in_mem_file = io.BytesIO()
        i.save(in_mem_file, format=i.format)
        in_mem_file.seek(0)
        print("sumpin")
        upload_src(in_mem_file, "media/" + title_name, os.environ['AWS_STORAGE_BUCKET_NAME'])
        print("more")
        title_names.append(title_name)

        in_mem_file = io.BytesIO()
        content_list[name_count].save(in_mem_file, format=content_list[name_count].format)
        in_mem_file.seek(0)
        upload_src(in_mem_file, "media/" + content_name, os.environ['AWS_STORAGE_BUCKET_NAME'])
        content_names.append(content_name)

        name_count += 1

    del title_list
    gc.collect()

    result = [title_names, content_names, title_text, content_text, page_number]
    index = 0
    proposal = Proposal.objects.get(pk=pk)
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

    del result, title_names, content_names, title_text, content_text, page_number, ocr_agent, Proposal, ComplianceImages
    gc.collect()

    return "DONE"