
SELECT date.date, product.type AS account_type, SUM(balance.balance) AS 'Balance Total' FROM account INNER JOIN product ON account.product_id = product.id INNER JOIN balance ON account.id = balance.account_id INNER JOIN date ON balance.balance_dt_id = date.id INNER JOIN relationship ON account.id = relationship.account_id INNER JOIN client ON relationship.client_id = client.id WHERE client.name = 'Mary Spock' AND date.date = '2023-10-11' AND relationship.relationship_type = 'Primary' GROUP BY date.date, product.type LIMIT 10;