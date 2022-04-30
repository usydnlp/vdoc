from collections import defaultdict
import json, os

all_files = []
json_path = 'ocr_json_files/'
json_list = os.listdir(json_path)
out_path = 'input_ocr/'

if not os.path.exists(out_path):
    os.mkdir(out_path)


documents = defaultdict(list)

all_pages = []

for name in json_list:
    path = json_path + name
    with open(path) as f:
        print(f.name)
        pages = json.load(f)
    all_pages.extend(pages)

for page in all_pages:
    doc_name = page['page_filename'].split('.')[0]
    documents[doc_name].append(page)

for name, pages in documents.items():
    with open(out_path+'/'+name+'.json', 'w') as f:
        json.dump(pages, f)



