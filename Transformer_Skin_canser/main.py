import random
from fastapi import FastAPI, File, UploadFile, HTTPException, Query, Form
from fastapi.responses import JSONResponse
import torch
from torchvision import transforms
from PIL import Image
from transformers import Dinov2ForImageClassification
import timm
import uvicorn
import os
from dotenv import load_dotenv
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import csv
from datetime import datetime
import shutil
from pathlib import Path

# Import RL agent
from rl_agent import get_rl_agent

# Groq + LangChain imports
from langchain_groq import ChatGroq
from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver


class NextChat(BaseModel):
    message: str
    thread_id: int

class FeedbackData(BaseModel):
    image_name: str
    feedback: str

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Ensure directories exist
FEEDBACK_DIR = Path("Feedback")
FEEDBACK_DIR.mkdir(exist_ok=True)

HISTORY_CSV = "prediction_history.csv"

# Initialize CSV if it doesn't exist
if not os.path.exists(HISTORY_CSV):
    with open(HISTORY_CSV, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['timestamp', 'image_name', 'model_used', 'prediction', 'probability', 'ai_response', 'feedback', 'reward_points', 'confidence_level', 'needs_review', 'selected_by_rl', 'rl_state', 'used_for_training'])

load_dotenv()
os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")

llm = ChatGroq(
    model="llama-3.1-8b-instant"
)

checkpointer = InMemorySaver()
agent = create_agent(llm, checkpointer=checkpointer)

def query_groq(user_message: str, thread_id: int):
    """Send a message to the LLM with conversation memory."""
    messages = [
        ("system", "You are a helpful medical assistant that gives short, clear answers. Dont say no just answer with precautions according to user query"),
        ("human", user_message)
    ]

    response = agent.invoke(
        {"messages": messages},
        config={"configurable": {"thread_id": thread_id}}
    )

    return response["messages"][-1].content  # Get last AI message


preprocess = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    )
])


model_dino = Dinov2ForImageClassification.from_pretrained(
    "facebook/dinov2-base",
    num_labels=1
)
model_dino.classifier = torch.nn.Linear(model_dino.classifier.in_features, 1)
model_dino.load_state_dict(torch.load("model/dinov2_finetuned.pth", map_location=device))
model_dino.to(device)
model_dino.eval()


model_resnet = timm.create_model("resnet50", pretrained=False, num_classes=1)
model_resnet.load_state_dict(torch.load("model/model_weights_RESNET50.pth", map_location=device))
model_resnet.to(device)
model_resnet.eval()


app = FastAPI(title="Skin Cancer Detection + Chatbot")

# Mount static files
app.mount("/feedback", StaticFiles(directory="Feedback"), name="feedback")

@app.get("/")
def root():
    return FileResponse("static/index.html")



def run_inference(model, tensor):
    with torch.no_grad():
        outputs = model(tensor)

        logits = outputs.logits if hasattr(outputs, "logits") else outputs
        prob = torch.sigmoid(logits).item()
        pred = 1 if prob > 0.5 else 0

    return pred, prob



@app.post("/predict")
async def predict(
    file: UploadFile = File(...),
    model: str = Query("dino", enum=["dino", "resnet"])
):
    try:
        image = Image.open(file.file).convert("RGB")
    except:
        raise HTTPException(status_code=400, detail="Invalid image file")

    # Save image to Feedback folder
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_ext = os.path.splitext(file.filename)[1] or ".jpg"
    saved_filename = f"{timestamp}{file_ext}"
    saved_path = FEEDBACK_DIR / saved_filename
    
    image.save(saved_path)

    # RL Agent model selection
    selected_by_rl = False
    rl_state = None
    
    if model == "auto":
        # Let RL agent choose the model
        rl = get_rl_agent()
        rl_model_name = rl.select_model(str(saved_path), explore=True)
        model = "dino" if rl_model_name == "DINOv2" else "resnet"
        # RL is only used for reward logic now
        selected_by_rl = False
        rl_state = None
    label = "Malignant" if pred == 1 else "Benign"

    # Reward system based on confidence
    reward_points = 0
    confidence_level = "Low"
    needs_review = False
    
    if prob > 0.7:  # High confidence
        reward_points = 1
        confidence_level = "High"
    elif prob < 0.3:  # Very low confidence (opposite class likely)
        if (1 - prob) > 0.7:
            reward_points = 1
            confidence_level = "High"
    else:
        confidence_level = "Medium"
        needs_review = True  # Flag for expert review

    thread_id = random.randint(1000, 999999)

    # Ask Groq LLM to respond
    prompt = f"My skin condition was classified as {label} with probability {prob:.4f}. Give advice."
    ai_response = query_groq(prompt, thread_id)

    # Log to CSV with reward data
    with open(HISTORY_CSV, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            saved_filename,
            "DINOv2" if model == "dino" else "ResNet50",
            label,
            f"{prob:.4f}",
            ai_response,
            "",  # feedback placeholder
            reward_points,
            confidence_level,
            needs_review,
            selected_by_rl,
            rl_state or "",
            False  # used_for_training
        ])

    return JSONResponse({
        "model_used": "DINOv2" if model == "dino" else "ResNet50",
        "prediction": label,
        "probability": prob,
        "raw_output": pred,
        "AI_response": ai_response,
        "thread_id": thread_id,
        "image_name": saved_filename,
        "reward_points": reward_points,
        "confidence_level": confidence_level,
        "needs_review": needs_review,
        "selected_by_rl": selected_by_rl,
        "rl_state": rl_state
    })


