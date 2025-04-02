-- اسکریپت اولیه‌ی ایجاد دیتابیس (می‌توان در پوشه docs یا database قرار داد)


-- Database setup for Telegram Chain Store
-- Warning: This will reset the database and user!

-- Drop existing database and user if they exist
DROP DATABASE IF EXISTS chainstore_db;
DROP USER IF EXISTS 'chainstore_user'@'localhost';

-- Create database with proper character set for multilingual support
CREATE DATABASE chainstore_db 
CHARACTER SET utf8mb4 
COLLATE utf8mb4_unicode_ci;

-- Create user with strong password and native password authentication
CREATE USER 'chainstore_user'@'localhost' 
IDENTIFIED WITH mysql_native_password BY 'V24aDAsda!!@xAKLAsSsx';

-- Grant only necessary privileges
GRANT SELECT, INSERT, UPDATE, DELETE, CREATE, DROP, REFERENCES, INDEX, ALTER, 
      EXECUTE, CREATE VIEW, SHOW VIEW, CREATE ROUTINE, ALTER ROUTINE 
ON chainstore_db.* TO 'chainstore_user'@'localhost';

-- Apply changes
FLUSH PRIVILEGES;

-- Security note: Make sure to change the password in production
-- and restrict user permissions as needed
