commands = ['''create table users (
                                id SERIAL PRIMARY KEY,
                                name VARCHAR(100) NOT NULL,
                                registry_timestamp INT NOT NULL);''',

            '''create table ml_model_actions (
                        id SERIAL PRIMARY KEY,
                        user_id SERIAL,
                        timestamp INT NOT NULL,
                        subject VARCHAR(100) NOT NULL,
                        object VARCHAR(100) NOT NULL,
                        predicate VARCHAR(100) NOT NULL,
                        probability FLOAT);''']
