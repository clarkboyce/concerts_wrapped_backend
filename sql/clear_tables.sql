-- Disable foreign key checks
SET FOREIGN_KEY_CHECKS = 0;

-- Delete from both tables
TRUNCATE TABLE user_concert;
TRUNCATE TABLE concerts;

-- Re-enable foreign key checks
SET FOREIGN_KEY_CHECKS = 1; 