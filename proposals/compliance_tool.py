# import numpy as np
# import fitz
from PIL import Image
import layoutparser.ocr as ocr
import boto3
import os
import gc
import io
import requests
# import json

from botocore.exceptions import ClientError

# # REMOVE IN PROD
# from dotenv import load_dotenv
# load_dotenv()

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


# def ComplianceImages(proposal, title, content, title_text, content_text, page_number, access_token):
#     '''
#     proposal=proposal,
#     title=title_name,
#     content=content_name,
#     title_text=ocr_agent.detect(title),
#     content_text=ocr_agent.detect(content),
#     page_number=index
#     '''
#     data = {
#         "proposal" : proposal,
#         "title_pre": title,
#         "content_pre": content,
#         "title_text": title_text,
#         "content_text": content_text,
#         "page_number": page_number,
#         "process": "None"
#     }

#     headers = {"Authorization": 'JWT ' + access_token}
#     response = requests.post(f'http://localhost:8000/api/proposals/{proposal}/compliance/', data=data, headers=headers)

#     if response.status_code == 201:
#         print("New instance of ChildModel created successfully!")
#         print("New object ID:", response.json()['id'])
#     else:
#         print("Failed to create new instance of ChildModel.")
#         print("Response status code:", response.status_code)
#         #print("Response content:", response.content)

# def proposal_update(pk, title, access_token, *args, **kwargs):

#     data = {
#         "proposal" : pk,
#         "title": title
#     }

#     for key, value in kwargs.items():
#         data[key] = value

#     headers = {"Authorization": 'JWT ' + access_token}
#     response = requests.put(f'http://localhost:8000/api/proposals/{pk}/update/', data=data, headers=headers)

#     if response.status_code == 200:
#         print("Proposal updated")
#     else:
#         print("Proposal Update Failed")
#         print("Response status code:", response.status_code)

# def compliance_tool(file_path, pk, start_page, end_page, start_orig, media_url, start_title_count, proposal_title):
#     #from .models import Proposal #ComplianceImages
#     from detectron2.config import get_cfg
#     from detectron2.engine import DefaultPredictor
#     from detectron2 import model_zoo

#     access_res = requests.post(
#         f'http://localhost:8000/api/token/', 
#         data=json.dumps({"username": os.environ['LAMBDA_USER'], "password": os.environ['LAMBDA_PASS']}), 
#         headers={'Content-Type': 'application/json'}
#         )
#     access_token = access_res.json()['access']

#     cfg = get_cfg()
#     cfg.merge_from_file(model_zoo.get_config_file("COCO-Detection/faster_rcnn_R_50_FPN_3x.yaml"))
#     cfg.MODEL.DEVICE = "cpu"
#     cfg.MODEL.ROI_HEADS.SCORE_THRESH_TEST = 0.3 # Set threshold for this model
#     cfg.MODEL.WEIGHTS = "https://django-proposer.s3.us-east-2.amazonaws.com/media/model_final.pth"#os.environ['AWS_MODEL_PATH']
#     cfg.MODEL.ROI_HEADS.NUM_CLASSES = 1
#     print("loading model")
#     predictor = DefaultPredictor(cfg)
#     ocr_agent = ocr.TesseractAgent(languages='eng')
#     print("model loaded")
#     # proposal = Proposal.objects.get(pk=pk)
#     # filtered_proposal = Proposal.objects.filter(pk=pk)

#     res = requests.get(media_url + file_path)
#     print("getting images")
#     try:
#         doc = fitz.open(stream=res.content, filetype="pdf")
#     except Exception as e:
#         print(e)
#         doc = fitz.open(stream=res.content.read(), filetype="pdf")


#     del file_path
#     gc.collect()

#     index = start_page

#     if end_page > doc.page_count:
#         end_page = doc.page_count
#         #filtered_proposal.update(doc_end=end_page)
#         proposal_update(pk, proposal_title, access_token, doc_end=end_page)

#     pages = end_page

#     zoom_x = 1.5
#     zoom_y = 1.5
#     mat = fitz.Matrix(zoom_x, zoom_y)

