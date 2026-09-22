create database ATMMachine1;
use ATMMachine1;
CREATE TABLE ATMMoney  
(  
ACCONT_NO int(4) primary key, 
PASSWORD INT(8) NOT NULL,  						  
NAME VARCHAR(20) , 
CR_AMT INT Default 0,   								
WITHDRAWL INT DEFAULT 0,  
BALANCE INT DEFAULT 0);  

desc ATMMoney;
select * from ATMMoney;
truncate ATMMoney;

ALTER TABLE ATMMoney
   MODIFY COLUMN BALANCE BIGINT;

DESC ATMMONEY;
