# V-Doc : Visual questions answers with Documents

To run the scene based question generation code, we need to fetch the JSON files from the source.  

#### Extract OCR information
```bash
python3 ./document_collection.py
```
After the step above, a new folder called <code>./input_ocr</code> will be generated.
#### Generate questions
```bash
python3 ./scene_based/pdf_generate_question.py
```
To limit the number of generated questions, you can change the code in <code>pdf_generate_question.py</code> line 575 and line 591-596

After the steps above, you can see a json file under the <code>./output_qa_dataset</code>.