#     try:
#         data = requests.get(settings.MEDIA_URL + 'previouscontent_' + pk).content
#         previous_content = Image.open(io.BytesIO(data))
#     except:
#         previous_content = 0

#     title_count = start_title_count#proposal.title_count

#     while index < pages:
#         print(index)
#         pix = doc.load_page(index).get_pixmap(matrix=mat)
#         print("a")
#         mode = "RGBA" if pix.alpha else "RGB"
#         print("b")
#         base_img = Image.frombytes(mode, [pix.width, pix.height], pix.samples)
#         print("c")
#         img = np.array(base_img)
#         print("d")
#         prediction = predictor(img)
#         print("e")

#         outputs = prediction
#         tb_list = []

#         outputs_filtered = outputs['instances'][outputs['instances'].scores > 0.84]

#         scores_list = []
#         lines_list = []
#         for l in outputs_filtered.pred_boxes:
#             lines_list.append([float(l[0]),float(l[1]),float(l[2]),float(l[3])])
#         for s in outputs_filtered.scores:
#             scores_list.append(float(s))

#         line_num = 0
#         for l in lines_list:
#             check = l[1]
#             score = scores_list[line_num]
#             for l2 in lines_list:
#                 if lines_list.index(l2) != line_num: 
#                     if check > l2[1] and check < l2[3]:
#                         try:
#                             if score > scores_list[lines_list.index(l2)]:
#                                 lines_list.remove(l2)
#                                 print("deleted an overlap")
#                             else:
#                                 lines_list.remove(l)
#                                 print("deleted an overlap")
#                         except Exception as e:
#                             print(e)
#             line_num += 1
        
#         for i in lines_list:
#             tb_list.append([i[0],i[1],i[2],i[3]])

#         order_list = sorted([b[1] for b in tb_list]) 

#         ordered_tb_list = []
#         for y in order_list:
#             for tb in tb_list:
#                 if tb[1] == y:
#                     ordered_tb_list.append(tb)

#         print("done with TB list")
#         if len(ordered_tb_list) != 0:
#             for i in ordered_tb_list:
#                 pred_index = ordered_tb_list.index(i)
#                 if ordered_tb_list.index(i) == 0 and previous_content != 0:
#                     print("f_1")
#                     final_content = base_img.crop((0,0,pix.width,i[1]))
#                     print("f_2")
#                     blank_content = Image.new("RGB", (pix.width, previous_content.height + final_content.height), "white")
#                     print("f_3")
#                     blank_content.paste(previous_content,(0,0))
#                     print("f_4")
#                     blank_content.paste(final_content, (0,previous_content.height))

#                     title_name = str(pk) + "_" + str(title_count) + "_" + "title.jpg"
#                     content_name = str(pk) + "_" + str(title_count) + "_" + "content.jpg"
                    
#                     print("f_5")
#                     in_mem_file = io.BytesIO()
#                     previous_title.save(in_mem_file, format="PNG")
#                     in_mem_file.seek(0)
#                     upload_src(in_mem_file, "media/" + title_name, os.environ['AWS_STORAGE_BUCKET_NAME'])

#                     in_mem_file = io.BytesIO()
#                     blank_content.save(in_mem_file, format="PNG")
#                     in_mem_file.seek(0)
#                     upload_src(in_mem_file, "media/" + content_name, os.environ['AWS_STORAGE_BUCKET_NAME'])

#                     print("f_6")

#                     new_ci = ComplianceImages(
#                         proposal=pk,
#                         title=title_name,
#                         content=content_name,
#                         title_text=ocr_agent.detect(previous_title),
#                         content_text=ocr_agent.detect(blank_content),
#                         page_number=index,
#                         access_token=access_token
#                         )
#                     # print("obj")
#                     # new_ci.save()
#                     print("saved")

#                     title_count += 1
#                     #filtered_proposal.update(title_count=title_count)
#                     proposal_update(pk, proposal_title, access_token, title_count=title_count)

