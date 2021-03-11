import sqlite3


conn = sqlite3.connect('db.sqlite3')
c = conn.cursor()
c.execute("DELETE from user_task;")
c.execute("DELETE from user_task_command;")
c.execute("DELETE from user_task_command_args;")
c.execute("DELETE from event_log;")

conn.commit()
conn.close()
