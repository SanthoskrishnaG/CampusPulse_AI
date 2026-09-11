import numpy as np
import joblib
from pathlib import Path
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score
from ml.registry.registry import ModelRegistry

MEAL_TYPE_MAP = {'BREAKFAST': 0, 'LUNCH': 1, 'SNACKS': 2, 'DINNER': 3}

def generate_canteen_demand_data(n_samples=700):
    np.random.seed(42)
    day_of_week = np.random.randint(0, 7, size=n_samples) # 0=Mon, 6=Sun
    meal_type = np.random.randint(0, 4, size=n_samples)
    is_event = np.random.choice([0, 1], p=[0.85, 0.15], size=n_samples)
    is_weekend = np.where(day_of_week >= 5, 1, 0)
    student_base = np.random.normal(520, 20, size=n_samples)

    # Realistic base demands
    base_demand = np.where(meal_type == 1, 380, np.where(meal_type == 0, 180, np.where(meal_type == 2, 220, 160)))
    
    # Event surges demand by 25%, weekend drops weekday student count
    demand = base_demand * np.where(is_weekend == 1, 0.45, 1.0) * (1.0 + is_event * 0.28)
    demand += np.random.normal(0, 15, size=n_samples)
    demand = np.clip(demand.astype(int), 30, 600)

    X = np.column_stack([day_of_week, meal_type, is_event, is_weekend, student_base])
    y = demand
    return X, y

def train_canteen_demand_model():
    X, y = generate_canteen_demand_data()
    model = RandomForestRegressor(n_estimators=100, max_depth=6, random_state=42)
    model.fit(X, y)

    preds = model.predict(X)
    mae = mean_absolute_error(y, preds)
    r2 = r2_score(y, preds)

    metrics = {
        'mae': round(float(mae), 2),
        'r2_score': round(float(r2), 4)
    }

    models_dir = Path("models")
    models_dir.mkdir(parents=True, exist_ok=True)
    model_path = models_dir / "canteen_demand_model.joblib"
    joblib.dump({'model': model, 'metrics': metrics}, model_path)

    ModelRegistry.register_model(
        model_name="Canteen_Food_Demand_Forecaster",
        version="1.0.0",
        algorithm="RandomForestRegressor",
        metrics=metrics,
        feature_list=['day_of_week', 'meal_type', 'is_event', 'is_weekend', 'student_base'],
        model_path=model_path,
        description="Predicts student food demand per meal type to minimize canteen kitchen leftover waste."
    )
    print(f"Trained Canteen Demand Model (R2: {r2:.4f}, MAE: {mae:.2f})")
    return model, metrics

if __name__ == '__main__':
    train_canteen_demand_model()