#                 if pred_index + 1 != len(ordered_tb_list):
#                     print("a_1")
#                     i2 = ordered_tb_list[pred_index + 1]
#                     print("a_2")
#                     title = base_img.crop((i[0]-15,i[1]-5,i[2]+15,i[3]+5))
#                     print("a_3")
#                     try:
#                         content = base_img.crop((0,i[1]-5,pix.width,i2[1]))
#                     except:
#                         content = base_img.crop((0,i[1]-5,pix.width,i[3]+5))

#                     title_name = str(pk) + "_" + str(title_count) + "_" + "title.jpg"
#                     content_name = str(pk) + "_" + str(title_count) + "_" + "content.jpg"

#                     print("a_4")

#                     in_mem_file = io.BytesIO()
#                     title.save(in_mem_file, format="PNG")
#                     in_mem_file.seek(0)
#                     upload_src(in_mem_file, "media/" + title_name, os.environ['AWS_STORAGE_BUCKET_NAME'])

#                     in_mem_file = io.BytesIO()
#                     content.save(in_mem_file, format="PNG")
#                     in_mem_file.seek(0)
#                     upload_src(in_mem_file, "media/" + content_name, os.environ['AWS_STORAGE_BUCKET_NAME'])

#                     print("a_5")

#                     new_ci = ComplianceImages(
#                         proposal=pk,
#                         title=title_name,
#                         content=content_name,
#                         title_text=ocr_agent.detect(title),
#                         content_text=ocr_agent.detect(content),
#                         page_number=index,
#                         access_token=access_token
#                         )
#                     # print("obj")
#                     # new_ci.save()
#                     print("saved")

#                     title_count += 1
#                     #filtered_proposal.update(title_count=title_count)
#                     proposal_update(pk, proposal_title, access_token, title_count=title_count)
                    
#                 else:
#                     print("b_1")
#                     previous_title = base_img.crop((i[0]-15,i[1]-5,i[2]+15,i[3]+5))
#                     previous_content = base_img.crop((0,i[1]-5,pix.width,pix.height))

#                     in_mem_file = io.BytesIO()
#                     previous_content.save(in_mem_file, format="PNG")
#                     in_mem_file.seek(0)
#                     upload_src(in_mem_file, "media/previouscontent_" + str(pk), os.environ['AWS_STORAGE_BUCKET_NAME'])
#         else:
#             if title_count != 0:
#                 print("c_1")
#                 blank_content = Image.new("RGB", (pix.width, previous_content.height + pix.height), "white")
#                 blank_content.paste(previous_content,(0,0))
#                 blank_content.paste(base_img, (0,previous_content.height))
#                 previous_content = blank_content

#                 in_mem_file = io.BytesIO()
#                 previous_content.save(in_mem_file, format="PNG")
#                 in_mem_file.seek(0)
#                 upload_src(in_mem_file, "media/previouscontent_" + str(pk), os.environ['AWS_STORAGE_BUCKET_NAME'])
            
#         index += 1
#         #filtered_proposal.update(pages_ran=(index - start_orig))
#         proposal_update(pk, proposal_title, access_token, pages_ran=(index - start_orig))

#     # ---- For end of the document -----
#     print("x_1")
#     final_content = base_img.crop((0,0,pix.width, i[1]))
#     blank_content = Image.new("RGB", (pix.width, previous_content.height + final_content.height), "white")
#     blank_content.paste(previous_content,(0,0))
#     blank_content.paste(final_content, (0,previous_content.height))

#     title_name = str(pk) + "_" + str(title_count) + "_" + "title.jpg"
#     content_name = str(pk) + "_" + str(title_count) + "_" + "content.jpg"

#     print("x_2")
#     in_mem_file = io.BytesIO()
#     previous_title.save(in_mem_file, format="PNG")
#     in_mem_file.seek(0)
#     upload_src(in_mem_file, "media/" + title_name, os.environ['AWS_STORAGE_BUCKET_NAME'])

#     in_mem_file = io.BytesIO()
#     blank_content.save(in_mem_file, format="PNG")
#     in_mem_file.seek(0)
#     upload_src(in_mem_file, "media/" + content_name, os.environ['AWS_STORAGE_BUCKET_NAME'])


