from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import warnings


def save_to_database(df, table_name, db_string):
    # Create the engine
    engine = create_engine(db_string)

    # Suppress the warning
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        df.to_sql(table_name, engine, if_exists='replace')

    # Create a Session
    Session = sessionmaker(bind=engine)
    session = Session()

    # Write the DataFrame to a table in the SQL database
    df.to_sql(table_name, engine, if_exists='replace')

    # Commit the transaction
    session.commit()

    # Close the session
    session.close()
