-- Database setup for Telegram Chain Store
-- Warning: This will reset the database and user!
-- Note: This script must be run with sudo mysql

-- Create database with proper encoding
DROP DATABASE IF EXISTS chainstore_db;
CREATE DATABASE chainstore_db
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;

-- Create user with password authentication (for both local and remote access)
DROP USER IF EXISTS 'chainstore_user'@'localhost';
DROP USER IF EXISTS 'chainstore_user'@'%';
CREATE USER 'chainstore_user'@'localhost' IDENTIFIED BY 'chainstore123';
CREATE USER 'chainstore_user'@'%' IDENTIFIED BY 'chainstore123';

-- Grant privileges to the user
GRANT ALL PRIVILEGES ON chainstore_db.* TO 'chainstore_user'@'localhost';
GRANT ALL PRIVILEGES ON chainstore_db.* TO 'chainstore_user'@'%';

-- Apply changes
FLUSH PRIVILEGES;
