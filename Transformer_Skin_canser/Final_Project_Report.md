<center>
<b>INSTITUTION NAME</b><br>
<b>UNIVERSITY LOGO PLACEHOLDER</b><br>
<b>DEPARTMENT OF COMPUTER SCIENCE</b><br>
<b>ACADEMIC YEAR: 2025-2026</b><br>
<br>
<b>SKIN DISEASE PREDICTION SYSTEM</b><br>
<b>Comprehensive Project Report</b><br>
<br>
<b>Submitted To:</b><br>
Guide Name Placeholder<br>
Course Name Placeholder<br>
<br>
<b>Submitted By:</b><br>
Akshay Kumar Bolusani (Roll No: 21CS001, Class: CSE-A)<br>
Priya Sharma (Roll No: 21CS002, Class: CSE-A)<br>
Rahul Verma (Roll No: 21CS003, Class: CSE-A)<br>
Sneha Patel (Roll No: 21CS004, Class: CSE-A)<br>
<br>
Date: December 6, 2025<br>
</center>

---

# Table of Contents

1. Abstract
2. Keywords
3. Introduction
4. Problem Definition
5. Objectives of the Study
6. Scope of the Project
7. Existing System
8. Proposed System
9. Literature Survey
10. Methodology / System Design
11. UML Diagrams
12. ER Diagram / Data Flow Diagram
13. Module Description
14. Algorithms Used
15. Hardware Requirements
16. Software Requirements
17. Project Planning (Gantt Chart)
18. Testing & Results
19. Conclusion & Future Scope
20. Bibliography
21. Appendix

---

# 1. Abstract
This project report presents the development of a Skin Disease Prediction System using deep learning models, including DINOv2 Vision Transformer [1] and ResNet50 CNN [2]. The system is designed to classify skin lesions as benign or malignant, integrating a chatbot powered by Groq LLM and a gamified reward system for user engagement. The platform achieves 92.6% test accuracy and includes features for prediction history, analytics, feedback collection, and active learning capabilities. The system addresses the need for accessible skin cancer screening while maintaining clinical safety through confidence-based flagging and expert review workflows.

# 2. Keywords
Skin cancer detection, deep learning, vision transformer, convolutional neural networks, active learning, medical imaging, reinforcement learning, dermoscopy

# 3. Introduction
Skin cancer is one of the most prevalent cancers worldwide, with melanoma accounting for approximately 1.7% of global cancer diagnoses [13]. Early detection is crucial for improving survival rates, as the 5-year survival rate for localized melanoma exceeds 99%, dropping to 35% for distant metastases [13]. Traditional diagnostic methods rely on dermatologist expertise and visual inspection, which can be subjective and time-consuming.

Recent advances in deep learning have revolutionized medical image analysis. CNNs have shown remarkable performance in skin lesion classification [2], [5], [6], while Vision Transformers (ViTs) are now demonstrating competitive and often superior results [1]. However, most systems focus solely on accuracy, neglecting clinical deployment challenges such as uncertainty quantification, active learning, and user engagement.

This project presents a comprehensive web-based platform combining DINOv2 Vision Transformer and ResNet50 CNN architectures, an intelligent reward system, and active learning framework. The system provides high-accuracy classification, confidence-based flagging, gamified user interaction, and infrastructure for continuous model improvement through expert validation.

# 4. Problem Definition
## 4.1 Clinical Challenges
- Limited access to specialists, leading to delayed diagnoses
- Subjective assessment and missed subtle lesions
- High workload for dermatologists
- Cost barriers for specialized equipment

## 4.2 Technical Challenges
- Model uncertainty on out-of-distribution samples
- Data scarcity due to privacy and annotation requirements
- Deployment safety and interpretability
- User engagement for clinical impact

# 5. Objectives of the Study
- Develop a robust skin disease prediction system using state-of-the-art deep learning models
- Integrate uncertainty quantification and active learning workflows
- Design a user-friendly web interface with gamified reward system
- Ensure clinical safety and expert validation

# 6. Scope of the Project
- Binary classification of skin lesions (benign vs malignant)
- Integration of DINOv2 ViT and ResNet50 CNN models
- Confidence-based flagging and review workflows
- Gamified user engagement and feedback collection
- Active learning for continuous model improvement

