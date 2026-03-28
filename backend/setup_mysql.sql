-- Serenity Mental Health Application - MySQL Setup Script
-- Run this script to create the database and user

-- Create database
CREATE DATABASE IF NOT EXISTS serenity_db 
CHARACTER SET utf8mb4 
COLLATE utf8mb4_unicode_ci;

-- Switch to database
USE serenity_db;

-- Create application user (optional, for production)
CREATE USER IF NOT EXISTS 'serenity_user'@'localhost' IDENTIFIED BY 'serenity_password';

-- Grant privileges
GRANT ALL PRIVILEGES ON serenity_db.* TO 'serenity_user'@'localhost';

-- Apply privileges
FLUSH PRIVILEGES;

-- Show databases
SELECT 'Database created successfully!' AS status;
SHOW DATABASES LIKE 'serenity%';

-- Note: Tables will be automatically created by SQLAlchemy when you start the application
-- The application will create: users, conversations, messages tables with proper indexes