#     new_ci = ComplianceImages(
#         proposal=pk,
#         title=title_name,
#         content=content_name,
#         title_text=ocr_agent.detect(previous_title),
#         content_text=ocr_agent.detect(blank_content),
#         page_number=index,
#         access_token=access_token
#         )
#     # print("obj")
#     # new_ci.save()
#     print("saved")

#     #filtered_proposal.update(loading=False, pages_ran=(index - start_orig + 1))
#     proposal_update(pk, proposal_title, access_token, loading=False, pages_ran=(index - start_orig + 1))

#     #del Proposal #ComplianceImages
#     gc.collect()

#     return "DONE"

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
        content = img.crop((0,y1,width,y3))

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

def merge_tool(url1, url2, content_id, pk):
    # Download images from URLs

    url1 = settings.MEDIA_URL + url1
    url2 = settings.MEDIA_URL + url2

    image1 = Image.open(io.BytesIO(requests.get(url1).content))
    image2 = Image.open(io.BytesIO(requests.get(url2).content))

    # Ensure images have the same width
    width = max(image1.width, image2.width)
    image1 = image1.resize((width, int(image1.height * (width / image1.width))))
    image2 = image2.resize((width, int(image2.height * (width / image2.width))))

    # Create a new image with doubled height
    merged_image = Image.new('RGB', (width, image1.height + image2.height))

    # Paste the images vertically
    merged_image.paste(image1, (0, 0))
    merged_image.paste(image2, (0, image1.height))

    content_name = str(pk) + "_" + str(content_id) + "_" + "content.jpg"

    in_mem_file = io.BytesIO()
    merged_image.save(in_mem_file, format="PNG")
    in_mem_file.seek(0)
    upload_src(in_mem_file, "media/" + content_name, os.environ['AWS_STORAGE_BUCKET_NAME'])

    return merged_image


