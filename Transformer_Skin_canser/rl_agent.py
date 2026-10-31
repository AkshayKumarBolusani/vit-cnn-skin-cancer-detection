"""
Reinforcement Learning Model Selection Agent

This module implements a Q-learning agent that learns to select the optimal model
(DINOv2 or ResNet50) for skin lesion classification based on image features.

State Space: Image features (brightness, contrast, complexity, color distribution)
Action Space: {0: DINOv2, 1: ResNet50}
Reward Function: Based on prediction confidence and expert feedback
Algorithm: Q-learning with epsilon-greedy exploration
"""

import numpy as np
import pickle
import os
from pathlib import Path
from PIL import Image
from typing import Tuple, Dict, Any
import json
from datetime import datetime


class QLearningModelSelector:
    """Q-learning agent for intelligent model selection."""
    
    def __init__(
        self, 
        learning_rate: float = 0.1,
        discount_factor: float = 0.95,
        epsilon: float = 0.2,
        epsilon_decay: float = 0.995,
        epsilon_min: float = 0.01,
        state_bins: int = 5
    ):
        """
        Initialize the Q-learning agent.
        
        Args:
            learning_rate: Alpha parameter for Q-value updates
            discount_factor: Gamma parameter for future reward consideration
            epsilon: Initial exploration rate
            epsilon_decay: Rate at which epsilon decreases
            epsilon_min: Minimum epsilon value
            state_bins: Number of bins for discretizing continuous features
        """
        self.lr = learning_rate
        self.gamma = discount_factor
        self.epsilon = epsilon
        self.epsilon_decay = epsilon_decay
        self.epsilon_min = epsilon_min
        self.state_bins = state_bins
        
        # Action space: 0 = DINOv2, 1 = ResNet50
        self.actions = ['DINOv2', 'ResNet50']
        self.n_actions = len(self.actions)
        
        # Q-table: state -> [Q(s, DINOv2), Q(s, ResNet50)]
        # State is represented as a tuple of discretized features
        self.q_table = {}
        
        # Performance tracking
        self.action_counts = {'DINOv2': 0, 'ResNet50': 0}
        self.total_reward = 0.0
        self.episode_count = 0
        
        # File for persisting the agent
        self.save_path = Path('model/rl_agent_state.pkl')
        
        # Load existing agent if available
        self.load()
    
    def extract_features(self, image_path: str) -> np.ndarray:
        """
        Extract features from an image to form the state representation.
        
        Features extracted:
        - Brightness (mean luminance)
        - Contrast (std of luminance)
        - Color variance (std across RGB channels)
        - Image complexity (edge density approximation)
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Feature vector as numpy array
        """
        try:
            img = Image.open(image_path).convert('RGB')
            img_array = np.array(img) / 255.0  # Normalize to [0, 1]
            
            # Feature 1: Brightness (mean luminance)
            # Using standard luminance formula
            luminance = 0.299 * img_array[:,:,0] + 0.587 * img_array[:,:,1] + 0.114 * img_array[:,:,2]
            brightness = np.mean(luminance)
            
            # Feature 2: Contrast (std of luminance)
            contrast = np.std(luminance)
            
            # Feature 3: Color variance (how much color varies)
            color_variance = np.mean([np.std(img_array[:,:,i]) for i in range(3)])
            
            # Feature 4: Complexity (approximated by gradient magnitude)
            # Simple edge detection approximation
            grad_x = np.abs(np.diff(luminance, axis=1))
            grad_y = np.abs(np.diff(luminance, axis=0))
            complexity = (np.mean(grad_x) + np.mean(grad_y)) / 2
            
            features = np.array([brightness, contrast, color_variance, complexity])
            return features
            
        except Exception as e:
            print(f"Error extracting features: {e}")
            # Return default features if extraction fails
            return np.array([0.5, 0.2, 0.2, 0.1])
    
    def discretize_state(self, features: np.ndarray) -> Tuple:
        """
        Discretize continuous features into bins to create discrete state.
        
        Args:
            features: Continuous feature vector
            
        Returns:
            Tuple representing discretized state
        """
        # Define feature ranges (empirically determined)
        feature_ranges = [
            (0.0, 1.0),   # Brightness
            (0.0, 0.5),   # Contrast
            (0.0, 0.5),   # Color variance
            (0.0, 0.3)    # Complexity
        ]
        
        discrete_state = []
        for i, (feat_min, feat_max) in enumerate(feature_ranges):
            # Clip feature to range and bin it
            feat_clipped = np.clip(features[i], feat_min, feat_max)
            bin_idx = int((feat_clipped - feat_min) / (feat_max - feat_min) * (self.state_bins - 1))
            bin_idx = min(bin_idx, self.state_bins - 1)  # Ensure within bounds
            discrete_state.append(bin_idx)
        
        return tuple(discrete_state)
    
    def get_q_values(self, state: Tuple) -> np.ndarray:
        """
        Get Q-values for a given state.
        
        Args:
            state: Discretized state tuple
            
        Returns:
            Array of Q-values for each action
        """
        if state not in self.q_table:
            # Initialize Q-values optimistically (slightly favor exploration)
            self.q_table[state] = np.zeros(self.n_actions)
        
        return self.q_table[state]
    
    def select_action(self, state: Tuple, explore: bool = True) -> int:
        """
        Select an action using epsilon-greedy policy.
        
        Args:
            state: Current state
            explore: Whether to use epsilon-greedy (False for pure exploitation)
            
        Returns:
            Action index (0 for DINOv2, 1 for ResNet50)
        """
        if explore and np.random.random() < self.epsilon:
            # Exploration: random action
            action = np.random.randint(0, self.n_actions)
        else:
            # Exploitation: best action
            q_values = self.get_q_values(state)
            action = np.argmax(q_values)
        
        return action
    
    def select_model(self, image_path: str, explore: bool = True) -> str:
        """
        Select which model to use for a given image.
        
        Args:
            image_path: Path to the image
            explore: Whether to explore (set False for production)
            
        Returns:
            Model name ('DINOv2' or 'ResNet50')
        """
        features = self.extract_features(image_path)
        state = self.discretize_state(features)
        action = self.select_action(state, explore=explore)
        
        model_name = self.actions[action]
        self.action_counts[model_name] += 1
        
        return model_name
    
    def update_q_value(
        self, 
        state: Tuple, 
        action: int, 
        reward: float, 
        next_state: Tuple = None
    ):
        """
        Update Q-value using the Q-learning update rule.
        
        Q(s,a) = Q(s,a) + α * [reward + γ * max(Q(s',a')) - Q(s,a)]
        
        Args:
            state: Current state
            action: Action taken
            reward: Reward received
            next_state: Next state (None for terminal states)
        """
        current_q = self.get_q_values(state)[action]
        
        if next_state is not None:
            # Non-terminal: consider future rewards
            max_next_q = np.max(self.get_q_values(next_state))
            target = reward + self.gamma * max_next_q
        else:
            # Terminal state: only immediate reward
            target = reward
        
        # Q-learning update
        new_q = current_q + self.lr * (target - current_q)
        self.q_table[state][action] = new_q
        
        # Update statistics
        self.total_reward += reward
        self.episode_count += 1
        
        # Decay epsilon
        self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)
    
    def calculate_reward(
        self, 
        prediction: str, 
        probability: float, 
        expert_feedback: str = None,
        ground_truth: str = None
    ) -> float:
        """
        Calculate reward based on prediction quality and expert feedback.
        
        Reward structure:
        - High confidence correct prediction: +1.0
        - Medium confidence correct: +0.5
        - Low confidence: -0.2 (needs review)
        - Wrong prediction: -1.0
        - No feedback yet: Based on confidence only
        
        Args:
            prediction: Model's prediction
            probability: Prediction confidence
            expert_feedback: Optional expert correction
            ground_truth: Optional ground truth label
            
        Returns:
            Reward value
        """
        # If we have ground truth or expert feedback, use it
        if ground_truth is not None:
            is_correct = (prediction.lower() == ground_truth.lower())
        elif expert_feedback is not None and expert_feedback.strip():
            # Expert provided feedback, assume it's correction if different
            is_correct = (prediction.lower() in expert_feedback.lower())
        else:
            # No feedback yet, reward based on confidence
            if probability > 0.7:
                return 0.5  # Optimistic reward for high confidence
            elif probability > 0.5:
                return 0.1  # Small positive for medium confidence
            else:
                return -0.2  # Penalty for low confidence
        
        # With ground truth/feedback
        if is_correct:
            if probability > 0.7:
                return 1.0  # High confidence correct
            else:
                return 0.5  # Low confidence correct (lucky guess?)
        else:
            return -1.0  # Wrong prediction
    
    def train_from_history(self, history_file: str = 'prediction_history.csv') -> int:
        """
        Train the agent from historical prediction data.
        
        Reads the CSV file and updates Q-values based on past predictions.
        Only trains on data that hasn't been used for training yet.
        
        Args:
            history_file: Path to the prediction history CSV
            
        Returns:
            Number of new predictions trained on
        """
        import csv
        
        if not os.path.exists(history_file):
            print("No history file found for training.")
            return 0
        
        trained_count = 0
        with open(history_file, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    # Skip if already used for training
                    if row.get('used_for_training', 'False') == 'True':
                        continue
                    
                    # Extract data from CSV
                    image_name = row['image_name']
                    image_path = f"Feedback/{image_name}"
                    
                    if not os.path.exists(image_path):
                        continue
                    
                    model_used = row['model_used']
                    prediction = row['prediction']
                    probability = float(row['probability'])
                    feedback = row.get('feedback', '')
                    
                    # Extract features and get state
                    features = self.extract_features(image_path)
                    state = self.discretize_state(features)
                    
                    # Determine action (which model was used)
                    action = 0 if model_used == 'DINOv2' else 1
                    
                    # Calculate reward
                    reward = self.calculate_reward(prediction, probability, feedback)
                    
                    # Update Q-value
                    self.update_q_value(state, action, reward)
                    trained_count += 1
                    
                except Exception as e:
                    print(f"Error processing row: {e}")
                    continue
        
        print(f"Trained on {trained_count} new predictions.")
        print(f"Total episodes: {self.episode_count}, Avg reward: {self.total_reward / max(1, self.episode_count):.3f}")
        print(f"Epsilon: {self.epsilon:.3f}")
        
        # Save updated agent
        self.save()
        
        return trained_count
    
    def save(self):
        """Save the agent's state to disk."""
        self.save_path.parent.mkdir(exist_ok=True)
        
        state = {
            'q_table': self.q_table,
            'epsilon': self.epsilon,
            'action_counts': self.action_counts,
            'total_reward': self.total_reward,
            'episode_count': self.episode_count,
            'hyperparameters': {
                'lr': self.lr,
                'gamma': self.gamma,
                'epsilon_decay': self.epsilon_decay,
                'epsilon_min': self.epsilon_min,
                'state_bins': self.state_bins
            }
        }
        
        with open(self.save_path, 'wb') as f:
            pickle.dump(state, f)
    
    def load(self):
        """Load the agent's state from disk."""
        if self.save_path.exists():
            try:
                with open(self.save_path, 'rb') as f:
                    state = pickle.load(f)
                
                self.q_table = state['q_table']
                self.epsilon = state['epsilon']
                self.action_counts = state['action_counts']
                self.total_reward = state['total_reward']
                self.episode_count = state['episode_count']
                
                print(f"Loaded RL agent: {len(self.q_table)} states, {self.episode_count} episodes trained")
            except Exception as e:
                print(f"Error loading agent state: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get agent statistics."""
        total_actions = sum(self.action_counts.values())
        
        return {
            'total_episodes': self.episode_count,
            'total_reward': round(self.total_reward, 3),
            'avg_reward': round(self.total_reward / max(1, self.episode_count), 3),
            'epsilon': round(self.epsilon, 4),
            'states_explored': len(self.q_table),
            'action_distribution': {
                model: f"{count} ({100*count/max(1, total_actions):.1f}%)"
                for model, count in self.action_counts.items()
            },
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }


# Global agent instance
rl_agent = None

def get_rl_agent() -> QLearningModelSelector:
    """Get or create the global RL agent instance."""
    global rl_agent
    if rl_agent is None:
        rl_agent = QLearningModelSelector(
            learning_rate=0.1,
            discount_factor=0.95,
            epsilon=0.2,  # 20% exploration initially
            epsilon_decay=0.995,
            epsilon_min=0.05,  # Always maintain 5% exploration
            state_bins=5
        )
    return rl_agent
