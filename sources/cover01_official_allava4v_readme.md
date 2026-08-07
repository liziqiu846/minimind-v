---
license: cc-by-nc-4.0
task_categories:
- question-answering
- text-generation
language:
- en
tags:
- GPT-4V
- LVLM
- Vision
- Language
size_categories:
- 1M<n<10M

configs:
  - config_name: allava_laion
    data_files:
      - split: caption
        path: "allava_laion/ALLaVA-Caption-LAION-4V.json"
      - split: instruct
        path: "allava_laion/ALLaVA-Instruct-LAION-4V.json"
  - config_name: allava_vflan
    data_files:
      - split: caption
        path: "allava_vflan/ALLaVA-Caption-VFLAN-4V.json"
      - split: instruct
        path: "allava_vflan/ALLaVA-Instruct-VFLAN-4V.json"    
  - config_name: allava_text
    data_files:
      - split: train
        path: "allava_text/Evol-Instruct-GPT4-Turbo-143K.json"
      
# - config_name: allava_laion_instruction
#   data_files: "allava_laion/ALLaVA-Instruct-LAION-4V.json"
  
# configs:
# - config_name: default
#   data_files:
#   - split: allava_laion_caption
#     path: "allava_laion/ALLaVA-Caption-LAION-4V.json"
#   - split: allava_laion_instruction
#     path: "allava_laion/ALLaVA-Instruction-LAION-4V.json"
  
# configs:
# - config_name: default
# - data_files:
#   - split: allava_laion_caption
#   - path:
#     - "allava_laion/ALLaVA-Caption-LAION-4V.json"
#   - split: allava_laion_instruction
#   - path:
#     - "allava_laion/ALLaVA-Instruction-LAION-4V.json"
---
## 📚 ALLaVA-4V Data

### Generation Pipeline

<!--
<div align=center>
<img src="assets/pipeline.jpg" width = "640" alt="pipeline" align=center />
</div>
-->

* LAION

