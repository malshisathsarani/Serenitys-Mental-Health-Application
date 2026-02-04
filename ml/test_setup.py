"""
ML Module Configuration Test
Verify the ML module is properly configured
"""
import sys
from pathlib import Path

def test_structure():
    """Test if all required directories exist"""
    ml_root = Path(__file__).parent
    
    required_dirs = [
        'config',
        'data/raw',
        'data/processed',
        'models',
        'src/training',
        'src/preprocessing',
        'src/evaluation',
        'src/utils',
        'scripts',
        'notebooks',
        'tests',
        'logs'
    ]
    
    print("🔍 Checking ML Module Structure...")
    print("="*60)
    
    all_exist = True
    for dir_path in required_dirs:
        full_path = ml_root / dir_path
        exists = full_path.exists()
        status = "✅" if exists else "❌"
        print(f"{status} {dir_path}")
        if not exists:
            all_exist = False
    
    print("="*60)
    
    if all_exist:
        print("✅ All required directories exist!")
    else:
        print("❌ Some directories are missing!")
    
    return all_exist

def test_config():
    """Test if configuration can be imported"""
    print("\n🔍 Testing Configuration...")
    print("="*60)
    
    try:
        sys.path.insert(0, str(Path(__file__).parent))
        from config.config import (
            ML_ROOT, DATA_DIR, MODELS_DIR,
            MODEL_CONFIG, TRAINING_CONFIG, PREPROCESSING_CONFIG
        )
        
        print("✅ Configuration imported successfully")
        print(f"   ML_ROOT: {ML_ROOT}")
        print(f"   DATA_DIR: {DATA_DIR}")
        print(f"   MODELS_DIR: {MODELS_DIR}")
        print("="*60)
        return True
    except Exception as e:
        print(f"❌ Configuration import failed: {e}")
        print("="*60)
        return False

def test_imports():
    """Test if main modules can be imported"""
    print("\n🔍 Testing Module Imports...")
    print("="*60)
    
    modules = [
        ('src.training.train_baseline', 'MentalHealthClassifier'),
        ('src.preprocessing.combine_csv', 'DataCombiner'),
        ('src.evaluation.model_evaluator', 'ModelEvaluator'),
        ('scripts.predict', 'MentalHealthPredictor'),
        ('src.utils.helpers', 'save_json')
    ]
    
    all_imported = True
    for module_name, class_name in modules:
        try:
            module = __import__(module_name, fromlist=[class_name])
            cls = getattr(module, class_name)
            print(f"✅ {module_name}.{class_name}")
        except Exception as e:
            print(f"❌ {module_name}.{class_name} - {str(e)}")
            all_imported = False
    
    print("="*60)
    
    if all_imported:
        print("✅ All modules imported successfully!")
    else:
        print("❌ Some modules failed to import!")
    
    return all_imported

def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("🚀 ML Module Configuration Test")
    print("="*60 + "\n")
    
    structure_ok = test_structure()
    config_ok = test_config()
    imports_ok = test_imports()
    
    print("\n" + "="*60)
    print("📊 Test Results Summary")
    print("="*60)
    print(f"Structure: {'✅ PASS' if structure_ok else '❌ FAIL'}")
    print(f"Configuration: {'✅ PASS' if config_ok else '❌ FAIL'}")
    print(f"Imports: {'✅ PASS' if imports_ok else '❌ FAIL'}")
    print("="*60)
    
    if structure_ok and config_ok and imports_ok:
        print("\n🎉 All tests passed! ML Module is properly configured!")
        print("\nNext steps:")
        print("1. Install dependencies: pip install -r requirements.txt")
        print("2. Train model: python train.py")
        print("3. Make predictions: python predict.py")
    else:
        print("\n⚠️  Some tests failed. Please check the errors above.")
    
    print("\n")

if __name__ == "__main__":
    main()
