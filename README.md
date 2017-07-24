### Notes for config etc.
####Run på heroku

####Run lokalt

####DB migrate
I term fra /badmin_api/

```
flask db migrate
```
Se rettelser i auto gen migration script

```
flask db upgrade
```

####Drop postgres DB and reload demo db
I postgres console

```
DROP SCHEMA public CASCADE;CREATE SCHEMA public;GRANT ALL ON SCHEMA public TO postgres;GRANT ALL ON SCHEMA public TO public;COMMENT ON SCHEMA public IS 'standard public schema';
```

I python:

```
exec(open('create_demo_db.py', 'r').read())
```

####Environ vars
DATABASE_URL=...
FLASK_APP=badmin_api.py
TOKEN_GEN_SECRET_KEY=...