# V-Doc : Visual questions answers with Documents
This repository contains code for the paper [V-Doc : Visual questions answers with Documents](https://arxiv.org/pdf/2205.13724.pdf). The demo videos can be accessed by this [link](https://drive.google.com/file/d/1Ztp9LBcrEcJA3NlbFWn1RfNyfwt8Y6Qk/view).

<h4 align="center">
  <b>Ding, Y.*, Huang, Z.*, Wang, R., Zhang, Y., Chen, X., Ma, Y., Chung, H., & Han, C. (CVPR 2022) <br/><a href="https://arxiv.org/pdf/2205.13724.pdf">V-Doc : Visual questions answers with Documents</a><br/></b></span>
</h4>

<p align="center">
  <img src="https://github.com/usydnlp/vdoc/blob/main/images/system_architecture.png">
</p>

### Dataset for training

The dataset we used to trained the model is provided in following links:


 [PubVQA Dataset] (https://drive.google.com/drive/folders/1YMuctGPJbsy45Iz23ygcN1VGHWQp3aaU?ths=true) for training Mac-Network.

Dataset for training LayoutLMv2([FUNSD-QA] (https://drive.google.com/file/d/1Ev_sLTx3U9nAr2TGgUT5BXB1rpfLMlcq/view?usp=sharing)). 

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
