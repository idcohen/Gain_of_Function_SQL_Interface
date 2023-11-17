

SELECT
 account.acct_nbr,
 balance.balance,
 product.type,
 date.date 

FROM
 account 

INNER JOIN
 product 
ON
 account.product_id = product.id 

INNER JOIN
 balance 
ON
 account.id = balance.account_id 

INNER JOIN
 date 
ON
 balance.balance_dt_id = date.id 

INNER JOIN
 relationship 
ON
 account.id = relationship.account_id 

INNER JOIN
 client 
ON
 relationship.client_id = client.id 

WHERE
 client.name = 'Mary Spock' 

AND
 date.date = '2023-10-10' 

AND
 relationship.relationship_type = 'Primary' 
LIMIT 10;