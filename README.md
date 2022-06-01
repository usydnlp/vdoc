# V-Doc : Visual questions answers with Documents
This repository contains code for the paper [V-Doc : Visual questions answers with Documents](https://arxiv.org/pdf/2205.13724.pdf)

<h4 align="center">
  <b>Ding, Y.*, Huang, Z.*, Wang, R., Zhang, Y., Chen, X., Ma, Y., Chung, H., & Han, C. (CVPR 2022) <br/><a href="https://arxiv.org/pdf/2205.13724.pdf">V-Doc : Visual questions answers with Documents</a><br/></b></span>
</h4>

![image](https://github.com/usydnlp/vdoc/tree/main/images/system_architecture.png)

### Dataset Generation
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
