-- Initialize MySQL for Telegram Chain Store
-- Run as: sudo mysql < mysql_init.sql

-- Basic database initialization
ALTER USER 'root'@'localhost' IDENTIFIED WITH auth_socket;
