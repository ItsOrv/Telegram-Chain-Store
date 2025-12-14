from telethon import events
from src.core.database import SessionLocal
from src.core.models import User, UserRole
from src.bot.common.messages import Messages
from src.config.settings import get_settings
import subprocess
import os
import time
from datetime import datetime
from pathlib import Path
import logging
import shutil
import hashlib
import secrets
from cryptography.fernet import Fernet
import tempfile

logger = logging.getLogger(__name__)

class BackupHandler:
    def __init__(self, client):
        self.client = client
        self.settings = get_settings()
        self.setup_handlers()
        
        # Create secure temporary backup directory
        self.backup_dir = Path(tempfile.mkdtemp(prefix='dbbackup_'))
        os.chmod(self.backup_dir, 0o700)  # Restrict permissions
        
        # Generate encryption key
        self.encryption_key = Fernet.generate_key()
        self.fernet = Fernet(self.encryption_key)
        
    def __del__(self):
        """Cleanup temporary files on destruction"""
        try:
            shutil.rmtree(self.backup_dir, ignore_errors=True)
        except:
            pass

    def setup_handlers(self):
        @self.client.on(events.CallbackQuery(pattern="💾 Get Database"))
        async def handle_backup_request(event):
            """Handle database backup request with security checks"""
            try:
                # Verify user is admin and HEAD_ADMIN
                user_id = event.sender_id
                if str(user_id) != str(self.settings.HEAD_ADMIN_ID):
                    logger.warning(f"Unauthorized backup attempt by user {user_id}")
                    await event.answer(Messages.UNAUTHORIZED, alert=True)
                    return

                with SessionLocal() as db:
                    user = db.query(User).filter(
                        User.telegram_id == user_id,
                        User.role == UserRole.ADMIN,
                        User.status == "ACTIVE"
                    ).first()
                    
                    if not user:
                        logger.warning(f"Unauthorized backup attempt by non-admin {user_id}")
                        await event.answer(Messages.UNAUTHORIZED, alert=True)
                        return

                # Rate limiting
                if not self._check_rate_limit(user_id):
                    await event.answer(Messages.BACKUP_RATE_LIMIT, alert=True)
                    return

                # Send "processing" message
                processing_msg = await event.respond(Messages.BACKUP_PROCESSING)

                # Create backup with encryption
                backup_info = await self.create_secure_backup()
                if not backup_info:
                    await processing_msg.edit(Messages.BACKUP_FAILED)
                    return

                backup_file, checksum = backup_info

                # Send encrypted backup file
                await self.client.send_file(
                    event.chat_id,
                    backup_file,
                    caption=Messages.BACKUP_COMPLETED.format(
                        checksum=checksum,
                        timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    ),
                    force_document=True
                )

                # Send encryption key separately with correct parse mode
                key_message = f"🔑 Backup Decryption Key:\n`{self.encryption_key.decode()}`\n\n⚠️ Store this key securely. It cannot be recovered if lost."
                await self.client.send_message(
                    event.chat_id,
                    key_message,
                    parse_mode='md'  # Using Markdown instead of 'code'
                )

                # Cleanup
                await processing_msg.delete()
                self._secure_cleanup(backup_file)

            except Exception as e:
                logger.error(f"Backup error: {str(e)}", exc_info=True)  # Add stack trace
                await event.respond(Messages.BACKUP_FAILED)

    def _check_rate_limit(self, user_id: int) -> bool:
        """Implement rate limiting for backup requests"""
        cache_key = f"backup_limit_{user_id}"
        current_time = time.time()
        
        # Allow only 1 backup per hour per admin
        if hasattr(self, '_rate_limit_cache'):
            last_backup_time = self._rate_limit_cache.get(cache_key, 0)
            if current_time - last_backup_time < 3600:  # 1 hour
                return False
                
        self._rate_limit_cache = getattr(self, '_rate_limit_cache', {})
        self._rate_limit_cache[cache_key] = current_time
        return True

    def _secure_cleanup(self, file_path: str):
        """Securely delete files by overwriting"""
        try:
            # Overwrite file with random data before deletion
            file_size = os.path.getsize(file_path)
            with open(file_path, 'wb') as f:
                f.write(secrets.token_bytes(file_size))
            os.remove(file_path)
        except:
            pass

    async def create_secure_backup(self) -> tuple:
        """Create encrypted database backup"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_name = f"db_backup_{timestamp}"
            backup_sql = self.backup_dir / f"{backup_name}.sql"
            backup_encrypted = self.backup_dir / f"{backup_name}.enc"

            # Create MySQL dump with secure options
            cmd = [
                'mysqldump',
                '--single-transaction',  # Consistent backup
                '--skip-extended-insert',  # One INSERT per row
                '--skip-comments',
                '--no-autocommit',
                '--quick',
                '-h', self.settings.DB_HOST,
                '-P', str(self.settings.DB_PORT),
                '-u', self.settings.DB_USER,
                self.settings.DB_NAME,
                f'--result-file={backup_sql}'
            ]

            # Execute backup command
            process = subprocess.Popen(
                cmd, 
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            stdout, stderr = process.communicate()

            if process.returncode != 0:
                logger.error(f"Backup failed: {stderr.decode()}")
                return None

            # Calculate checksum of unencrypted file
            with open(backup_sql, 'rb') as f:
                file_hash = hashlib.sha256(f.read()).hexdigest()

            # Encrypt the backup
            with open(backup_sql, 'rb') as f:
                encrypted_data = self.fernet.encrypt(f.read())
            
            with open(backup_encrypted, 'wb') as f:
                f.write(encrypted_data)

            # Secure delete the unencrypted SQL file
            self._secure_cleanup(str(backup_sql))

            return str(backup_encrypted), file_hash

        except Exception as e:
            logger.error(f"Error creating secure backup: {str(e)}")
            return None