def langchain_api(url, template, pk, aitype=os.environ['AI_TYPE']):
    if aitype == "OpenAI":
        from langchain.embeddings.openai import OpenAIEmbeddings
        from langchain.chains import ConversationalRetrievalChain
        from langchain.chat_models import ChatOpenAI
        from langchain.document_loaders import PyPDFLoader
        from langchain_core.prompts import PromptTemplate
        from tempfile import NamedTemporaryFile
        from langchain.vectorstores.pinecone import Pinecone as PineconeStore
        from pinecone import Pinecone
        import time
        print("starting langchain")
        from .models import Proposal
        Proposal.objects.filter(pk=pk).update(loading_checklist=True)
        response = requests.get(settings.MEDIA_URL + url)
        mem_obj = io.BytesIO(response.content)

        print("doc in mem")

        bytes_data = mem_obj.read()
        with NamedTemporaryFile(delete=False) as tmp:
            tmp.write(bytes_data)                     
            loader = PyPDFLoader(tmp.name).load()

        print("doc loader")

        os.remove(tmp.name)
        embeddings = OpenAIEmbeddings()

        print("embeddings loaded")

        pc = Pinecone(api_key=os.environ['PINECONE_API_KEY'])
        index_name = os.environ['PINECONE_INDEX']
        index = pc.Index(index_name)

        print("index found")
        
        pdfsearch = PineconeStore.from_documents(loader, embeddings, index_name=index_name)

        while index.describe_index_stats()['total_vector_count'] < len(loader):
            print(index.describe_index_stats()['total_vector_count'])
            print("sleeping")
            time.sleep(5)
            print("slept")

        temp = ''' 
        You are a helpful AI bot that answers questions for a user.
        The following is a set of context and a question that will relate to the context.
        #CONTEXT
        {context}
        #ENDCONTEXT

        #QUESTION
        {question} Don’t give information outside the document. If the information is not available in the context respond UNABLE TO FIND BASED ON THE PROMPT.
        '''
        
        prompt = PromptTemplate(
                    template=temp, 
                    input_variables=["context", "chat_history", "question"])

        chain = ConversationalRetrievalChain.from_llm(ChatOpenAI(temperature=0.1), 
                                                        retriever=
                                                        pdfsearch.as_retriever(search_kwargs={"k": 1}),
                                                        return_source_documents=True,
                                                        combine_docs_chain_kwargs={"prompt": prompt})
        
        print("chain retrieved")
        chat_history = []
        for i in template:
            print(i['prompt'])
            query = i['prompt']
            try:
                result = chain({"question": query, 'chat_history':chat_history}, return_only_outputs=True)
                chat_history += [(query, result["answer"])]
                i['data'] = result["answer"]
                i['page'] = list(result['source_documents'][0])[1][1]['page']
            except Exception as e:
                print(e)
                continue

        Proposal.objects.filter(pk=pk).update(checklist=template, loading_checklist=False)
        index.delete(delete_all=True)
        
        return "DONE"
    
    if aitype == "HuggingFace":
        from langchain.embeddings.huggingface_hub import HuggingFaceHubEmbeddings
        from langchain.llms.huggingface_hub import HuggingFaceHub
        from langchain.chains import ConversationalRetrievalChain
        from langchain_core.prompts import PromptTemplate
        from langchain.document_loaders import PyPDFLoader
        from tempfile import NamedTemporaryFile
        from langchain.vectorstores.pinecone import Pinecone as PineconeStore
        from pinecone import Pinecone
        import time
        print("starting langchain")
        from .models import Proposal
        Proposal.objects.filter(pk=pk).update(loading_checklist=True)
        response = requests.get(settings.MEDIA_URL + url)
        mem_obj = io.BytesIO(response.content)

        print("doc in mem")

        bytes_data = mem_obj.read()
        with NamedTemporaryFile(delete=False) as tmp:
            tmp.write(bytes_data)                     
            loader = PyPDFLoader(tmp.name).load()

        print("doc loader")

        os.remove(tmp.name)
        embeddings = HuggingFaceHubEmbeddings()

        llm = HuggingFaceHub(
            repo_id="HuggingFaceH4/zephyr-7b-beta",
            task="text-generation",
            model_kwargs={
                "max_new_tokens": 512,
                "top_k": 30,
                "temperature": 0.1,
                "repetition_penalty": 1.03,
            },
        )

        print("embeddings loaded")

        pc = Pinecone(api_key=os.environ['PINECONE_API_KEY'])
        index_name = os.environ['PINECONE_INDEX2']
        index = pc.Index(index_name)

        print("index found")
        
        pdfsearch = PineconeStore.from_documents(loader, embeddings, index_name=index_name)

        while index.describe_index_stats()['total_vector_count'] < len(loader):
            print(index.describe_index_stats()['total_vector_count'])
            print("sleeping")
            time.sleep(5)
            print("slept")

        temp = ''' 
        You are a helpful AI bot that answers questions for a user.
        The following is a set of context and a question that will relate to the context.
        #CONTEXT
        {context}
        #ENDCONTEXT

        #QUESTION
        {question} Don’t give information outside the document. If the information is not available in the context respond UNABLE TO FIND BASED ON THE PROMPT.
        '''
        
        prompt = PromptTemplate(
                    template=temp, 
                    input_variables=["context", "chat_history", "question"])


        chain = ConversationalRetrievalChain.from_llm(llm=llm, 
                                                        retriever=
                                                        pdfsearch.as_retriever(search_kwargs={"k": 1}),
                                                        return_source_documents=True,
                                                        combine_docs_chain_kwargs={"prompt": prompt})
        
        print("chain retrieved")
        chat_history = []
        for i in template:
            print(i['prompt'])
            query = i['prompt']
            try:
                result = chain({"question": query, 'chat_history':chat_history}, return_only_outputs=True)
                chat_history += [(query, result["answer"])]
                i['data'] = result["answer"]
                i['page'] = list(result['source_documents'][0])[1][1]['page']
            except Exception as e:
                print(e)
                continue

        Proposal.objects.filter(pk=pk).update(checklist=template, loading_checklist=False)
        index.delete(delete_all=True)
        
        return "DONE"