# Message REST-API
A small message service hosted by a REST-API built with Flask.
## Usage

Install dependencies using `pip`:

```bash
pip install -r requirements.txt
```
Before the service can be started, the database must be created:

```bash
make db
# or
python init_db.py
```

To start the service:

```bash
make start
# or
python run.py
```

If everything goes well, the base address to the service is `http://127.0.0.1:5000`

After `init_db.py` has been run, two users have been added (`henrik, mikaela`). For instance, you should now be able to read all (none initially) unread messages for `henrik` at:
http://127.0.0.1:5000/user/henrik/messages/unread

## API Documentation

The API documentation can be found at `doc/index.html`