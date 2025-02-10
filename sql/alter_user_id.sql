-- Disable foreign key checks
SET FOREIGN_KEY_CHECKS = 0;

-- Modify the user_id column in user_concert table
ALTER TABLE user_concert MODIFY COLUMN user_id VARCHAR(255) NOT NULL;

-- Re-enable foreign key checks
SET FOREIGN_KEY_CHECKS = 1; 