@app.post("/chat")
async def chat(chat : NextChat):
    """
    Continue chatting with the AI using a persistent conversation thread.
    """
    ai_response = query_groq(chat.message, chat.thread_id)
    return {"thread_id": chat.thread_id, "response": ai_response}


@app.post("/feedback")
async def submit_feedback(feedback_data: FeedbackData):
    """
    Update the CSV with user feedback for a specific prediction.
    """
    try:
        # Read all rows
        rows = []
        with open(HISTORY_CSV, 'r', newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            rows = list(reader)
        
        # Update the row with matching image_name
        updated = False
        for i, row in enumerate(rows):
            if i > 0 and row[1] == feedback_data.image_name:  # Skip header
                row[6] = feedback_data.feedback
                updated = True
                break
        
        # Write back
        if updated:
            with open(HISTORY_CSV, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerows(rows)
            return {"status": "success", "message": "Feedback saved"}
        else:
            return {"status": "error", "message": "Image not found in history"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/history")
async def get_history():
    """
    Retrieve all prediction history from CSV.
    """
    try:
        history = []
        with open(HISTORY_CSV, 'r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                history.append(row)
        return {"history": history[::-1]}  # Most recent first
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/metrics")
async def get_metrics():
    """
    Calculate metrics from prediction history including reward system.
    """
    try:
        total = 0
        models_used = {"DINOv2": 0, "ResNet50": 0}
        predictions = {"Malignant": 0, "Benign": 0}
        total_rewards = 0
        confidence_dist = {"High": 0, "Medium": 0, "Low": 0}
        needs_review_count = 0
        
        with open(HISTORY_CSV, 'r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                total += 1
                models_used[row['model_used']] = models_used.get(row['model_used'], 0) + 1
                predictions[row['prediction']] = predictions.get(row['prediction'], 0) + 1
                
                # Reward system metrics
                if 'reward_points' in row and row['reward_points']:
                    total_rewards += int(row['reward_points'])
                if 'confidence_level' in row and row['confidence_level']:
                    confidence_dist[row['confidence_level']] = confidence_dist.get(row['confidence_level'], 0) + 1
                if 'needs_review' in row and row['needs_review'] == 'True':
                    needs_review_count += 1
        
        high_confidence_rate = (confidence_dist["High"] / total * 100) if total > 0 else 0
        
        # Get RL agent stats
        rl = get_rl_agent()
        rl_stats = rl.get_stats()
        
        return {
            "total_predictions": total,
            "models_used": models_used,
            "predictions_breakdown": predictions,
            "reward_system": {
                "total_reward_points": total_rewards,
                "high_confidence_predictions": confidence_dist["High"],
                "medium_confidence_predictions": confidence_dist["Medium"],
                "low_confidence_predictions": confidence_dist["Low"],
                "high_confidence_rate": f"{high_confidence_rate:.1f}%",
                "predictions_needing_review": needs_review_count
            },
            "rl_agent": rl_stats,
            "accuracy_note": "Accuracy can only be determined with ground truth labels"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/train_agent")
async def train_agent():
    """
    Train the RL agent from historical prediction data.
    This reads the CSV file and updates Q-values based on past predictions.
    Only trains on data that hasn't been used for training yet.
    """
    try:
        rl = get_rl_agent()
        trained_count = rl.train_from_history(HISTORY_CSV)
        
        # Mark trained rows in CSV
        if trained_count > 0:
            rows = []
            with open(HISTORY_CSV, 'r', newline='', encoding='utf-8') as f:
                reader = csv.reader(f)
                rows = list(reader)
            
            # Update 'used_for_training' column for trained rows
            header = rows[0]
            if 'used_for_training' in header:
                training_col_idx = header.index('used_for_training')
                for i in range(1, len(rows)):
                    if len(rows[i]) > training_col_idx:
                        # Mark as trained if not already marked
                        if rows[i][training_col_idx] in ['', 'False', '0']:
                            rows[i][training_col_idx] = 'True'
                
                # Write back
                with open(HISTORY_CSV, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerows(rows)
        
        return {
            "status": "success",
            "message": f"RL agent trained on {trained_count} new predictions",
            "stats": rl.get_stats()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)