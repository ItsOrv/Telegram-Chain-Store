import secrets
import argparse
import hashlib
import base64
from pathlib import Path
from datetime import datetime
import json
from cryptography.fernet import Fernet
from typing import Dict, Optional
import os

class SecretKeyGenerator:
    """پیشرفته‌ترین کلاس برای تولید و مدیریت کلیدهای رمزنگاری"""

    def __init__(self, key_length: int = 32, backup_dir: str = "secrets_backup"):
        self.key_length = key_length
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(exist_ok=True)
        self.key_meta: Dict = {}

    def generate_key(self, method: str = "urlsafe") -> str:
        """
        تولید کلید با روش‌های مختلف:
        - urlsafe: کلید امن URL-safe
        - hex: کلید هگزادسیمال
        - base64: کلید Base64
        - mix: ترکیبی از همه روش‌ها
        """
        if method == "urlsafe":
            key = secrets.token_urlsafe(self.key_length)
        elif method == "hex":
            key = secrets.token_hex(self.key_length)
        elif method == "base64":
            key = base64.b64encode(secrets.token_bytes(self.key_length)).decode()
        elif method == "mix":
            # ترکیب روش‌های مختلف برای امنیت بیشتر
            base_key = secrets.token_bytes(self.key_length)
            key = hashlib.sha256(base_key).hexdigest()
        else:
            raise ValueError("Invalid key generation method")

        # ذخیره متادیتای کلید
        self.key_meta = {
            "method": method,
            "length": self.key_length,
            "created_at": datetime.now().isoformat(),
            "sha256": hashlib.sha256(key.encode()).hexdigest(),
            "strength_score": self._calculate_strength(key)
        }

        return key

    def _calculate_strength(self, key: str) -> float:
        """محاسبه امتیاز قدرت کلید"""
        score = 0.0
        
        # طول کلید
        score += min(len(key) / 32.0, 1.0) * 0.3
        
        # تنوع کاراکترها
        unique_chars = len(set(key))
        score += min(unique_chars / 64.0, 1.0) * 0.3
        
        # آنتروپی
        entropy = self._calculate_entropy(key)
        score += min(entropy / 4.0, 1.0) * 0.4
        
        return round(score * 100, 2)

    def _calculate_entropy(self, key: str) -> float:
        """محاسبه آنتروپی Shannon برای کلید"""
        import math
        from collections import Counter
        
        entropy = 0
        key_len = len(key)
        
        for count in Counter(key).values():
            prob = count / key_len
            entropy -= prob * math.log2(prob)
            
        return entropy

    def backup_key(self, key: str, name: str = None) -> str:
        """
        ذخیره‌سازی امن کلید با رمزنگاری
        - name: نام اختیاری برای کلید
        """
        if name is None:
            name = f"key_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # رمزنگاری کلید با Fernet
        backup_key = Fernet.generate_key()
        f = Fernet(backup_key)
        encrypted_key = f.encrypt(key.encode())

        # ذخیره کلید و متادیتا
        backup_data = {
            "encrypted_key": encrypted_key.decode(),
            "backup_key": backup_key.decode(),
            "metadata": self.key_meta
        }

        backup_file = self.backup_dir / f"{name}.json"
        with open(backup_file, 'w') as f:
            json.dump(backup_data, f, indent=4)

        return str(backup_file)

    def restore_key(self, backup_file: str) -> Dict:
        """بازیابی کلید از فایل پشتیبان"""
        backup_file = Path(backup_file)
        if not backup_file.exists():
            raise FileNotFoundError(f"Backup file not found: {backup_file}")

        with open(backup_file) as f:
            backup_data = json.load(f)

        f = Fernet(backup_data["backup_key"].encode())
        decrypted_key = f.decrypt(backup_data["encrypted_key"].encode()).decode()

        return {
            "key": decrypted_key,
            "metadata": backup_data["metadata"]
        }

    def generate_env_file(self, key: str, env_file: str = ".env") -> None:
        """ایجاد فایل .env با کلید تولید شده"""
        env_content = f"""
# Generated at {datetime.now().isoformat()}
SECRET_KEY="{key}"
KEY_STRENGTH_SCORE={self.key_meta['strength_score']}
KEY_GENERATION_METHOD={self.key_meta['method']}
DEBUG=False
        """.strip()

        with open(env_file, 'w') as f:
            f.write(env_content)

def main():
    parser = argparse.ArgumentParser(description="Advanced Secret Key Generator")
    parser.add_argument("--length", type=int, default=32, help="Key length")
    parser.add_argument("--method", choices=["urlsafe", "hex", "base64", "mix"],
                      default="mix", help="Key generation method")
    parser.add_argument("--backup", action="store_true", help="Backup the key")
    parser.add_argument("--name", help="Backup name")
    parser.add_argument("--env", action="store_true", help="Generate .env file")
    
    args = parser.parse_args()

    generator = SecretKeyGenerator(key_length=args.length)
    key = generator.generate_key(method=args.method)

    print(f"\n{'='*50}")
    print(f"Generated Secret Key: {key}")
    print(f"Key Strength Score: {generator.key_meta['strength_score']}%")
    print(f"SHA256: {generator.key_meta['sha256']}")
    print(f"{'='*50}\n")

    if args.backup:
        backup_file = generator.backup_key(key, args.name)
        print(f"Key backed up to: {backup_file}")

    if args.env:
        generator.generate_env_file(key)
        print("Generated .env file with the new key")

if __name__ == "__main__":
    main()
