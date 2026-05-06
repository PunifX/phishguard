from huggingface_hub import HfApi
from pathlib import Path

api = HfApi()

MODELS_DIR = Path("d:/codes/project/AI/phishguard/src/models")

# Create the repo first (safe to run even if it already exists)
api.create_repo(repo_id="PunifX/phishguard-models", repo_type="model", exist_ok=True)
print("Repo ready.")

# Now upload
api.upload_file(
    path_or_fileobj=str(MODELS_DIR / "phishguard_model.pkl"),
    path_in_repo="phishguard_model.pkl",
    repo_id="PunifX/phishguard-models",
    repo_type="model"
)
print("✓ Random Forest uploaded")

api.upload_file(
    path_or_fileobj=str(MODELS_DIR / "phishguard_xgb_model.pkl"),
    path_in_repo="phishguard_xgb_model.pkl",
    repo_id="PunifX/phishguard-models",
    repo_type="model"
)
print("✓ XGBoost uploaded")

api.upload_file(
    path_or_fileobj=str(MODELS_DIR / "phishguard_linear_reg_model.pkl"),
    path_in_repo="phishguard_linear_reg_model.pkl",
    repo_id="PunifX/phishguard-models",
    repo_type="model"
)
print("✓ Logistic Regression uploaded")

print("\nAll done! Check: https://huggingface.co/PunifX/phishguard-models")