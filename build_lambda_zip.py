from pathlib import Path
import zipfile

ROOT = Path(__file__).parent
OUT = ROOT / "lambda.zip"

# Orígenes del ZIP:
APP_DIR = ROOT / "app"
WRAPPER_DIR = ROOT / "lambda_wrapper"  # solo contiene main.py

def add_folder(z: zipfile.ZipFile, folder: Path, base_in_zip: str = ""):
    for p in folder.rglob("*"):
        if p.is_dir():
            continue
        rel = p.relative_to(folder).as_posix()
        arcname = f"{base_in_zip}{rel}" if base_in_zip else rel
        z.write(p, arcname)

def build_zip():
    if not APP_DIR.exists():
        raise FileNotFoundError(f"Missing {APP_DIR}")
    if not (WRAPPER_DIR / "main.py").exists():
        raise FileNotFoundError("Missing lambda_wrapper/main.py")

    if OUT.exists():
        OUT.unlink()

    with zipfile.ZipFile(OUT, "w", compression=zipfile.ZIP_DEFLATED) as z:
        # wrapper main.py goes to root of zip
        z.write((WRAPPER_DIR / "main.py"), "main.py")
        # app package goes into app/ in zip
        add_folder(z, APP_DIR, base_in_zip="app/")

    print(f"Built {OUT}")

if __name__ == "__main__":
    build_zip()