We leverage the superb GPT-4V to generate captions and complex reasoning QA pairs. Prompt is [here](https://github.com/FreedomIntelligence/ALLaVA/blob/main/prompts/prompt_for_laion.txt).

* Vison-FLAN

We leverage the superb GPT-4V to generate captions and detailed answer for the original instructions.  Prompt is [here](
https://github.com/FreedomIntelligence/ALLaVA/blob/main/prompts/prompt_for_vflan.txt).

* Wizard

We regenerate the answer of Wizard_evol_instruct with GPT-4-Turbo.

### Dataset Cards

All datasets can be found [here](https://huggingface.co/datasets/FreedomIntelligence/ALLaVA-4V).
The structure of naming is shown below:
```bash
ALLaVA-4V
├── ALLaVA-Caption-4V
│   ├── ALLaVA-Caption-LAION-4V
│   └── ALLaVA-Caption-VFLAN-4V
├── ALLaVA-Instruct-4V
│   ├── ALLaVA-Instruct-LAION-4V
│   └── ALLaVA-Instruct-VFLAN-4V
├── Evol-Instruct-GPT4-Turbo-143K
```

The folder structure of this dataset space:
```bash
ALLaVA-4V
├── allava_laion/
│   ├── ALLaVA-Caption-LAION-4V.json
│   ├── ALLaVA-Instruct-LAION-4V.json
|   └── images.zip 
├── allava_vflan/
│   ├── ALLaVA-Caption-VFLAN-4V.json
│   └── ALLaVA-Instruct-VFLAN-4V.json
├── allava_text/
│   └── Evol-Instruct-GPT4-Turbo-143K.json
├── others/
│   ├── Instruct-LAION-4oiterative.json
│   └── Instruct-LAION-4v_gemini_claude-ensembled.json
```
**We do not own right to any image contained within the "images.zip" file. We collate the images and upload this file in request of the community to facilitate the data preparation process.**

Here we provide detailed information of each subset.

| Name | #Samples | Image Source | Instruction Source | Answer Source |
| --- | ---: | ---: | ---: | ---: | 
|ALLaVA-Caption-LAION-4V* | 468,670 | LAION (web) | [Handcrafted](prompts/instructions_for_captions.txt) | GPT-4V
|ALLaVA-Caption-VFLAN-4V**| 194,976 | [Vision FLAN](https://huggingface.co/datasets/Vision-Flan/vision-flan_191-task_1k/tree/main) | [Handcrafted](prompts/instructions_for_captions.txt) | GPT-4V
|ALLaVA-Instruct-LAION-4V* | 468,670 | LAION (web) | GPT-4V | GPT-4V
|ALLaVA-Instruct-VFLAN-4V**| 192,903 | [Vision FLAN](https://huggingface.co/datasets/Vision-Flan/vision-flan_191-task_1k/tree/main) | [Vision FLAN](https://huggingface.co/datasets/Vision-Flan/vision-flan_191-task_1k/tree/main) *** | GPT-4V
Evol-Instruct-GPT4-Turbo-143K |143,000 | / | [Wizard](https://huggingface.co/datasets/WizardLM/WizardLM_evol_instruct_V2_196k) | GPT-4-Turbo
|Instruct-LAION-4oiterative|49,932|LAION (web)| GPT-4o**** | GPT-4o|
|Instruct-LAION-4v_gemini_claude-ensembled|49,946|LAION (web)| GPT-4V, Gemini, Claude**** | GPT-4V, Gemini, Claude |

*ALLaVA-Caption-LAION-4V* and *ALLaVA-Instruct-LAION-4V* share the same set of images.

** *ALLaVA-Caption-VFLAN-4V* and *ALLaVA-Instruct-VFLAN-4V* share the same set of images. 

*** In *ALLaVA-Caption-VFLAN-4V* and *ALLaVA-Instruct-VFLAN-4V*, we additionally include 30K samples which are distilled following the same manner for LAION (i.e. Distilling Captions and Complex Reasoning QA pairs). We mix them up with the other data whose instructions are from the original VFLAN.

**** We use `gpt-4o-2024-08-06` for GPT-4o, `gemini-1.5-pro` for Gemini, and `claude-3-5-sonnet-20240620` for Claude.

### Data Preparation
Clone our github repo first:
```shell
git clone https://github.com/FreedomIntelligence/ALLaVA.git
cd ALLaVA
```

#### LAION

Specify the `laion_root` in `./download/download_laion.sh` and run 
```shell
sh ./download/download_laion.sh
```
<!-- Specify the input and output paths in `./download/laion/download_laion.sh` and simply run
```shell
sh ./download/laion/laion.sh
```
to start downloading images from URLs in the annotation files. As a reference, downloading 512K images takes ~10 hours with 200 threads and a maximum bandwidth of 3MB/s. The outputs of running this script are:

- successfully downloaded images (binary files)

- captions in conversation format with local image paths (json)

- instructions in conversation format with local image paths (json) -->


#### VFLAN
Specify the `vflan_root` in `./download/download_vflan.sh` and run 
```shell
sh ./download/download_vflan.sh
```


#### Evol-Instruct-GPT4-Turbo-143K
Specify the `text_root` in `./download/download_text.sh` and run 
```shell
sh ./download/download_text.sh
```


### Sample Demonstration
<details><summary>ALLaVA-Caption-LAION-4V</summary>

```
{
  "id": "allava_laion_cap_100277305",
  "image": "allava_laion/images/100277305.jpeg",
  "conversations": [
    {
      "from": "human",
      "value": "<image>\nPlease depict the image in words."
    },
    {
      "from": "gpt",
      "value": "The image displays a silver ring with a design that resembles a stylized leaf. The leaf design is split into two symmetrical halves, separated by a gap that runs along the ring's band. Each half of the leaf pattern is textured with detailed, vein-like striations that give it a realistic look. The edges of the leaf design are embellished with small, clear gemstones that could possibly be diamonds, adding a sparkle to the ring. The band of the ring is wide, supporting the large leaf motif, and it tapers slightly as it moves away from the leaf design. The silver metal has a high polish, reflecting light brightly and providing a contrast to the textured leaf surface. The craftsmanship suggests a mix of organic inspiration with a touch of elegance due to the gems
tone accents."
    }
  ],
  "original_caption": "190952cz Pandora Tropical Palm Leaf Ring",
  "url": "https://theartofpandora.com/wp-content/uploads/2016/10/190952CZ-1-600x600.jpg"
}
  ```
</details>


<details><summary>ALLaVA-Caption-VFLAN-4V</summary>

```
{
  "id": "allava_vflan_cap_100000",
  "image": "allava_vflan/images/images_191task_1k/PACS+guitar_image_category_classification_830_n03272010_10795-5.png",
  "conversations": [
    {
      "from": "human",
      "value": "<image>\nHow would you describe the image to someone who cannot see it?"
    },
    {
      "from": "gpt",
      "value": "The image shows a simplistic line drawing of an electric guitar. The guitar is oriented diagonally from the top left corner to the bottom right corner of the image. It has a long, narrow neck with tuning pegs at the top, resembling a stylized \"T\" shape. The body of the guitar is irregular, with two cutaways on either side of the neck, giving it an asymmetric appearance. The body is also characterized by sharp angles rather than curves, which is not typical for most guitars. There are four horizontal lines across the body, likely representing strings. The drawing is black and white, with no shading or color, and appears to be hand-drawn with a single continuous line without much detail. The background is plain and white."
    }
  ]
}
```
</details>

<details><summary>ALLaVA-Instruct-LAION-4V</summary>

```
{
  "id": "allava_laion_inst_100277305",
  "image": "allava_laion/images/100277305.jpeg",
  "conversations": [
    {
      "from": "human",
      "value": "<image>\nHow does the inclusion of gemstones affect the overall aesthetic and possible value of the ring?"
    },
    {
      "from": "gpt",
      "value": "The inclusion of gemstones along the edges of the leaf design enhances the ring's aesthetic by adding a touch of brilliance and luxury. The small, clear gemstones catch the light, creating a sparkling effect that contrasts with the silver's polished surface and the leaf's textured details. This sparkling accent likely increases the ring's visual appeal, making it stand out more as an accessory. In terms of value, the presence of gemstones, which could be diamonds, would likely raise the ring's monetary worth. Gemstones, especially diamonds, are prized for their beauty and durability, and their addition to jewelry pieces often signifies a higher quality and class of the item, thereby increasing its market value."
    }
  ],
  "original_caption": "190952cz Pandora Tropical Palm Leaf Ring",
  "url": "https://theartofpandora.com/wp-content/uploads/2016/10/190952CZ-1-600x600.jpg"
}
```
</details>


<details><summary>ALLaVA-Instruct-VFLAN-4V</summary>

```
{
  "id": "allava_vflan_inst_9",
  "image": "allava_vflan/images/images_191task_1k/VQA-E+visual_question_answering_574_COCO_train2014_000000119456.jpg",
  "conversations": [
    {
      "from": "human",
      "value": "<image>\nYou are provided with an image and a question related to the image. Answer the question based on the information given in the image.\n\nIs bigfoot in the picture?"
    },
    {
      "from": "gpt",
      "value": "The creature in the image is not Bigfoot, also known as Sasquatch. Bigfoot is typically described in folklore and cryptozoology as a large, bipedal humanoid creature with ape-like features, standing upwards of 6 to 9 feet tall. The animal present in the photograph is quadrupedal, possesses a body structure similar to that of a pig, and has features such as long hair and tusks, which are characteristic of a wild boar. Additionally, there is no evidence of bipedal creatures or any human-like figures that would suggest the presence of Bigfoot. The setting and visual clues do not align with the commonly reported sightings of Bigfoot, which often describe it as a solitary figure standing upright among trees. Therefore, based on the visual information available in the image, the conclusion is that Bigfoot is not depicted here."
    }
  ]
}
```
</details>

<details><summary>Evol-Instruct-GPT4-Turbo-143K</summary>

```
{
  "idx": "heR0vZB",
  "conversations": [
    {
      "from": "human",
      "value": "As an online platform teacher named Aimee, you possess impeccable credentials which include a Bachelor of Science degree in Industrial and Labor Relations from Cornell University, expertise in the English language, and intermediate proficiency in both Chinese and Spanish. Additionally, your professional experience as a STEAM teacher at UN Women in Singapore has honed your skills in teaching children from the ages of 6-11 and working with students from all levels of education. Your exceptional teaching abilities in spoken English and pronunciation paired with your personal strengths of being informed, patient, and engaging make you an ideal teacher for students seeking to improve their English language skills. Can you provide a short, concise, and unique English self-introduction in bullet point form that would attract students to enroll in your course?"
    },
    {
      "from": "gpt",
      "value": "Sure, here are some bullet points for your English self-introduction:\n\n- Hi there! My name is Aimee and I'm thrilled to be your online English teacher!\n- With a Bachelor's degree from Cornell University and experience teaching STEAM at UN Women in Singapore, I know how to help students learn effectively.\n- I'm passionate about language and have intermediate proficiency in both Chinese and Spanish, so I understand the challenges of learning a new language.\n- In my classes, I focus on improving spoken English and pronunciation, as well as building vocabulary and grammar skills.\n- But learning English doesn't have to be boring! I'm an engaging and patient teacher who loves to have fun and make learning enjoyable.\n- So, whether you're a beginner or an advanced student, I'm confident that I can help you improve your English skills and achieve your goals. Let's get started!"
    }
  ]
}
```
</details>



## Citation

<!-- If there is a paper or blog post introducing the dataset, the APA and Bibtex information for that should go in this section. -->
If you find our data useful, please consider citing our work! We are FreedomIntelligence from [Shenzhen Research Institute of Big Data](http://sribd.cn/en) and [The Chinese University of Hong Kong, Shenzhen](https://sds.cuhk.edu.cn/en)
```
@misc{chen2024allava,
      title={ALLaVA: Harnessing GPT4V-synthesized Data for A Lite Vision-Language Model}, 
      author={Guiming Hardy Chen and Shunian Chen and Ruifei Zhang and Junying Chen and Xiangbo Wu and Zhiyi Zhang and Zhihong Chen and Jianquan Li and Xiang Wan and Benyou Wang},
      year={2024},
      eprint={2402.11684},
      archivePrefix={arXiv},
      primaryClass={cs.CL}
}
```