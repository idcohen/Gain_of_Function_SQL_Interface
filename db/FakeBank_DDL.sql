/* Fake Bank DDL */

/*
drop table NAICS;
drop table relationship ;
drop table balance;
drop table account;
drop table product;
drop table client;
drop table employer;
drop table HH;
drop table address;
drop table banker;
drop table Transactions;
drop table date;

*/
create table NAICS
(
    NAICS_CD integer Primary key,
    DESCRIPTION varchar(128)
);

    create table product
    (
        ID integer primary key,
        Type varchar(128) not null,
        Name varchar(128) not null,
        Start_Dt date not null,
        End_Dt date not null,
        Is_Current integer not null
    );

    create table banker
    (
        ID integer primary key,
        Name varchar(128) not null,
        FirstName  varchar(128) not null,
        LastName varchar(128) not null,
		Start_Dt date not null,
		End_Dt date not null,
        Is_Current integer not null
    );

    create table address
    (
        ID integer primary key,
        Address varchar(128),
        City varchar(128),
        State varchar(128),
        Zip varchar(128),
        Start_Dt date not null,
        End_Dt date not null,
        Is_Current integer not null
    );
    
       create table account
    (
        ID integer primary key,
        acct_nbr varchar(128) not null,
        Product_ID integer not null,
        Banker_ID integer not null,
        Status varchar(128) not null,
        Open_Dt date not null,
        Close_Dt date,
		Start_Dt date not null,
		End_Dt date not null,
        Is_Current integer not null,
        FOREIGN KEY(Product_ID) REFERENCES Product(ID),
        FOREIGN KEY(Banker_ID) REFERENCES banker(ID)   
    );

    create table  HH
    (
        ID integer PRIMARY KEY,
        Person_Org varchar(128) not null,
        Name varchar(128) not null,
        FirstName varchar(128) ,
        LastName varchar(128) ,
        NAICS_CD integer not null,
        Address_ID integer not null,
        Banker_ID integer not null,
        Start_Dt date not null,
        End_Dt date not null,
        Is_Current integer not null,
        FOREIGN KEY(Address_ID) REFERENCES address(ID),
        FOREIGN KEY(Banker_ID) REFERENCES banker(ID),
        FOREIGN KEY(NAICS_CD) REFERENCES NAICS(NAICS_CD)
        
    );
   
    create table employer
    (
        ID integer primary key,
        Name varchar(128),
        Address_ID integer not null,
        Client_ID integer,
        Industry varchar(128),
        NAICS_CD integer,
        Start_Dt date not null,
        End_Dt date not null,
        Is_Current integer not null,
        FOREIGN KEY(Address_ID) REFERENCES address(ID),
        Foreign key(NAICS_CD) References NAICS(NAICS_CD) 
    );

   
   CREATE TABLE client
    (
        ID integer PRIMARY KEY,
        Client_ID integer not null,
        HH_ID integer not null,
        Person_Org varchar(128) not null,
        Name varchar(128)not null,
        FirstName varchar(128) ,
        LastName varchar(128) ,
        NAICS_CD integer,
        SSN varchar(128),
        Address_ID integer not null,
        Banker_ID integer not null,
        Employer_ID integer not null,
        Title varchar(128),
        New_Client_Dt date not null,
        Start_Dt date not null,
        End_Dt date not null,
        Is_Current integer not null,
        FOREIGN KEY(Address_ID) REFERENCES address(ID),
        FOREIGN KEY(Banker_ID) REFERENCES banker(ID),
        FOREIGN KEY(HH_ID) REFERENCES HH(ID),
        FOREIGN KEY(Employer_ID) REFERENCES employer(ID),
        Foreign key(NAICS_CD) References NAICS(NAICS_CD) 
    
    );

   
    create table relationship
    (
        ID integer primary key,
        Account_ID integer not null,
        Client_ID integer not null,
        Relationship_Type varchar(128) not null,
   		Start_Dt date not null,
		End_Dt date not null,
        Is_Current integer not null,
        FOREIGN KEY(Account_ID) REFERENCES account(ID),
        FOREIGN KEY(Client_ID) REFERENCES client(ID)
    );
        

       create table date
    (
        ID integer primary key,
        Date date not null,
        Julian_Dt integer not null,
        Month integer not null,
        Day integer not null,
        Year integer not null,
        Quarter integer not null
    );

   
    create table  balance
    (
        ID integer primary key,
        Account_ID integer not null,
        Balance real not null,
        Balance_Dt_Id integer not null,
        FOREIGN KEY(Account_ID) REFERENCES account(ID),
        FOREIGN KEY(Balance_Dt_Id) REFERENCES date(ID)
    );

        
   create table Transactions
   (
		IDX integer primary key,
		Date_ID integer not null,
		Account_Number varchar(128) not null,
		Transaction_Type varchar(128) not null,
		Transfer_Acct_Nbr varchar(128),
		ACH_Acct_Nbr varchar(128),
		ACH_Rtg_Nbr varchar(128),
		Transaction_Purpose varchar(128),
		Transaction_Direction varchar(128),
		Transaction_Amount float,
		Balance float,
		Transaction_Description varchar(256)
	);
