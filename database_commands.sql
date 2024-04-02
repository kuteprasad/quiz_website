-- CREATE TABLE accounts (
      -- type text, 
--   user_id SERIAL PRIMARY KEY, 
--   username VARCHAR (50) UNIQUE NOT NULL, 
--   password VARCHAR (50) NOT NULL, 
--   email VARCHAR (255) UNIQUE NOT NULL );

-- insert into accounts (username, password, email) Values ('prasad', '1234', 'prasad@gmail.com');

-- select * from accounts;

-- create table test_number (
-- 	subject VARCHAR	(50) NOT NULL, 
-- 	test_no int not null,
-- 	test_id int PRIMARY KEY not null, 
--  total_questions int not null,
-- );

-- insert into test_number ( subject, test_no, test_id) 
-- values ( 'Aptitude', 1, 466);

-- select * from test_number;


-- CREATE TABLE test_data (
--   test_id int not null references test_number(test_id), 
--   question_no int not null, 
--   question text NOT NULL, 
--   option_1 VARCHAR(100) NOT NULL,
-- 	option_2 VARCHAR(100) NOT NULL, 
-- 	option_3 VARCHAR(100) NOT NULL, 
-- 	option_4 VARCHAR(100) NOT NULL,
-- 	correct_option VARCHAR(100) NOT NULL,
--  PRIMARY KEY (test_id, question_no)
-- 	 );

-- insert into test_data (test_id, question_no, question, option_1, option_2, option_3, option_4, correct_option)
-- values (244, 2, 'What is capital of Tamil Nadu?', 'Mumbai', 'New Delhi', 'Pune', 'Chennai', 'Chennai');
 
-- select * from test_data;
 
-- CREATE TABLE users_data (
--     data_id SERIAL PRIMARY KEY,
--     username VARCHAR(50) REFERENCES accounts(username) NOT NULL,
--     test_id INT REFERENCES test_number(test_id) NOT NULL,
--     score INT NOT NULL, 
--     total_score INT NOT NULL,
--     test_duration INT, 
--     date_stamp DATE, 
--     time_stamp TIME
-- );

