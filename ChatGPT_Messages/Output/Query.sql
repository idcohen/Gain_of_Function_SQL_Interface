
SELECT
 account.acct_nbr,
 balance.balance 
FROM
 account 
INNER JOIN
 balance 
ON
 account.id = balance.account_id 
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
 account.status = 'Open';