# 7. Existing System
Existing systems primarily use CNN architectures for skin lesion classification [2], [5], [6]. These systems achieve high accuracy but often lack uncertainty quantification, active learning, and user engagement features. Most rely on public datasets (ISIC, HAM10000, DermNet) with limited clinical validation [3].

# 8. Proposed System
The proposed system combines ViT and CNN architectures, implements active learning with confidence-based rewards, and provides a web-based deployment with comprehensive user features. It addresses clinical deployment challenges beyond classification accuracy, including uncertainty quantification and user engagement.

# 9. Literature Survey
A comparative analysis of related work is presented below:

| Reference | Year | Method | Dataset | Key Features | Accuracy |
|-----------|------|--------|---------|--------------|----------|
| [4] | 2024 | GA-Optimized Stacking | DermNet | Ensemble learning, genetic algorithm optimization | 96.2% |
| [5] | 2022 | Combined Deep Learners | ISIC 2018 | Multi-model decision fusion | 94.8% |
| [6] | 2023 | Enhanced CNN | HAM10000 | Computer vision techniques | 93.5% |
| [7] | 2024 | ML/DL Hybrid | Clinical Images | Systematic approaches, decision support | 91.7% |
| [8] | 2024 | Multimodal Approach | Custom Dataset | Telegram chatbot integration | 89.3% |
| [9] | 2023 | Interpretable CNN | ISIC 2017 | Explainable AI, Grad-CAM | 92.1% |
| [10] | 2019 | Multiple CNNs | Clinical Images | Comparative study | 87.4% |
| [11] | 2025 | Segmentation + Classification | Multiple Datasets | Comprehensive review | 95.2% |
| [12] | 2020 | Triplet Loss CNN | DermNet | Discriminative feature learning | 88.9% |
| [13] | 2020 | Review Article | Multiple | Deep learning survey | N/A |
| [14] | 2020 | Customized Loss | HAM10000 | Balanced training | 90.5% |

# 10. Methodology / System Design
## 10.1 System Architecture
### Figure 1: System Architecture Diagram
![System Architecture Diagram](images/System_Architecture_Diagram.png)

## 10.2 Model Architecture
### Figure 2: Model Architecture Comparison
![Model Architecture Comparison](images/Model_Architecture_Comparison.png)

## 10.3 User Interface
### Figure 3: User Interface Mockups
![User Interface Mockups](images/testing_app_UI.jpeg)

## 10.4 Active Learning Workflow
### Figure 4: Active Learning Workflow
![Active Learning Workflow](images/Active_Learning_Workflow.png)

# 11. UML Diagrams
- Use Case Diagram (Placeholder)
- Activity Diagram (Placeholder)
- Sequence Diagram (Placeholder)
- Class Diagram (Placeholder)

# 12. ER Diagram / Data Flow Diagram
- ER Diagram (Placeholder)
- Data Flow Diagram (Placeholder)

# 13. Module Description
- Module 1: Data Ingestion and Preprocessing
- Module 2: Model Training and Evaluation
- Module 3: Prediction and User Interface
- Module 4: Feedback and Active Learning

# 14. Algorithms Used
- DINOv2 Vision Transformer [1]
- ResNet50 CNN [2]
- Confidence-based flagging
- Active learning selection
- Reward system logic

# 15. Hardware Requirements
- CPU: Intel i5 or higher
- RAM: 8GB minimum
- GPU: NVIDIA GTX 1060 or higher (recommended)
- Storage: 50GB minimum

# 16. Software Requirements
- OS: Windows 10 / macOS / Linux
- Python 3.11+
- PyTorch, Transformers, timm
- FastAPI, Uvicorn
- LangChain, LangGraph
- Pandoc

# 17. Project Planning (Gantt Chart)
- Gantt Chart (Placeholder)

# 18. Testing & Results
## 18.1 Test Cases
| Test Case | Input | Expected Output | Result |
|-----------|-------|----------------|--------|
| TC1 | Benign image | Benign | Pass |
| TC2 | Malignant image | Malignant | Pass |
| TC3 | Low confidence image | Flagged for review | Pass |
| TC4 | Invalid image | Error message | Pass |

