import gradio as gr
import torch
from torchvision import transforms
from PIL import Image
from transformers import Dinov2ForImageClassification
import timm
import os
from langchain_groq import ChatGroq
from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver
import random

# Set up device
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Initialize Groq API
os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY", "")
llm = ChatGroq(model="llama-3.1-8b-instant")
checkpointer = InMemorySaver()
agent = create_agent(llm, checkpointer=checkpointer)

# Image preprocessing
preprocess = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    )
])

# Load DINOv2 model
model_dino = Dinov2ForImageClassification.from_pretrained(
    "facebook/dinov2-base",
    num_labels=1
)
model_dino.classifier = torch.nn.Linear(model_dino.classifier.in_features, 1)
model_dino.load_state_dict(torch.load("dinov2_finetuned.pth", map_location=device))
model_dino.to(device)
model_dino.eval()

# Load ResNet50 model
model_resnet = timm.create_model("resnet50", pretrained=False, num_classes=1)
model_resnet.load_state_dict(torch.load("model_weights_RESNET50.pth", map_location=device))
model_resnet.to(device)
model_resnet.eval()

def query_groq(user_message: str, thread_id: int):
    """Send a message to the LLM with conversation memory."""
    messages = [
        ("system", "You are a helpful medical assistant that gives short, clear answers. Don't say no, just answer with precautions according to user query"),
        ("human", user_message)
    ]
    response = agent.invoke(
        {"messages": messages},
        config={"configurable": {"thread_id": thread_id}}
    )
    return response["messages"][-1].content

def run_inference(model, tensor):
    with torch.no_grad():
        outputs = model(tensor)
        logits = outputs.logits if hasattr(outputs, "logits") else outputs
        prob = torch.sigmoid(logits).item()
        pred = 1 if prob > 0.5 else 0
    return pred, prob

def predict_skin_condition(image, model_choice):
    """Main prediction function for Gradio interface"""
    if image is None:
        return "Please upload an image", "", ""

    # Map display label to backend value
    if model_choice == "DINOv2 (Vision Transformer)":
        model_backend = "dino"
        selected_model = model_dino
    else:
        model_backend = "resnet"
        selected_model = model_resnet

    # Preprocess image
    img_tensor = preprocess(image).unsqueeze(0).to(device)

    # Run inference
    pred, prob = run_inference(selected_model, img_tensor)
    label = "Malignant" if pred == 1 else "Benign"
    
    # Get AI advice
    thread_id = random.randint(1000, 999999)
    prompt = f"My skin condition was classified as {label} with probability {prob:.4f}. Give advice."
    ai_response = query_groq(prompt, thread_id)
    
    # Format results
    result = f"### 🔬 Prediction: **{label}**\n\n"
    result += f"**Confidence:** {prob*100:.2f}%\n\n"
    result += f"**Model Used:** {'DINOv2' if model_backend == 'dino' else 'ResNet50'}\n\n"
    result += f"---\n\n### 🤖 AI Medical Assistant:\n\n{ai_response}"
    
    return result

# Custom CSS for better styling
custom_css = """
.gradio-container {
    font-family: 'Arial', sans-serif;
}
.output-markdown {
    background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    padding: 20px;
    border-radius: 10px;
}
"""

# Create Gradio interface
with gr.Blocks(css=custom_css, theme=gr.themes.Soft()) as demo:
    gr.Markdown("""
    # 🏥 Skin Disease Prediction System
    ## AI-Powered Melanoma Detection using Vision Transformers
    
    Upload a skin lesion image to get an instant AI-powered analysis using state-of-the-art deep learning models.
    
    ⚠️ **Disclaimer:** This is an AI research tool and NOT a substitute for professional medical diagnosis.
    """)
    
    with gr.Row():
        with gr.Column(scale=1):
            image_input = gr.Image(
                label="📸 Upload Skin Lesion Image",
                type="pil",
                height=400
            )
            
            model_choice = gr.Radio(
                choices=["DINOv2 (Vision Transformer)", "ResNet50 (CNN)"],
                value="DINOv2 (Vision Transformer)",
                label="🧠 Select AI Model",
                info="DINOv2: 92.6% accuracy | ResNet50: 91.8% accuracy"
            )
            
            predict_btn = gr.Button("🔍 Analyze Image", variant="primary", size="lg")
        
        with gr.Column(scale=1):
            output = gr.Markdown(label="📋 Analysis Results")
    
    predict_btn.click(
        fn=predict_skin_condition,
        inputs=[image_input, model_choice],
        outputs=output
    )
    
    gr.Markdown("""
    ---
    ### 📊 Model Performance
    - **DINOv2 (Vision Transformer):** 92.6% Test Accuracy
    - **ResNet50 (CNN):** 91.8% Test Accuracy
    - **Dataset:** 9,605 training images (Melanoma Cancer Dataset)
    
    ### ⚕️ Medical Disclaimer
    This AI system is intended for research and educational purposes only. Always consult with qualified healthcare professionals for medical diagnosis and treatment decisions.
    
    ### 🔒 Privacy
    Images are processed locally and not stored permanently.
    """)

# Launch the app
if __name__ == "__main__":
    demo.launch()
