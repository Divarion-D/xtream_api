## How to use
### Main public methods
- `get_sql()` returns SQL query string which will be executed
- `get_params()` returns a tuple of parameters for a query
- `get_result()` returns query's result
- `get_count()` returns result's rows count
- `get_error()` returns `True` if an error is had
- `get_error_message()` returns an error message if an error is had
- `set_error(message)` sets `_error` to `True` and `_error_message`
- `get_first()` returns the first item of results
- `get_last()` returns the last item of results
- `reset()` resets state to default values
- `all()` executes SQL query and returns all rows of result (`fetchall()`)
- `one()` executes SQL query and returns the first row of result (`fetchone()`)
- `column(col)` executes SQL query and returns the needed column of result by its index or name, `col` is `0` by default
- `pluck(key, col)` executes SQL query and returns a list of tuples/dicts (the key (usually ID) and the needed column of result) by its indexes or names, `key` is `0` and `col` is `1` by default
- `go()` this method is for non `SELECT` queries. it executes SQL query and returns nothing (but returns the last inserted row ID for `INSERT` method)
- `exists()` returns `True` if SQL query has a row and `False` if it hasn't
- `count()` prepares a query with SQL `COUNT(*)` function and executes it
- `query(sql, params, fetch_type, col_index)` executes prepared `sql` with `params`, it can be used for custom queries
- 'SQL' methods are presented in [Usage section](#usage-examples)

### Import the module and init `QueryBuilder` with `Database()`
```python
from simple_query_builder import *

# if you want to get results as a list of dictionaries (by default since 0.3.5)
qb = QueryBuilder(DataBase(), 'my_db.db') # result_dict=True, print_errors=False

# or if you want to get results as a list of tuples (since 0.3.5)
qb = QueryBuilder(DataBase(), 'my_db.db', result_dict=False)

# for printing errors into terminal (since 0.3.5)
qb = QueryBuilder(DataBase(), 'my_db.db', print_errors=True)
```
### Usage examples
- Select all rows from a table
```python
results = qb.select('users').all()
```
```sql
SELECT * FROM `users`;
```
- Select a row with a condition
```python
results = qb.select('users').where([['id', '=', 10]]).one()
# or since 0.3.4
results = qb.select('users').where([['id', 10]]).one()
```
```sql
SELECT * FROM `users` WHERE `id` = 10;
```
- Select rows with two conditions
```python
results = qb.select('users').where([['id', '>', 1], 'and', ['group_id', '=', 2]]).all()
# or since 0.3.4
results = qb.select('users').where([['id', '>', 1], 'and', ['group_id', 2]]).all()
```
```sql
SELECT * FROM `users` WHERE (`id` > 1) AND (`group_id` = 2);
```
- Select a row with a `LIKE` and `NOT LIKE` condition
```python
results = qb.select('users').like(['name', '%John%']).all()
# or
results = qb.select('users').where([['name', 'LIKE', '%John%']]).all()
# or since 0.3.5
results = qb.select('users').like('name', '%John%').all()
```
```sql
SELECT * FROM `users` WHERE (`name` LIKE '%John%');
```
```python
results = qb.select('users').not_like(['name', '%John%']).all()
# or
results = qb.select('users').where([['name', 'NOT LIKE', '%John%']]).all()
# or since 0.3.5
results = qb.select('users').not_like('name', '%John%').all()
```
```sql
SELECT * FROM `users` WHERE (`name` NOT LIKE '%John%');
```
- Select a row with a `IS NULL` and `IS NOT NULL` condition (since 0.3.5)
```python
results = qb.select('users').is_null('phone').all()
# or
results = qb.select('users').where([['phone', 'is null']]).all()
```
```sql
SELECT * FROM `users` WHERE (`phone` IS NULL);
```
```python
results = qb.select('customers').is_not_null('address').all()
# or
results = qb.select('customers').not_null('address').all()
# or
results = qb.select('customers').where([['address', 'is not null']]).all()
```
```sql
SELECT * FROM `customers` WHERE (`address` IS NOT NULL);
```
- Select rows with `OFFSET` and `LIMIT`
```python
results = qb.select('posts')\
    .where([['user_id', '=', 3]])\
    .offset(14)\
    .limit(7)\
    .all()
# or since 0.3.4
results = qb.select('posts')\
    .where([['user_id', 3]])\
    .offset(14)\
    .limit(7)\
    .all()
```
```sql
SELECT * FROM `posts` WHERE (`user_id` = 3) OFFSET 14 LIMIT 7;
```
- Select custom fields with additional SQL
1. `COUNT()`
```python
results = qb.select('users', {'counter': 'COUNT(*)'}).one()
# or
results = qb.count('users').one()
```
```sql
SELECT COUNT(*) AS `counter` FROM `users`;
```
2. `ORDER BY`
```python
results = qb.select({'b': 'branches'}, ['b.id', 'b.name'])\
    .where([['b.id', '>', 1], 'and', ['b.parent_id', 1]])\
    .order_by('b.id', 'desc')\
    .all()
# or since 0.3.4
results = qb.select({'b': 'branches'}, ['b.id', 'b.name'])\
    .where([['b.id', '>', 1], 'and', ['b.parent_id', 1]])\
    .order_by('b.id desc')\
    .all()
```
```sql
SELECT `b`.`id`, `b`.`name` FROM `branches` AS `b`
WHERE (`b`.`id` > 1) AND (`b`.`parent_id` = 1)
ORDER BY `b`.`id` DESC;
``` 
3. `GROUP BY` and `HAVING`
```python
results = qb.select('posts', ['id', 'category', 'title'])\
    .where([['views', '>=', 1000]])\
    .group_by('category')\
    .all()
```
```sql
SELECT `id`, `category`, `title` FROM `posts`
WHERE (`views` >= 1000) GROUP BY `category`;
```
```python
groups = qb.select('orders', {'month_num': 'MONTH(`created_at`)', 'total': 'SUM(`total`)'})\
    .where([['YEAR(`created_at`)', '=', 2020]])\
    .group_by('month_num')\
    .having([['total', '=', 20000]])\
    .all()
# or since 0.3.4
groups = qb.select('orders', {'month_num': 'MONTH(`created_at`)', 'total': 'SUM(`total`)'})\
    .where([['YEAR(`created_at`)', 2020]])\
    .group_by('month_num')\
    .having([['total', 20000]])\
    .all()
```
```sql
SELECT MONTH(`created_at`) AS `month_num`, SUM(`total`) AS `total`
FROM `orders` WHERE (YEAR(`created_at`) = 2020)
GROUP BY `month_num` HAVING (`total` = 20000);
```
4. `JOIN`. Supports `INNER`, `LEFT OUTER`, `RIGHT OUTER`, `FULL OUTER` and `CROSS` joins (`INNER` is by default)
```python
results = qb.select({'u': 'users'}, [
        'u.id',
        'u.email',
        'u.username',
        {'perms': 'groups.permissions'}
    ])\
    .join('groups', ['u.group_id', 'groups.id'])\
    .limit(5)\
    .all()
```
```sql
SELECT `u`.`id`, `u`.`email`, `u`.`username`, `groups`.`permissions` AS `perms`
FROM `users` AS `u`
INNER JOIN `groups` ON `u`.`group_id` = `groups`.`id`
LIMIT 5;
```
```python
results = qb.select({'cp': 'cabs_printers'}, [
        'cp.id',
        'cp.cab_id',
        {'cab_name': 'cb.name'},
        'cp.printer_id',
        {'printer_name': 'p.name'},
        {'cartridge_type': 'c.name'},
        'cp.comment'
    ])\
    .join({'cb': 'cabs'}, ['cp.cab_id', 'cb.id'])\
    .join({'p': 'printer_models'}, ['cp.printer_id', 'p.id'])\
    .join({'c': 'cartridge_types'}, 'p.cartridge_id=c.id')\
    .where([['cp.cab_id', 'in', [11, 12, 13]], 'or', ['cp.cab_id', '=', 5], 'and', ['p.id', '>', 'c.id']])\
    .all()
```
```sql
SELECT `cp`.`id`, `cp`.`cab_id`, `cb`.`name` AS `cab_name`, `cp`.`printer_id`,
       `p`.`name` AS `printer_name`, `c`.`name` AS `cartridge_type`, `cp`.`comment`
FROM `cabs_printers` AS `cp`
INNER JOIN `cabs` AS `cb` ON `cp`.`cab_id` = `cb`.`id`
INNER JOIN `printer_models` AS `p` ON `cp`.`printer_id` = `p`.`id`
INNER JOIN `cartridge_types` AS `c` ON p.cartridge_id=c.id
WHERE (`cp`.`cab_id` IN (11, 12, 13)) OR (`cp`.`cab_id` = 5) AND (`p`.`id` > `c`.`id`);
```
```python
# since 0.3.4
results = qb.select({'cp': 'cabs_printers'}, [
        'cp.id',
        'cp.cab_id',
        {'cab_name': 'cb.name'},
        'cp.printer_id',
        {'cartridge_id': 'c.id'},
        {'printer_name': 'p.name'},
        {'cartridge_type': 'c.name'},
        'cp.comment'
    ])\
    .join({'cb': 'cabs'}, ['cp.cab_id', 'cb.id'])\
    .join({'p': 'printer_models'}, ['cp.printer_id', 'p.id'])\
    .join({'c': 'cartridge_types'}, ['p.cartridge_id', 'c.id'])\
    .group_by(['cp.printer_id', 'cartridge_id'])\
    .order_by(['cp.cab_id', 'cp.printer_id desc'])\
    .all()
```
```sql
SELECT `cp`.`id`, `cp`.`cab_id`, `cb`.`name` AS `cab_name`, `cp`.`printer_id`, `c`.`id` AS `cartridge_id`,
    `p`.`name` AS `printer_name`, `c`.`name` AS `cartridge_type`, `cp`.`comment`
FROM `cabs_printers` AS `cp`
INNER JOIN `cabs` AS `cb` ON `cp`.`cab_id` = `cb`.`id`
INNER JOIN `printer_models` AS `p` ON `cp`.`printer_id` = `p`.`id`
INNER JOIN `cartridge_types` AS `c` ON `p`.`cartridge_id` = `c`.`id`
GROUP BY `cp`.`printer_id`, `cartridge_id`
ORDER BY `cp`.`cab_id` ASC, `cp`.`printer_id` DESC;
```
- Insert a row
```python
new_id = qb.insert('groups', {
    'name': 'Moderator',
    'permissions': 'moderator'
}).go()
```
```sql
INSERT INTO `groups` (`name`, `permissions`) VALUES ('Moderator', 'moderator');
```
- Insert many rows
```python
qb.insert('groups', [['name', 'role'],
    ['Moderator', 'moderator'],
    ['Moderator2', 'moderator'],
    ['User', 'user'],
    ['User2', 'user']
]).go()
```
```sql
INSERT INTO `groups` (`name`, `role`)
VALUES ('Moderator', 'moderator'),
       ('Moderator2', 'moderator'),
       ('User', 'user'),
       ('User2', 'user');
```
- Update a row
```python
qb.update('users', {
        'username': 'John Doe',
        'status': 'new status'
    })\
    .where([['id', '=', 7]])\
    .limit()\
    .go()
# or since 0.3.4
qb.update('users', {
        'username': 'John Doe',
        'status': 'new status'
    })\
    .where([['id', 7]])\
    .limit()\
    .go()
```
```sql
UPDATE `users` SET `username` = 'John Doe', `status` = 'new status'
WHERE `id` = 7 LIMIT 1;
```
- Update rows
```python
qb.update('posts', {'status': 'published'})\
    .where([['YEAR(`updated_at`)', '>', 2020]])\
    .go()
```
```sql
UPDATE `posts` SET `status` = 'published'
WHERE (YEAR(`updated_at`) > 2020);
```
- Delete a row
```python
qb.delete('users')\
    .where([['name', '=', 'John']])\
    .limit()\
    .go()
# or since 0.3.4
qb.delete('users')\
    .where([['name', 'John']])\
    .limit()\
    .go()
```
```sql
DELETE FROM `users` WHERE `name` = 'John' LIMIT 1;
```
- Delete rows
```python
qb.delete('comments')\
    .where([['user_id', '=', 10]])\
    .go()
# or since 0.3.4
qb.delete('comments')\
    .where([['user_id', 10]])\
    .go()
```
```sql
DELETE FROM `comments` WHERE `user_id` = 10;
```
- Truncate a table

This method will be moved to another class
```python
qb.truncate('users').go()
```
```sql
TRUNCATE TABLE `users`;
```
- Drop a table

This method will be moved to another class
```python
qb.drop('temporary').go()
```
```sql
DROP TABLE IF EXISTS `temporary`;
```