import numpy as np
import joblib
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, root_mean_squared_error, r2_score
from ml.registry.registry import ModelRegistry

MEAL_TYPE_MAP = {'BREAKFAST': 0, 'LUNCH': 1, 'SNACKS': 2, 'DINNER': 3}

def generate_food_waste_dataset(n_samples=900, random_state=42):
    """
    Simulates institutional dining kitchen waste records.
    Features:
      - meals_prepared (e.g. 150 - 450)
      - predicted_demand (e.g. 140 - 430)
      - meal_type (0=Breakfast, 1=Lunch, 2=Snacks, 3=Dinner)
      - day_of_week (0-6)
      - is_event (0/1)
    Target:
      - leftover_waste_kg (Continuous real kg of organic food waste)
    """
    np.random.seed(random_state)
    meals_prepared = np.random.randint(120, 500, size=n_samples)
    
    # Actual demand tends to be close to or slightly under prepared
    surplus_fraction = np.random.normal(0.06, 0.04, size=n_samples)
    predicted_demand = np.clip((meals_prepared * (1.0 - surplus_fraction)).astype(int), 80, meals_prepared)

    meal_type = np.random.randint(0, 4, size=n_samples)
    day_of_week = np.random.randint(0, 7, size=n_samples)
    is_event = np.random.choice([0, 1], p=[0.85, 0.15], size=n_samples)

    # Overproduction waste (~0.38 kg per unserved meal portion)
    overproduction = np.maximum(0, meals_prepared - predicted_demand) * 0.38
    # Baseline plate scrap & kitchen trimming (higher for Lunch/Dinner)
    baseline_trim = np.where(meal_type == 1, 4.5, np.where(meal_type == 3, 3.8, 1.8))
    event_scrap = is_event * 2.2

    noise = np.random.normal(0, 0.6, size=n_samples)
    waste_kg = np.clip(overproduction + baseline_trim + event_scrap + noise, 0.8, 45.0)

    X = np.column_stack([meals_prepared, predicted_demand, meal_type, day_of_week, is_event])
    y = np.round(waste_kg, 2)
    return X, y

def train_food_waste_model():
    """
    Trains and serializes Gradient Boosting Regressor for kitchen leftover food waste prediction.
    """
    X, y = generate_food_waste_dataset()
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42)

    model = GradientBoostingRegressor(n_estimators=100, max_depth=4, learning_rate=0.08, random_state=42)
    model.fit(X_train, y_train)

    preds = model.predict(X_test)
    mae = mean_absolute_error(y_test, preds)
    rmse = root_mean_squared_error(y_test, preds)
    r2 = r2_score(y_test, preds)

    metrics = {
        'mae': round(float(mae), 2),
        'rmse': round(float(rmse), 2),
        'r2_score': round(float(r2), 4),
        'test_samples': len(y_test)
    }

    models_dir = Path("models")
    models_dir.mkdir(parents=True, exist_ok=True)
    model_path = models_dir / "food_waste_model.joblib"
    joblib.dump({
        'model': model,
        'metrics': metrics,
        'features': ['meals_prepared', 'predicted_demand', 'meal_type', 'day_of_week', 'is_event'],
        'version': '1.0.0'
    }, model_path)

    ModelRegistry.register_model(
        model_name="Food_Waste_Forecaster",
        version="1.0.0",
        task="REGRESSION",
        algorithm="GradientBoostingRegressor",
        metrics=metrics,
        feature_list=['meals_prepared', 'predicted_demand', 'meal_type', 'day_of_week', 'is_event'],
        model_path=model_path,
        description="Predicts expected post-service kitchen food waste (kg) based on overproduction buffer."
    )
    print(f"Food Waste Model Trained: R2={r2:.4f}, MAE={mae:.2f} kg, RMSE={rmse:.2f} kg")
    return model, metrics

if __name__ == '__main__':
    train_food_waste_model()