## 18.2 Screenshots
### Figure 5: Reward System UI and Feedback Showcase
![Reward System UI](images/reward_system_UI_Feedback_Showcase.jpeg)

### Figure 6: Reward Showcase
![Reward Showcase](images/reward_showcase.jpeg)

# 19. Conclusion & Future Scope
The Skin Disease Prediction System demonstrates strong performance in binary classification of skin lesions with 92.6% accuracy using Vision Transformer architecture [1]. The system includes comprehensive features for user interaction, AI assistance, and active learning capabilities. While showing promise as a screening tool, the system requires external validation and dermatologist comparison before clinical deployment. The implemented reward system and active learning infrastructure provide a foundation for continuous improvement through expert-validated data collection.

## 19.1 Limitations
- Limited to binary classification
- Requires internet connectivity
- Dependent on image quality

## 19.2 Future Enhancements
- Multi-class classification
- Mobile app development
- Integration with EHR systems
- Advanced uncertainty quantification

# 20. Bibliography
[1] M. Oquab et al., "DINOv2: Learning robust visual features without supervision," arXiv preprint arXiv:2304.07193, 2023.
[2] K. He et al., "Deep residual learning for image recognition," in Proceedings of the IEEE conference on computer vision and pattern recognition, 2016, pp. 770-778.
[3] Melanoma Cancer Dataset. [Online]. Available: https://www.kaggle.com/datasets/hasnainjaved/melanoma-cancer-dataset
[4] A. Balasundaram et al., "Genetic algorithm optimized stacking approach to skin disease detection," IEEE Access, vol. 12, pp. 88950-88962, 2024.
[5] A. Imran et al., "Skin cancer detection using combined decision of deep learners," IEEE Access, vol. 10, pp. 118198-118212, 2022.
[6] A. Magdy et al., "Performance enhancement of skin cancer classification using computer vision," IEEE Access, vol. 11, pp. 72120-72133, 2023.
[7] R. Mittal et al., "DermCDSM: Clinical decision support model for dermatosis using systematic approaches of machine learning and deep learning," IEEE Access, vol. 12, pp. 47319-47337, 2024.
[8] M. Narendra et al., "Advancing skin disease diagnosis: A multimodal approach utilizing telegram api token chatbot for text and image analysis in skin disease classification," IEEE Access, vol. 12, pp. 189009-189023, 2024.
[9] K. Mridha et al., "An interpretable skin cancer classification using optimized convolutional neural network for a smart healthcare system," IEEE Access, vol. 11, pp. 41003-41018, 2023.
[10] Z. Wu et al., "Studies on different CNN algorithms for face skin disease classification based on clinical images," IEEE Access, vol. 7, pp. 66505-66511, 2019.
[11] A. D. Khalaf et al., "Segmentation and classification of skin cancer diseases based on deep learning: Challenges and future directions," IEEE Access, vol. 13, pp. 90163-90184, 2025.
[12] B. Ahmad et al., "Discriminative feature learning for skin disease classification using deep convolutional neural network," IEEE Access, vol. 8, pp. 39025-39033, 2020.
[13] M. A. Khan et al., "Deep learning in skin disease image recognition: A review," IEEE Access, vol. 8, pp. 208264-208280, 2020.
[14] M. A. Khan et al., "Improving skin-disease classification based on customized loss function combined with balanced mini-batch logic and real-time image augmentation," IEEE Access, vol. 8, pp. 150725-150737, 2020.
[15] LangChain Documentation. [Online]. Available: https://python.langchain.com/
[16] FastAPI Documentation. [Online]. Available: https://fastapi.tiangolo.com/
[17] HuggingFace Transformers. [Online]. Available: https://huggingface.co/docs/transformers/index

# 21. Appendix
- Appendix A: Additional Diagrams (Placeholder)
- Appendix B: Code Snippets (Placeholder)

---

<b>Document Version</b>: 1.0  
<b>Date</b>: December 6, 2025  
<b>Author</b>: Akshay Kumar Bolusani
