import numpy as np
import layoutparser as lp
import fitz
from PIL import Image
import pytesseract
pytesseract.pytesseract.tesseract_cmd = 'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'
import layoutparser.ocr as ocr
import time

from django.conf import settings

def compliance_tool(file_path,pk):
    model = lp.models.Detectron2LayoutModel('lp://PubLayNet/mask_rcnn_X_101_32x8d_FPN_3x/config',
                                    extra_config=["MODEL.ROI_HEADS.SCORE_THRESH_TEST", 0.3],
                                    label_map={0: "Text", 1: "Title", 2: "List", 3:"Table", 4:"Figure"})
    
    doc = fitz.open(stream=file_path.read(), filetype="pdf")
    index = 0

    image_dict = {}

    ocr_agent = ocr.TesseractAgent(languages='eng')

    def to_pil(tb, img):
        segment_image = (tb
                        .pad(left=15, right=15, top=5, bottom=5)
                        .crop_image(img))

        return Image.fromarray(segment_image)

    def new_tb(x_1,y_1,x_2,y_2):
        return lp.TextBlock(block=lp.Rectangle(x_1=x_1, y_1=y_1, x_2=x_2, y_2=y_2))

    ts = time.time()

    while index < 4:
        print(index, ts)
        pix = doc.load_page(index).get_pixmap()
        mode = "RGBA" if pix.alpha else "RGB"
        img = Image.frombytes(mode, [pix.width, pix.height], pix.samples)
        layout_result = model.detect(img)

        tb_list = [b for b in layout_result if b.type=='Title']
        order_list = sorted([b.block.y_1 for b in layout_result if b.type=='Title'])

        ordered_tb_list = []
        for y in order_list:
            for tb in tb_list:
                if tb.block.y_1 == y:
                    ordered_tb_list.append(tb)

        text_blocks = lp.Layout(ordered_tb_list)

        img = np.asarray(img)

        if len(image_dict) == 0:
            try:
                image_dict[0] = {'Title': 'Initial','Contents': [to_pil(new_tb(0,0,pix.width,text_blocks[0].block.y_1 - 1.5),img)], 'Page':index}
            except:
                image_dict[0] = {'Title': 'Initial','Contents': [to_pil(new_tb(0,0,pix.width,pix.height),img)],'Page':index}

        if len(text_blocks) == 0:
            image_dict[list(image_dict)[-1]]['Contents'].append(to_pil(new_tb(0,0,pix.width,pix.height),img))
        else:
            title_order = 0
            if len(image_dict) > 1:
                image_dict[list(image_dict)[-1]]['Contents'].append(to_pil(new_tb(0,0,pix.width,text_blocks[0].block.y_1 - 1.5),img))
            for block in text_blocks:
                try:
                    contents = [to_pil(new_tb(0,block.block.y_2 + 2,pix.width,text_blocks[title_order + 1].block.y_1 - 1.5),img)]
                    image_dict[len(image_dict)] = {'Title': to_pil(block,img), 'Contents': contents, 'Page':index}
                    title_order += 1
                except:
                    contents = [to_pil(new_tb(0,block.block.y_1,pix.width,pix.height),img)]
                    image_dict[len(image_dict)] = {'Title': to_pil(block,img), 'Contents': contents, 'Page':index}
                    title_order += 1
            
        index += 1

    title_list = []
    title_text = []
    content_list = []
    content_text = []
    page_number = []

    for i in image_dict:

        mode = "RGBA" if pix.alpha else "RGB"
        height = 0
        for c in image_dict[i]['Contents']:
            height += c.height
        base_img = Image.new("RGB", (pix.width, height), "white")
        content_y = 0
        for c in image_dict[i]['Contents']:
            base_img.paste(c, (0, content_y))
            content_y += c.height

        content_list.append(base_img)
        content_text.append(ocr_agent.detect(base_img))
        if i == 0:
            title_list.append(base_img)
            title_text.append("Overview")
            page_number.append(image_dict[i]['Page'] + 1)
        else:
            title_list.append(image_dict[i]['Title'])
            title_text.append(ocr_agent.detect(image_dict[i]['Title']))
            page_number.append(image_dict[i]['Page'] + 1)

    name_count = 0
    title_names = []
    content_names = []
    for i in title_list:
        title_name = str(pk) + "_" + str(name_count) + "_" + "title.jpg"
        content_name = str(pk) + "_" + str(name_count) + "_" + "content.jpg"

        title_names.append(title_name)
        i.save(settings.MEDIA_ROOT + title_name)
        #Saving in Front end, may need to be removed/changed in prod
        i.save('C:\\Users\\nhagl\\Desktop\\django-rest-framework\\drf\\frontend\\public\\' + title_name)

        content_names.append(content_name)
        content_list[name_count].save(settings.MEDIA_ROOT + content_name)
        #Saving in Front end, may need to be removed/changed in prod
        content_list[name_count].save('C:\\Users\\nhagl\\Desktop\\django-rest-framework\\drf\\frontend\\public\\' + content_name)

        name_count += 1

    return [title_names, content_names, title_text, content_text, page_number]



